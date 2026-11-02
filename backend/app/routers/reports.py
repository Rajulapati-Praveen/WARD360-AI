from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy import select
from sqlalchemy.orm import Session

from .. import models, services
from ..database import get_db
from ..reportpdf import build_pdf
from ..routers.alerts import full
from ..security import audit, get_current_user, get_patient_or_403
from ..util import aware, iso, now_utc
from ml import anomaly

router = APIRouter(prefix="/api/reports", tags=["reports"])


def build_report(db: Session, p, period: str) -> dict:
    hours = 24 if period == "daily" else 168
    now = now_utc()
    since = now - timedelta(hours=hours)
    rows = db.scalars(select(models.VitalReading).where(models.VitalReading.patient_id == p.id, models.VitalReading.ts >= since)
                      .order_by(models.VitalReading.id)).all()
    stats = {}
    for f in anomaly.FEATURES:
        vals = [getattr(r, f) for r in rows if getattr(r, f) is not None]
        stats[f] = {"min": round(min(vals), 1), "mean": round(sum(vals) / len(vals), 1), "max": round(max(vals), 1), "count": len(vals)} \
            if vals else {"min": "-", "mean": "-", "max": "-", "count": 0}
    total = len(rows)
    good = sum(1 for r in rows if r.quality == "good")
    step = max(1, total // 120)
    t0 = aware(rows[0].ts).timestamp() if rows else 0
    chart = {f: [((aware(r.ts).timestamp() - t0) / 60, getattr(r, f)) for r in rows[::step] if getattr(r, f) is not None]
             for f in ("heart_rate", "spo2")}
    risks = db.scalars(select(models.RiskAssessment).where(models.RiskAssessment.patient_id == p.id, models.RiskAssessment.ts >= since)).all()
    risk_counts = {}
    for x in risks:
        risk_counts[x.level] = risk_counts.get(x.level, 0) + 1
    an = db.scalars(select(models.AnomalyEvent).where(models.AnomalyEvent.patient_id == p.id, models.AnomalyEvent.ts >= since)
                    .order_by(models.AnomalyEvent.id.desc())).all()
    al = db.scalars(select(models.Alert).where(models.Alert.patient_id == p.id, models.Alert.created_at >= since)
                    .order_by(models.Alert.id.desc())).all()
    return {"period": period, "generated_at": iso(now)[:19].replace("T", " ") + " UTC",
            "patient": {"id": p.id, "name": p.name, "age": p.age}, "labels": anomaly.LABELS, "stats": stats,
            "availability": {"total": total, "good_pct": round(100 * good / total, 1) if total else 0,
                             "poor": sum(1 for r in rows if r.quality == "poor"), "missing": sum(1 for r in rows if r.quality == "missing")},
            "risk_counts": risk_counts or {"none": 0}, "chart": chart,
            "anomaly_count": len(an), "anomalies": [services.anomaly_dict(a) for a in an[:30]],
            "alert_count": len(al), "alerts": [full(db, a, {p.id: p.name}) for a in al[:40]]}


def _check(period):
    if period not in ("daily", "weekly"):
        raise HTTPException(422, "period must be daily or weekly")


@router.get("/{pid}/summary")
def summary(pid: int, period: str = "daily", db: Session = Depends(get_db), user=Depends(get_current_user)):
    _check(period)
    return build_report(db, get_patient_or_403(db, user, pid), period)


@router.get("/{pid}/pdf")
def pdf(pid: int, period: str = "daily", db: Session = Depends(get_db), user=Depends(get_current_user)):
    _check(period)
    p = get_patient_or_403(db, user, pid)
    data = build_pdf(build_report(db, p, period))
    db.add(models.HealthReport(patient_id=pid, period=period, file_path=f"generated-on-demand-{period}"))
    db.commit()
    audit(db, user.id, "report_generated", f"patient:{pid}:{period}")
    return Response(data, media_type="application/pdf",
                    headers={"Content-Disposition": f'attachment; filename="ward360-{period}-patient{pid}.pdf"'})
