"""
app/models/appointment.py
──────────────────────────
Appointment database model.
Links patients to doctors with scheduled times and status tracking.
"""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class Appointment(Base):
    __tablename__ = "appointments"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False)
    doctor_id = Column(Integer, ForeignKey("doctors.id"), nullable=False)
    scheduled_at = Column(DateTime(timezone=True), nullable=False)
    duration_minutes = Column(Integer, default=30)
    status = Column(String(20), default="scheduled")  # scheduled/completed/cancelled
    reason = Column(String(500), nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    patient = relationship("Patient", back_populates="appointments")
    doctor = relationship("Doctor", back_populates="appointments")
