"""
app/services/patient_service.py
────────────────────────────────
Patient business logic layer.
All database operations for patients live here.
Routes call these functions — no DB logic in routes.
"""
import random
import string
import logging
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime

from app.models.patient import Patient
from app.schemas.patient import PatientCreate, PatientUpdate

logger = logging.getLogger(__name__)


def generate_mrn() -> str:
    """
    Generate a unique Medical Record Number.

    Format: MRN-XXXXXX where X is alphanumeric.
    MRNs are unique identifiers for patients in the hospital system.

    Returns:
        str: A unique MRN string in format MRN-XXXXXX
    """
    chars = string.ascii_uppercase + string.digits
    suffix = "".join(random.choices(chars, k=8))
    return f"MRN-{suffix}"


def get_patient(db: Session, patient_id: int) -> Optional[Patient]:
    """
    Retrieve a single patient by their internal database ID.

    Args:
        db: Database session
        patient_id: Internal integer ID of the patient

    Returns:
        Patient object if found, None otherwise
    """
    return db.query(Patient).filter(Patient.id == patient_id).first()


def get_patient_by_mrn(db: Session, mrn: str) -> Optional[Patient]:
    """
    Retrieve a patient by their Medical Record Number.

    Args:
        db: Database session
        mrn: Medical Record Number e.g. MRN-ABC12345

    Returns:
        Patient object if found, None otherwise
    """
    return db.query(Patient).filter(Patient.mrn == mrn).first()


def get_all_patients(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    is_active: Optional[bool] = None
) -> list[Patient]:
    """
    Retrieve all patients with optional filtering and pagination.

    Args:
        db: Database session
        skip: Number of records to skip (for pagination)
        limit: Maximum number of records to return
        is_active: If provided, filter by active/inactive status

    Returns:
        List of Patient objects
    """
    query = db.query(Patient)
    if is_active is not None:
        query = query.filter(Patient.is_active == is_active)
    return query.offset(skip).limit(limit).all()


def create_patient(db: Session, data: PatientCreate) -> Patient:
    """
    Create a new patient record in the database.

    Automatically generates a unique Medical Record Number.

    Args:
        db: Database session
        data: PatientCreate schema with validated patient data

    Returns:
        Newly created Patient object with generated MRN
    """
    mrn = generate_mrn()
    patient = Patient(
        mrn=mrn,
        first_name=data.first_name,
        last_name=data.last_name,
        date_of_birth=data.date_of_birth,
        gender=data.gender,
        blood_type=data.blood_type,
        phone=data.phone,
        email=data.email,
        address=data.address,
        emergency_contact=data.emergency_contact,
        insurance_id=data.insurance_id,
    )
    db.add(patient)
    db.commit()
    db.refresh(patient)
    logger.info(f"Patient created with MRN: {mrn}")
    return patient


def update_patient(db: Session, patient_id: int, data: PatientUpdate) -> Optional[Patient]:
    """
    Update an existing patient record.

    Args:
        db: Database session
        patient_id: ID of patient to update
        data: PatientUpdate schema with fields to change

    Returns:
        Updated Patient object, or None if not found
    """
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not patient:
        return None
    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(patient, field, value)
    patient.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(patient)
    return patient


def deactivate_patient(db: Session, patient_id: int) -> bool:
    """
    Soft-delete a patient by marking them as inactive.

    We never hard-delete patient records for medical compliance reasons.
    HIPAA requires retention of medical records for minimum 6 years.

    Args:
        db: Database session
        patient_id: ID of patient to deactivate

    Returns:
        True if deactivated, False if patient not found
    """
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not patient:
        return False
    patient.is_active = False
    db.commit()
    logger.info(f"Patient {patient_id} deactivated (soft delete)")
    return True


def get_patient_stats(db: Session) -> dict:
    """
    Get aggregate statistics about the patient population.

    Returns:
        Dict with total, active, and inactive patient counts
    """
    total = db.query(Patient).count()
    active = db.query(Patient).filter(Patient.is_active == True).count()
    return {
        "total_patients": total,
        "active_patients": active,
        "inactive_patients": total - active,
    }
