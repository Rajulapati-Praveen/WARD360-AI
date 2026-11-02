"""Synthetic demo data (users, patients, devices, ~25 min of simulated history)."""
import json
from datetime import timedelta

from sqlalchemy.orm import Session

from . import models
from .security import hash_password
from .simulation import PatientSim
from .util import now_utc

DEMO_USERS = [("Demo Admin", "admin@ward360.test", "Admin@123", "admin"),
              ("Demo Caregiver", "caregiver@ward360.test", "Care@123", "caregiver"),
              ("Demo Doctor", "doctor@ward360.test", "Doctor@123", "doctor")]
BASE = {"heart_rate": 75, "spo2": 97, "temperature": 36.8, "resp_rate": 16}
PATIENTS = [("Synthetic Patient A", 72, "female", BASE),
            ("Synthetic Patient B", 65, "male", {**BASE, "heart_rate": 70}),
            ("Synthetic Patient C", 80, "female", {**BASE, "spo2": 95, "heart_rate": 78})]


def seed(db: Session, history: int = 150) -> bool:
    if db.query(models.User).count():
        return False
    users = [models.User(name=n, email=e, password_hash=hash_password(p), role=r) for n, e, p, r in DEMO_USERS]
    db.add_all(users)
    db.flush()
    start = now_utc() - timedelta(seconds=10 * history + 30)
    for i, (name, age, gender, base) in enumerate(PATIENTS):
        p = models.Patient(name=name, age=age, gender=gender, notes="Synthetic demo patient", baseline_json=json.dumps(base))
        db.add(p)
        db.flush()
        d = models.Device(patient_id=p.id, name=f"SimBand-{p.id}", kind="simulated", status="offline", battery=100)
        db.add(d)
        db.flush()
        for u in users[1:]:
            db.add(models.CaregiverAssignment(user_id=u.id, patient_id=p.id))
        sim = PatientSim(base, seed=100 + i)
        for k in range(history):
            x = sim.next()
            db.add(models.VitalReading(patient_id=p.id, device_id=d.id, ts=start + timedelta(seconds=10 * k),
                                       heart_rate=x["heart_rate"], spo2=x["spo2"], temperature=x["temperature"],
                                       resp_rate=x["resp_rate"], activity=x["activity"], accel_magnitude=x["accel_magnitude"],
                                       quality="good", is_simulated=True))
    db.commit()
    return True
