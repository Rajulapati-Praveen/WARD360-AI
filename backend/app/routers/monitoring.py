from fastapi import APIRouter, Depends, Header, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.orm import Session

from .. import models, services
from ..config import settings
from ..database import get_db
from ..security import allowed_patient_ids, audit, get_current_user, get_patient_or_403
from ..util import aware, now_utc
from ..ws import manager
from ml import anomaly

router = APIRouter(prefix="/api", tags=["monitoring"])


class IngestIn(BaseModel):
    device_id: int
    heart_rate: float | None = None
    spo2: float | None = None
    temperature: float | None = None
    resp_rate: float | None = None
    activity: str = Field(default="resting", max_length=20)
    accel_magnitude: float | None = Field(default=None, ge=0, le=20)
    quality: str = Field(default="good", max_length=10)
    battery: int | None = Field(default=None, ge=0, le=100)


class EmergencyIn(BaseModel):
    message: str = Field(default="Help requested", max_length=300)
    via: str = Field(default="button", max_length=20)


@router.post("/ingest")
async def ingest(body: IngestIn, x_device_key: str | None = Header(default=None), db: Session = Depends(get_db)):
    """Device endpoint (used by iot/simulator.py or an ESP32). Authenticated with X-Device-Key."""
    if x_device_key != settings.DEVICE_API_KEY:
        raise HTTPException(401, "Invalid device key")
    dev = db.get(models.Device, body.device_id)
    if not dev:
        raise HTTPException(404, "Unknown device")
    patient = db.get(models.Patient, dev.patient_id)
    events = services.process_reading(db, patient, dev, body.model_dump())
    await manager.broadcast(events)
    last = events[-1]
    return {"stored": True, "reading_id": last["reading"]["id"], "quality": last["reading"]["quality"],
            "risk": last["risk"]["level"], "anomaly": last["anomaly"]["is_anomaly"], "issues": last["issues"]}


@router.get("/patients/{pid}/vitals")
def vitals(pid: int, hours: float = 1, limit: int = 500, db: Session = Depends(get_db), user=Depends(get_current_user)):
    get_patient_or_403(db, user, pid)
    from datetime import timedelta
    since = now_utc() - timedelta(hours=min(hours, 168))
    rows = db.scalars(select(models.VitalReading).where(models.VitalReading.patient_id == pid, models.VitalReading.ts >= since)
                      .order_by(models.VitalReading.id.desc()).limit(min(limit, 2000))).all()
    return [services.reading_dict(r) for r in reversed(rows)]


@router.get("/patients/{pid}/live")
def live(pid: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    p = get_patient_or_403(db, user, pid)
    rows = services.series_for(db, pid, 60)
    last = rows[-1] if rows else None
    rk = db.scalar(select(models.RiskAssessment).where(models.RiskAssessment.patient_id == pid).order_by(models.RiskAssessment.id.desc()))
    an = db.scalar(select(models.AnomalyEvent).where(models.AnomalyEvent.patient_id == pid).order_by(models.AnomalyEvent.id.desc()))
    dev = db.scalar(select(models.Device).where(models.Device.patient_id == pid))
    alerts = db.scalars(select(models.Alert).where(models.Alert.patient_id == pid).order_by(models.Alert.id.desc()).limit(5)).all()
    # recompute contributions for the explainable panel
    contributions, confidence = [], None
    if rows:
        from ml import risk
        assessed = risk.assess([services.reading_dict(r) for r in rows[-5:]], services.get_baseline(p), anomaly.DEFAULT_SD)
        contributions, confidence = assessed["contributions"], assessed["confidence"]
    return {"patient": {"id": p.id, "name": p.name, "age": p.age, "baseline": services.get_baseline(p)},
            "reading": services.reading_dict(last) if last else None,
            "series": [services.reading_dict(r) for r in rows],
            "risk": services.risk_dict(rk) if rk else None, "contributions": contributions, "confidence": confidence,
            "anomaly": services.anomaly_dict(an) if an else None,
            "device": services.device_dict(dev) if dev else None,
            "recent_alerts": [services.alert_dict(a) for a in alerts]}


@router.get("/patients/{pid}/analysis")
def analysis(pid: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    p = get_patient_or_403(db, user, pid)
    rows = services.series_for(db, pid, 120)
    trends = services.compute_trends(rows, p) if rows else {}
    anomalies = db.scalars(select(models.AnomalyEvent).where(models.AnomalyEvent.patient_id == pid)
                           .order_by(models.AnomalyEvent.id.desc()).limit(25)).all()
    return {"trends": trends, "anomalies": [services.anomaly_dict(a) for a in anomalies],
            "labels": anomaly.LABELS, "units": anomaly.UNITS,
            "note": "Anomaly 'model_score' is an Isolation Forest score, not a clinical probability. Forecasts are experimental."}


@router.get("/patients/{pid}/risk")
def risk_history(pid: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    get_patient_or_403(db, user, pid)
    rows = db.scalars(select(models.RiskAssessment).where(models.RiskAssessment.patient_id == pid)
                      .order_by(models.RiskAssessment.id.desc()).limit(60)).all()
    return [services.risk_dict(r) for r in rows]


@router.post("/patients/{pid}/emergency", status_code=201)
async def emergency(pid: int, body: EmergencyIn, db: Session = Depends(get_db), user=Depends(get_current_user)):
    """Direct emergency request. Does NOT depend on any AI component."""
    p = get_patient_or_403(db, user, pid)
    a = models.Alert(patient_id=pid, level="critical", source="manual", status="open", created_at=now_utc(),
                     message=f"EMERGENCY request for {p.name} via {body.via}: {body.message}")
    db.add(a)
    db.commit()
    db.refresh(a)
    services.notify(db, a, "new")
    audit(db, user.id, "emergency_request", f"patient:{pid}")
    ev = [{"type": "alert", "patient_id": pid, "alert": services.alert_dict(a)}]
    await manager.broadcast(ev)
    return services.alert_dict(a)


@router.get("/devices")
def devices(db: Session = Depends(get_db), user=Depends(get_current_user)):
    ids = allowed_patient_ids(db, user)
    q = select(models.Device, models.Patient.name).join(models.Patient, models.Patient.id == models.Device.patient_id)
    if ids is not None:
        q = q.where(models.Device.patient_id.in_(ids))
    return [{**services.device_dict(d), "patient_name": n} for d, n in db.execute(q)]
