"""Core pipeline: validate -> store -> anomaly -> risk -> fall/trend -> alerts -> notifications."""
import json
from datetime import timedelta

import pandas as pd
from sqlalchemy import select
from sqlalchemy.orm import Session

from ml import anomaly, fall, risk, trend
from ml.anomaly import FEATURES, DEFAULT_SD

from . import models
from .config import settings
from .util import aware, iso, now_utc

RANGES = {"heart_rate": (20, 250), "spo2": (50, 100), "temperature": (30, 43), "resp_rate": (3, 60)}
DEFAULT_BASELINE = {"heart_rate": 75, "spo2": 97, "temperature": 36.8, "resp_rate": 16}


# ---------- serializers ----------
def get_baseline(p) -> dict:
    return {**DEFAULT_BASELINE, **json.loads(p.baseline_json or "{}")}


def reading_dict(r) -> dict:
    return {"id": r.id, "patient_id": r.patient_id, "device_id": r.device_id, "ts": iso(r.ts),
            "heart_rate": r.heart_rate, "spo2": r.spo2, "temperature": r.temperature, "resp_rate": r.resp_rate,
            "activity": r.activity, "accel_magnitude": r.accel_magnitude, "quality": r.quality,
            "is_simulated": r.is_simulated}


def alert_dict(a) -> dict:
    return {"id": a.id, "patient_id": a.patient_id, "level": a.level, "source": a.source, "message": a.message,
            "status": a.status, "created_at": iso(a.created_at), "escalated_at": iso(a.escalated_at),
            "acknowledged_at": iso(a.acknowledged_at)}


def device_dict(d) -> dict:
    return {"id": d.id, "patient_id": d.patient_id, "name": d.name, "kind": d.kind, "status": d.status,
            "battery": d.battery, "last_seen": iso(d.last_seen)}


def risk_dict(r) -> dict:
    return {"id": r.id, "patient_id": r.patient_id, "ts": iso(r.ts), "level": r.level,
            "reasons": json.loads(r.reasons_json), "action": r.suggested_action}


def anomaly_dict(a) -> dict:
    return {"id": a.id, "patient_id": a.patient_id, "reading_id": a.reading_id, "ts": iso(a.ts),
            "feature": a.feature, "model_score": a.model_score, "explanation": a.explanation}


# ---------- helpers ----------
def validate_vitals(payload: dict):
    clean, issues = {}, []
    for k, (lo, hi) in RANGES.items():
        v = payload.get(k)
        if v is None:
            clean[k] = None
        elif lo <= v <= hi:
            clean[k] = float(v)
        else:
            clean[k] = None
            issues.append(f"{k}={v} outside valid range {lo}-{hi}")
    present = [v for v in clean.values() if v is not None]
    if not present:
        quality = "missing"
    elif len(present) < 4 or issues or payload.get("quality") in ("poor", "missing"):
        quality = "poor"
    else:
        quality = "good"
    return clean, issues, quality


def recipients(db: Session, patient_id: int, include_admins=False):
    ids = set(db.scalars(select(models.CaregiverAssignment.user_id).where(models.CaregiverAssignment.patient_id == patient_id)))
    if include_admins:
        ids |= set(db.scalars(select(models.User.id).where(models.User.role == "admin", models.User.is_active == True)))  # noqa: E712
    return ids


def notify(db: Session, alert, kind: str):
    channel = "simulated-sms" if kind == "escalation" else "simulated-push"
    prefix = "ESCALATED - not acknowledged: " if kind == "escalation" else ""
    for uid in recipients(db, alert.patient_id, include_admins=(kind == "escalation")):
        db.add(models.Notification(alert_id=alert.id, user_id=uid, kind=kind, channel=channel,
                                   message=f"{prefix}[{alert.level.upper()}] {alert.message}"))
    db.commit()


def raise_alert(db: Session, patient, level, source, message, events, now=None):
    now = now or now_utc()
    last = db.scalar(select(models.Alert).where(models.Alert.patient_id == patient.id, models.Alert.source == source)
                     .order_by(models.Alert.id.desc()))
    if last and last.status in ("open", "escalated"):
        if level == "critical" and last.level == "warning":
            last.level, last.message = "critical", message
            db.commit()
            notify(db, last, "new")
            events.append({"type": "alert", "patient_id": patient.id, "alert": alert_dict(last)})
        return last
    if last and last.status == "acknowledged" and last.acknowledged_at and \
            (now - aware(last.acknowledged_at)).total_seconds() < settings.ALERT_COOLDOWN_SECONDS:
        return last  # cooldown after caregiver acknowledged
    a = models.Alert(patient_id=patient.id, level=level, source=source, message=message, status="open", created_at=now)
    db.add(a)
    db.commit()
    db.refresh(a)
    notify(db, a, "new")
    events.append({"type": "alert", "patient_id": patient.id, "alert": alert_dict(a)})
    return a


def history_df(db: Session, patient_id: int, before_id: int, limit=300):
    rows = db.scalars(select(models.VitalReading).where(models.VitalReading.patient_id == patient_id,
                      models.VitalReading.id < before_id).order_by(models.VitalReading.id.desc()).limit(limit)).all()
    return pd.DataFrame([{f: getattr(r, f) for f in FEATURES} for r in rows], columns=FEATURES)


def series_for(db: Session, patient_id: int, limit=60):
    rows = db.scalars(select(models.VitalReading).where(models.VitalReading.patient_id == patient_id)
                      .order_by(models.VitalReading.id.desc()).limit(limit)).all()
    return list(reversed(rows))


def compute_trends(rows, patient, sds=None):
    base = get_baseline(patient)
    sds = sds or DEFAULT_SD
    ts = [aware(r.ts).timestamp() for r in rows]
    return {f: trend.analyse(ts, [getattr(r, f) for r in rows], base[f], sds[f]) for f in FEATURES}


# ---------- main pipeline ----------
def process_reading(db: Session, patient, device, data: dict) -> list:
    events = []
    clean, issues, quality = validate_vitals(data)
    accel = data.get("accel_magnitude")
    r = models.VitalReading(patient_id=patient.id, device_id=device.id if device else None, ts=now_utc(), **clean,
                            activity=(data.get("activity") or "resting")[:20],
                            accel_magnitude=accel, quality=quality, is_simulated=True)
    db.add(r)
    if device:
        device.status, device.last_seen = "online", r.ts
        if data.get("battery") is not None:
            device.battery = max(0, min(100, int(data["battery"])))
    db.commit()
    db.refresh(r)

    base = get_baseline(patient)
    reading = reading_dict(r)
    hist = history_df(db, patient.id, r.id)
    an = anomaly.detect(reading, hist, base, patient.id)
    if an["is_anomaly"]:
        db.add(models.AnomalyEvent(patient_id=patient.id, reading_id=r.id, ts=r.ts, feature=an["feature"],
                                   model_score=an["model_score"] if an["model_score"] is not None else 0.0,
                                   explanation=an["explanation"]))
    recent_rows = series_for(db, patient.id, 30)
    recent = [reading_dict(x) for x in recent_rows[-5:]]
    rk = risk.assess(recent, base, an["sds"])
    ra = models.RiskAssessment(patient_id=patient.id, ts=r.ts, level=rk["level"],
                               reasons_json=json.dumps(rk["reasons"]), suggested_action=rk["action"])
    db.add(ra)
    db.commit()
    db.refresh(ra)

    if rk["level"] in ("warning", "critical"):
        raise_alert(db, patient, rk["level"], "risk", f"Risk {rk['level']}: " + "; ".join(rk["reasons"][:3]), events)
    fe = fall.detect(reading)
    if fe:
        raise_alert(db, patient, "critical", "fall", fe["message"], events)
    if sum(1 for x in recent if x["quality"] == "missing") >= 3:
        raise_alert(db, patient, "warning", "device", "Sensor data missing or unreliable for several readings.", events)
    if device and device.battery <= 15:
        raise_alert(db, patient, "warning", "device", f"{device.name} battery low ({device.battery}%).", events)
    # trend-based early warning (only when drifting AWAY from the personal baseline)
    if len([x for x in recent_rows if x.heart_rate is not None]) >= 20:
        for f, t in compute_trends(recent_rows, patient, an["sds"]).items():
            if t["abnormal"] and t["baseline_deviation"] * t["change_over_window"] > 0 \
                    and abs(t["baseline_deviation"]) >= an["sds"][f]:
                raise_alert(db, patient, "warning", "trend",
                            f"{anomaly.LABELS[f]} is {t['direction']} away from baseline "
                            f"({t['baseline_deviation']:+.1f} {anomaly.UNITS[f]} vs baseline).", events)
                break
    db.commit()
    events.append({"type": "reading", "patient_id": patient.id, "reading": reading,
                   "risk": {"level": rk["level"], "reasons": rk["reasons"], "action": rk["action"],
                            "confidence": rk["confidence"], "contributions": rk["contributions"]},
                   "anomaly": {k: an[k] for k in ("is_anomaly", "feature", "model_score", "explanation")},
                   "device": device_dict(device) if device else None, "issues": issues})
    return events


def run_device_check(db: Session, now=None, timeout=None) -> list:
    now, timeout = now or now_utc(), timeout or settings.DEVICE_TIMEOUT_SECONDS
    events = []
    for d in db.scalars(select(models.Device).where(models.Device.status == "online")).all():
        if d.last_seen and (now - aware(d.last_seen)).total_seconds() > timeout:
            d.status = "offline"
            db.commit()
            p = db.get(models.Patient, d.patient_id)
            raise_alert(db, p, "warning", "device", f"{d.name} disconnected - no data received.", events, now=now)
            events.append({"type": "device", "patient_id": d.patient_id, "device": device_dict(d)})
    return events


def run_escalation_check(db: Session, now=None, seconds=None) -> list:
    now = now or now_utc()
    seconds = settings.ESCALATION_SECONDS if seconds is None else seconds
    events = []
    for a in db.scalars(select(models.Alert).where(models.Alert.status == "open")).all():
        if (now - aware(a.created_at)).total_seconds() >= seconds:
            a.status, a.escalated_at = "escalated", now
            db.commit()
            notify(db, a, "escalation")
            events.append({"type": "alert", "patient_id": a.patient_id, "alert": alert_dict(a)})
    return events
