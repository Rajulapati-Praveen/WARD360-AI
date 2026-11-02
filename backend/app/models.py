from datetime import datetime, timezone

from sqlalchemy import (Boolean, DateTime, Float, ForeignKey, Index, Integer,
                        String, Text, UniqueConstraint)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .database import Base


def now():
    return datetime.now(timezone.utc)


class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    email: Mapped[str] = mapped_column(String(150), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    role: Mapped[str] = mapped_column(String(20))  # admin | caregiver | doctor
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)


class Patient(Base):
    __tablename__ = "patients"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    age: Mapped[int] = mapped_column(Integer)
    gender: Mapped[str] = mapped_column(String(20), default="unspecified")
    notes: Mapped[str] = mapped_column(Text, default="")
    baseline_json: Mapped[str] = mapped_column(Text, default="{}")  # personal baseline
    is_synthetic: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)
    devices: Mapped[list["Device"]] = relationship(back_populates="patient")


class CaregiverAssignment(Base):
    __tablename__ = "caregiver_assignments"
    __table_args__ = (UniqueConstraint("user_id", "patient_id"),)
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    patient_id: Mapped[int] = mapped_column(ForeignKey("patients.id"), index=True)


class Device(Base):
    __tablename__ = "devices"
    id: Mapped[int] = mapped_column(primary_key=True)
    patient_id: Mapped[int] = mapped_column(ForeignKey("patients.id"), index=True)
    name: Mapped[str] = mapped_column(String(100))
    kind: Mapped[str] = mapped_column(String(30), default="simulated")
    status: Mapped[str] = mapped_column(String(20), default="offline")  # online | offline
    battery: Mapped[int] = mapped_column(Integer, default=100)
    last_seen: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    patient: Mapped["Patient"] = relationship(back_populates="devices")


class VitalReading(Base):
    __tablename__ = "vital_readings"
    __table_args__ = (Index("ix_vitals_patient_ts", "patient_id", "ts"),)
    id: Mapped[int] = mapped_column(primary_key=True)
    patient_id: Mapped[int] = mapped_column(ForeignKey("patients.id"))
    device_id: Mapped[int | None] = mapped_column(ForeignKey("devices.id"), nullable=True)
    ts: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)
    heart_rate: Mapped[float | None] = mapped_column(Float, nullable=True)
    spo2: Mapped[float | None] = mapped_column(Float, nullable=True)
    temperature: Mapped[float | None] = mapped_column(Float, nullable=True)
    resp_rate: Mapped[float | None] = mapped_column(Float, nullable=True)
    activity: Mapped[str] = mapped_column(String(20), default="resting")
    accel_magnitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    quality: Mapped[str] = mapped_column(String(20), default="good")  # good | poor | missing
    is_simulated: Mapped[bool] = mapped_column(Boolean, default=True)


class RiskAssessment(Base):
    __tablename__ = "risk_assessments"
    __table_args__ = (Index("ix_risk_patient_ts", "patient_id", "ts"),)
    id: Mapped[int] = mapped_column(primary_key=True)
    patient_id: Mapped[int] = mapped_column(ForeignKey("patients.id"))
    ts: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)
    level: Mapped[str] = mapped_column(String(20))  # normal | warning | critical
    reasons_json: Mapped[str] = mapped_column(Text, default="[]")
    suggested_action: Mapped[str] = mapped_column(Text, default="")


class AnomalyEvent(Base):
    __tablename__ = "anomaly_events"
    id: Mapped[int] = mapped_column(primary_key=True)
    patient_id: Mapped[int] = mapped_column(ForeignKey("patients.id"), index=True)
    reading_id: Mapped[int | None] = mapped_column(ForeignKey("vital_readings.id"), nullable=True)
    ts: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)
    feature: Mapped[str] = mapped_column(String(30))
    model_score: Mapped[float] = mapped_column(Float)  # model score, NOT clinical probability
    explanation: Mapped[str] = mapped_column(Text)


class Alert(Base):
    __tablename__ = "alerts"
    __table_args__ = (Index("ix_alerts_patient_status", "patient_id", "status"),)
    id: Mapped[int] = mapped_column(primary_key=True)
    patient_id: Mapped[int] = mapped_column(ForeignKey("patients.id"))
    level: Mapped[str] = mapped_column(String(20))  # warning | critical
    source: Mapped[str] = mapped_column(String(30))  # risk | anomaly | fall | device | manual
    message: Mapped[str] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(20), default="open")  # open | acknowledged | escalated
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)
    escalated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    acknowledged_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class AlertAcknowledgement(Base):
    __tablename__ = "alert_acknowledgements"
    id: Mapped[int] = mapped_column(primary_key=True)
    alert_id: Mapped[int] = mapped_column(ForeignKey("alerts.id"), index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    ts: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)
    note: Mapped[str] = mapped_column(Text, default="")


class HealthReport(Base):
    __tablename__ = "health_reports"
    id: Mapped[int] = mapped_column(primary_key=True)
    patient_id: Mapped[int] = mapped_column(ForeignKey("patients.id"), index=True)
    period: Mapped[str] = mapped_column(String(10))  # daily | weekly
    file_path: Mapped[str] = mapped_column(String(255), default="")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)


class AuditLog(Base):
    __tablename__ = "audit_logs"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    action: Mapped[str] = mapped_column(String(50))
    target: Mapped[str] = mapped_column(String(100), default="")
    ts: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)


class Notification(Base):
    """Simulated caregiver notification (push/SMS are simulated in this prototype)."""
    __tablename__ = "notifications"
    id: Mapped[int] = mapped_column(primary_key=True)
    alert_id: Mapped[int] = mapped_column(ForeignKey("alerts.id"), index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    kind: Mapped[str] = mapped_column(String(20), default="new")  # new | escalation
    channel: Mapped[str] = mapped_column(String(30), default="simulated-push")
    message: Mapped[str] = mapped_column(Text, default="")
    ts: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)
