import json

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.orm import Session

from .. import models, services
from ..database import get_db
from ..security import allowed_patient_ids, audit, get_current_user, get_patient_or_403, require_roles
from .auth import user_dict

router = APIRouter(prefix="/api", tags=["patients"])


class PatientIn(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    age: int = Field(ge=0, le=120)
    gender: str = Field(default="unspecified", max_length=20)
    notes: str = Field(default="", max_length=1000)
    baseline: dict | None = None


class AssignIn(BaseModel):
    user_id: int


def clean_baseline(b):
    out = dict(services.DEFAULT_BASELINE)
    for k, (lo, hi) in services.RANGES.items():
        if b and k in b and lo <= float(b[k]) <= hi:
            out[k] = float(b[k])
    return out


def summary(db, p):
    last = db.scalar(select(models.VitalReading).where(models.VitalReading.patient_id == p.id).order_by(models.VitalReading.id.desc()))
    rk = db.scalar(select(models.RiskAssessment).where(models.RiskAssessment.patient_id == p.id).order_by(models.RiskAssessment.id.desc()))
    dev = db.scalar(select(models.Device).where(models.Device.patient_id == p.id))
    open_alerts = db.scalars(select(models.Alert).where(models.Alert.patient_id == p.id, models.Alert.status.in_(["open", "escalated"]))).all()
    return {"id": p.id, "name": p.name, "age": p.age, "gender": p.gender, "notes": p.notes,
            "baseline": services.get_baseline(p), "is_synthetic": p.is_synthetic,
            "latest": services.reading_dict(last) if last else None,
            "risk": services.risk_dict(rk) if rk else None,
            "device": services.device_dict(dev) if dev else None,
            "open_alerts": len(open_alerts),
            "has_critical": any(a.level == "critical" for a in open_alerts)}


@router.get("/patients")
def list_patients(db: Session = Depends(get_db), user=Depends(get_current_user)):
    ids = allowed_patient_ids(db, user)
    q = select(models.Patient).order_by(models.Patient.id)
    if ids is not None:
        q = q.where(models.Patient.id.in_(ids))
    return [summary(db, p) for p in db.scalars(q)]


@router.post("/patients", status_code=201)
def create_patient(body: PatientIn, db: Session = Depends(get_db), user=Depends(require_roles("admin"))):
    p = models.Patient(name=body.name, age=body.age, gender=body.gender, notes=body.notes,
                       baseline_json=json.dumps(clean_baseline(body.baseline)))
    db.add(p)
    db.flush()
    db.add(models.Device(patient_id=p.id, name=f"SimBand-{p.id}", kind="simulated"))
    db.commit()
    audit(db, user.id, "patient_created", f"patient:{p.id}")
    return summary(db, p)


@router.get("/patients/{pid}")
def get_patient(pid: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    p = get_patient_or_403(db, user, pid)
    audit(db, user.id, "patient_viewed", f"patient:{pid}")
    team = db.scalars(select(models.User).join(models.CaregiverAssignment, models.CaregiverAssignment.user_id == models.User.id)
                      .where(models.CaregiverAssignment.patient_id == pid)).all()
    devices = db.scalars(select(models.Device).where(models.Device.patient_id == pid)).all()
    return {**summary(db, p), "team": [user_dict(u) for u in team], "devices": [services.device_dict(d) for d in devices]}


@router.put("/patients/{pid}")
def update_patient(pid: int, body: PatientIn, db: Session = Depends(get_db), user=Depends(require_roles("admin"))):
    p = get_patient_or_403(db, user, pid)
    p.name, p.age, p.gender, p.notes = body.name, body.age, body.gender, body.notes
    if body.baseline:
        p.baseline_json = json.dumps(clean_baseline(body.baseline))
    db.commit()
    audit(db, user.id, "patient_updated", f"patient:{pid}")
    return summary(db, p)


@router.post("/patients/{pid}/assign")
def assign(pid: int, body: AssignIn, db: Session = Depends(get_db), user=Depends(require_roles("admin"))):
    get_patient_or_403(db, user, pid)
    target = db.get(models.User, body.user_id)
    if not target or target.role == "admin":
        raise HTTPException(422, "Choose a caregiver or doctor account")
    exists = db.scalar(select(models.CaregiverAssignment).where(models.CaregiverAssignment.user_id == body.user_id,
                                                                models.CaregiverAssignment.patient_id == pid))
    if not exists:
        db.add(models.CaregiverAssignment(user_id=body.user_id, patient_id=pid))
        db.commit()
        audit(db, user.id, "assignment_added", f"patient:{pid},user:{body.user_id}")
    return {"ok": True}


@router.delete("/patients/{pid}/assign/{uid}")
def unassign(pid: int, uid: int, db: Session = Depends(get_db), user=Depends(require_roles("admin"))):
    row = db.scalar(select(models.CaregiverAssignment).where(models.CaregiverAssignment.user_id == uid,
                                                             models.CaregiverAssignment.patient_id == pid))
    if row:
        db.delete(row)
        db.commit()
        audit(db, user.id, "assignment_removed", f"patient:{pid},user:{uid}")
    return {"ok": True}
