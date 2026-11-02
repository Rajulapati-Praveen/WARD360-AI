from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy import select
from sqlalchemy.orm import Session

from .. import models
from ..database import get_db
from ..security import (ROLES, audit, create_token, get_current_user, hash_password, require_roles, verify_password)

router = APIRouter(prefix="/api", tags=["auth"])


class LoginIn(BaseModel):
    email: str = Field(min_length=3, max_length=150)
    password: str = Field(min_length=1, max_length=128)


class UserIn(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    email: str = Field(min_length=5, max_length=150, pattern=r"^[^@\s]+@[^@\s]+$")
    password: str = Field(min_length=8, max_length=128)
    role: str


def user_dict(u):
    return {"id": u.id, "name": u.name, "email": u.email, "role": u.role, "is_active": u.is_active}


@router.post("/auth/login")
def login(body: LoginIn, db: Session = Depends(get_db)):
    user = db.scalar(select(models.User).where(models.User.email == body.email.lower()))
    if not user or not user.is_active or not verify_password(body.password, user.password_hash):
        audit(db, user.id if user else None, "login_failed", body.email[:80])
        raise HTTPException(401, "Incorrect email or password")
    audit(db, user.id, "login", "")
    return {"token": create_token(user), "user": user_dict(user)}


@router.get("/auth/me")
def me(user=Depends(get_current_user)):
    return user_dict(user)


@router.get("/users")
def users(db: Session = Depends(get_db), user=Depends(require_roles("admin"))):
    return [user_dict(u) for u in db.scalars(select(models.User).order_by(models.User.id))]


@router.post("/users", status_code=201)
def create_user(body: UserIn, db: Session = Depends(get_db), user=Depends(require_roles("admin"))):
    if body.role not in ROLES:
        raise HTTPException(422, f"role must be one of {ROLES}")
    email = body.email.lower()
    if db.scalar(select(models.User).where(models.User.email == email)):
        raise HTTPException(409, "Email already registered")
    u = models.User(name=body.name, email=email, password_hash=hash_password(body.password), role=body.role)
    db.add(u)
    db.commit()
    audit(db, user.id, "user_created", f"user:{u.id}")
    return user_dict(u)
