from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.orm import Session

from .. import models, services
from ..database import get_db
from ..security import allowed_patient_ids, audit, get_current_user, get_patient_or_403
from ..util import iso, now_utc
from ..ws import manager

router = APIRouter(prefix="/api", tags=["alerts"])


class AckIn(BaseModel):
    note: str = Field(default="", max_length=300)


def full(db, a, names):
    acks = db.execute(select(models.AlertAcknowledgement, models.User.name)
                      .join(models.User, models.User.id == models.AlertAcknowledgement.user_id)
                      .where(models.AlertAcknowledgement.alert_id == a.id)).all()
    notes = db.scalars(select(models.Notification).where(models.Notification.alert_id == a.id).order_by(models.Notification.id)).all()
    return {**services.alert_dict(a), "patient_name": names.get(a.patient_id, ""),
            "acknowledgements": [{"by": n, "ts": iso(k.ts), "note": k.note} for k, n in acks],
            "notifications": [{"user_id": x.user_id, "kind": x.kind, "channel": x.channel, "ts": iso(x.ts), "message": x.message} for x in notes]}


@router.get("/alerts")
def list_alerts(patient_id: int | None = None, status: str | None = None, limit: int = 100,
                db: Session = Depends(get_db), user=Depends(get_current_user)):
    ids = allowed_patient_ids(db, user)
    q = select(models.Alert).order_by(models.Alert.id.desc()).limit(min(limit, 300))
    if ids is not None:
        q = q.where(models.Alert.patient_id.in_(ids))
    if patient_id:
        get_patient_or_403(db, user, patient_id)
        q = q.where(models.Alert.patient_id == patient_id)
    if status:
        q = q.where(models.Alert.status == status)
    names = {p.id: p.name for p in db.scalars(select(models.Patient))}
    return [full(db, a, names) for a in db.scalars(q)]


@router.post("/alerts/{aid}/acknowledge")
async def acknowledge(aid: int, body: AckIn, db: Session = Depends(get_db), user=Depends(get_current_user)):
    a = db.get(models.Alert, aid)
    if not a:
        raise HTTPException(404, "Alert not found")
    get_patient_or_403(db, user, a.patient_id)
    if a.status == "acknowledged":
        raise HTTPException(409, "Alert already acknowledged")
    a.status, a.acknowledged_at = "acknowledged", now_utc()
    db.add(models.AlertAcknowledgement(alert_id=aid, user_id=user.id, note=body.note, ts=a.acknowledged_at))
    db.commit()
    audit(db, user.id, "alert_acknowledged", f"alert:{aid}")
    await manager.broadcast([{"type": "alert", "patient_id": a.patient_id, "alert": services.alert_dict(a)}])
    return full(db, a, {a.patient_id: ""})


@router.get("/notifications")
def notifications(db: Session = Depends(get_db), user=Depends(get_current_user)):
    rows = db.scalars(select(models.Notification).where(models.Notification.user_id == user.id)
                      .order_by(models.Notification.id.desc()).limit(50)).all()
    return [{"id": n.id, "alert_id": n.alert_id, "kind": n.kind, "channel": n.channel, "message": n.message, "ts": iso(n.ts)} for n in rows]
