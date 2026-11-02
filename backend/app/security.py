from datetime import datetime, timedelta, timezone

import bcrypt
import jwt
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.orm import Session

from . import models
from .config import settings
from .database import get_db

bearer = HTTPBearer(auto_error=False)
ROLES = ("admin", "caregiver", "doctor")


def hash_password(p: str) -> str:
    return bcrypt.hashpw(p.encode(), bcrypt.gensalt()).decode()


def verify_password(p: str, h: str) -> bool:
    try:
        return bcrypt.checkpw(p.encode(), h.encode())
    except ValueError:
        return False


def create_token(user) -> str:
    exp = datetime.now(timezone.utc) + timedelta(minutes=settings.TOKEN_MINUTES)
    return jwt.encode({"sub": str(user.id), "role": user.role, "exp": exp}, settings.SECRET_KEY, algorithm="HS256")


def decode_token(token: str):
    try:
        return jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
    except jwt.PyJWTError:
        return None


def user_from_token(db: Session, token: str):
    payload = decode_token(token)
    if not payload:
        return None
    user = db.get(models.User, int(payload["sub"]))
    return user if user and user.is_active else None


def get_current_user(creds: HTTPAuthorizationCredentials = Depends(bearer), db: Session = Depends(get_db)):
    if not creds:
        raise HTTPException(401, "Not authenticated")
    user = user_from_token(db, creds.credentials)
    if not user:
        raise HTTPException(401, "Invalid or expired token")
    return user


def require_roles(*roles):
    def dep(user=Depends(get_current_user)):
        if user.role not in roles:
            raise HTTPException(403, "Your role is not permitted to do this")
        return user
    return dep


def audit(db: Session, user_id, action: str, target: str = ""):
    db.add(models.AuditLog(user_id=user_id, action=action, target=target))
    db.commit()


def allowed_patient_ids(db: Session, user):
    """None = all patients (admin). Otherwise the assigned patient ids."""
    if user.role == "admin":
        return None
    return list(db.scalars(select(models.CaregiverAssignment.patient_id).where(models.CaregiverAssignment.user_id == user.id)))


def get_patient_or_403(db: Session, user, patient_id: int):
    patient = db.get(models.Patient, patient_id)
    if not patient:
        raise HTTPException(404, "Patient not found")
    ids = allowed_patient_ids(db, user)
    if ids is not None and patient_id not in ids:
        audit(db, user.id, "access_denied", f"patient:{patient_id}")
        raise HTTPException(403, "You are not authorised to access this patient")
    return patient
