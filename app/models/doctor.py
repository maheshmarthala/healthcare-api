"""
app/models/doctor.py
─────────────────────
Doctor database model.
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class Doctor(Base):
    __tablename__ = "doctors"

    id = Column(Integer, primary_key=True, index=True)
    license_number = Column(String(50), unique=True, nullable=False)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    specialization = Column(String(100), nullable=False)
    department = Column(String(100), nullable=False)
    phone = Column(String(20), nullable=True)
    email = Column(String(200), nullable=False)
    is_available = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    appointments = relationship("Appointment", back_populates="doctor")
    prescriptions = relationship("Prescription", back_populates="doctor")
