"""
app/schemas/patient.py
───────────────────────
Pydantic schemas for request validation and response serialization.
Separates what comes IN from what goes OUT —
ensuring we never accidentally expose sensitive fields.
"""
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import date, datetime


class PatientCreate(BaseModel):
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    date_of_birth: date
    gender: str = Field(..., pattern="^(male|female|other)$")
    blood_type: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None
    emergency_contact: Optional[str] = None
    insurance_id: Optional[str] = None


class PatientUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None
    emergency_contact: Optional[str] = None
    insurance_id: Optional[str] = None


class PatientResponse(BaseModel):
    id: int
    mrn: str
    first_name: str
    last_name: str
    date_of_birth: date
    gender: str
    blood_type: Optional[str]
    phone: Optional[str]
    email: Optional[str]
    is_active: bool
    created_at: Optional[datetime]

    model_config = {"from_attributes": True}


class AppointmentCreate(BaseModel):
    patient_id: int
    doctor_id: int
    scheduled_at: datetime
    duration_minutes: int = Field(default=30, ge=15, le=120)
    reason: Optional[str] = None


class AppointmentResponse(BaseModel):
    id: int
    patient_id: int
    doctor_id: int
    scheduled_at: datetime
    duration_minutes: int
    status: str
    reason: Optional[str]
    created_at: Optional[datetime]

    model_config = {"from_attributes": True}


class PrescriptionCreate(BaseModel):
    patient_id: int
    doctor_id: int
    medication_name: str = Field(..., min_length=1, max_length=200)
    dosage: str
    frequency: str
    duration_days: int = Field(..., ge=1, le=365)
    instructions: Optional[str] = None
    valid_until: date
    refills_remaining: int = Field(default=0, ge=0, le=12)


class PrescriptionResponse(BaseModel):
    id: int
    patient_id: int
    doctor_id: int
    medication_name: str
    dosage: str
    frequency: str
    duration_days: int
    valid_until: date
    is_active: bool
    refills_remaining: int

    model_config = {"from_attributes": True}
