"""
app/models/patient.py
──────────────────────
Patient database model.
Stores sensitive PII — name, DOB, medical record number, blood type.
In production all PII fields would be encrypted at rest.
"""
from sqlalchemy import Column, Integer, String, Date, DateTime, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class Patient(Base):
    __tablename__ = "patients"

    id = Column(Integer, primary_key=True, index=True)
    mrn = Column(String(20), unique=True, index=True, nullable=False)  # Medical Record Number
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    date_of_birth = Column(Date, nullable=False)
    gender = Column(String(10), nullable=False)
    blood_type = Column(String(5), nullable=True)
    phone = Column(String(20), nullable=True)
    email = Column(String(200), nullable=True)
    address = Column(String(500), nullable=True)
    emergency_contact = Column(String(200), nullable=True)
    insurance_id = Column(String(100), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    appointments = relationship("Appointment", back_populates="patient")
    prescriptions = relationship("Prescription", back_populates="patient")
