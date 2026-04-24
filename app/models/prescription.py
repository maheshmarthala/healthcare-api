"""
app/models/prescription.py
───────────────────────────
Prescription database model.
Tracks medications prescribed to patients by doctors.
"""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Date
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class Prescription(Base):
    __tablename__ = "prescriptions"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False)
    doctor_id = Column(Integer, ForeignKey("doctors.id"), nullable=False)
    medication_name = Column(String(200), nullable=False)
    dosage = Column(String(100), nullable=False)
    frequency = Column(String(100), nullable=False)
    duration_days = Column(Integer, nullable=False)
    instructions = Column(Text, nullable=True)
    prescribed_at = Column(DateTime(timezone=True), server_default=func.now())
    valid_until = Column(Date, nullable=False)
    is_active = Column(Boolean, default=True)
    refills_remaining = Column(Integer, default=0)

    patient = relationship("Patient", back_populates="prescriptions")
    doctor = relationship("Doctor", back_populates="prescriptions")


from sqlalchemy import Boolean
