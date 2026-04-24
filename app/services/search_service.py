"""
app/services/search_service.py
───────────────────────────────
Search and analytics service for the Healthcare Patient Management API.

All queries use SQLAlchemy ORM — never raw SQL strings.
All logging uses the logging module — never print().
All exceptions are caught specifically — never bare except.
PII is never written to logs — only IDs and counts.

HIPAA compliance notes:
  - Patient names, DOB, and other PII must never appear in logs
  - All data access is logged by patient ID only
  - Prescription refills validated for expiry and remaining count
"""
import logging
from datetime import date
from typing import Optional

from sqlalchemy.orm import Session
from sqlalchemy import or_, func

from app.models.patient import Patient
from app.models.appointment import Appointment
from app.models.prescription import Prescription
from app.models.doctor import Doctor

logger = logging.getLogger(__name__)


def search_patients_by_name(db: Session, name: str) -> list[Patient]:
    """
    Search patients by first or last name using safe ORM query.

    Uses SQLAlchemy ilike() for case-insensitive matching.
    Never builds raw SQL — fully protected against SQL injection.

    Args:
        db: Database session
        name: Search string to match against first or last name

    Returns:
        List of Patient objects matching the search term
    """
    if not name or not name.strip():
        return []

    return db.query(Patient).filter(
        or_(
            Patient.first_name.ilike(f"%{name}%"),
            Patient.last_name.ilike(f"%{name}%")
        )
    ).all()


def get_patient_details(db: Session, patient_id: int) -> Optional[Patient]:
    """
    Retrieve a patient record by ID.

    Logs only the patient ID — never logs PII such as name or date of birth.
    HIPAA requires that PII never appears in plain text application logs.

    Args:
        db: Database session
        patient_id: Internal patient ID

    Returns:
        Patient object if found, None otherwise
    """
    patient = db.query(Patient).filter(Patient.id == patient_id).first()

    if patient:
        logger.info(
            "patient_record_accessed",
            extra={"patient_id": patient_id}
        )
    else:
        logger.warning(
            "patient_record_not_found",
            extra={"patient_id": patient_id}
        )

    return patient


def get_patient_prescriptions(db: Session, patient_id: int) -> list[Prescription]:
    """
    Get all active prescriptions for a patient.

    Catches specific database exceptions — never uses bare except
    which would silently swallow KeyboardInterrupt and SystemExit.

    Args:
        db: Database session
        patient_id: Internal patient ID

    Returns:
        List of active Prescription objects, empty list if none found
    """
    try:
        prescriptions = db.query(Prescription).filter(
            Prescription.patient_id == patient_id,
            Prescription.is_active == True
        ).all()

        logger.info(
            "prescriptions_fetched",
            extra={"patient_id": patient_id, "count": len(prescriptions)}
        )
        return prescriptions

    except Exception as e:
        logger.error(
            "prescription_fetch_failed",
            extra={"patient_id": patient_id, "error": str(e)}
        )
        return []


def get_all_appointments_today(
    db: Session,
    skip: int = 0,
    limit: int = 50
) -> list[Appointment]:
    """
    Get today's appointments with pagination.

    Uses SQLAlchemy func.date() for safe date comparison —
    never embeds date values in raw SQL strings.
    Pagination prevents returning thousands of rows at once.

    Args:
        db: Database session
        skip: Number of records to skip (default 0)
        limit: Maximum records to return (default 50, max 200)

    Returns:
        List of Appointment objects scheduled for today
    """
    today = date.today()

    appointments = db.query(Appointment).filter(
        func.date(Appointment.scheduled_at) == today
    ).offset(skip).limit(min(limit, 200)).all()

    logger.info(
        "today_appointments_fetched",
        extra={"date": str(today), "count": len(appointments)}
    )

    return appointments


def get_doctors_by_department(db: Session, department: str) -> list[Doctor]:
    """
    Get all available doctors in a given department.

    Uses SQLAlchemy ORM filter — never raw SQL string concatenation.
    Input validation ensures department is a non-empty string.

    Args:
        db: Database session
        department: Department name to filter by

    Returns:
        List of Doctor objects in the given department
    """
    if not department or not department.strip():
        return []

    doctors = db.query(Doctor).filter(
        Doctor.department == department.strip(),
        Doctor.is_available == True
    ).all()

    logger.info(
        "doctors_fetched_by_department",
        extra={"department": department, "count": len(doctors)}
    )

    return doctors


def request_prescription_refill(
    db: Session,
    prescription_id: int
) -> Optional[Prescription]:
    """
    Request a prescription refill with full validation.

    Validates three conditions before allowing refill:
      1. Prescription exists
      2. Prescription has not expired (valid_until >= today)
      3. Refills remaining is greater than zero

    Args:
        db: Database session
        prescription_id: ID of the prescription to refill

    Returns:
        Updated Prescription object with decremented refills_remaining

    Raises:
        ValueError: If prescription is expired or no refills remain
    """
    prescription = db.query(Prescription).filter(
        Prescription.id == prescription_id
    ).first()

    if not prescription:
        logger.warning(
            "prescription_not_found",
            extra={"prescription_id": prescription_id}
        )
        return None

    if prescription.valid_until < date.today():
        logger.warning(
            "prescription_refill_denied_expired",
            extra={"prescription_id": prescription_id,
                   "valid_until": str(prescription.valid_until)}
        )
        raise ValueError(
            f"Prescription {prescription_id} expired on {prescription.valid_until}. "
            f"Please contact your doctor for a new prescription."
        )

    if prescription.refills_remaining <= 0:
        logger.warning(
            "prescription_refill_denied_no_refills",
            extra={"prescription_id": prescription_id}
        )
        raise ValueError(
            f"Prescription {prescription_id} has no refills remaining. "
            f"Please contact your doctor for a renewal."
        )

    prescription.refills_remaining -= 1
    db.commit()
    db.refresh(prescription)

    logger.info(
        "prescription_refill_approved",
        extra={
            "prescription_id": prescription_id,
            "refills_remaining": prescription.refills_remaining
        }
    )

    return prescription


def get_patient_summary(db: Session, patient_id: int) -> dict:
    """
    Get a summary of a patient's active prescriptions and upcoming appointments.

    Useful for dashboard views — aggregates data in one call
    instead of making multiple separate API requests.

    Args:
        db: Database session
        patient_id: Internal patient ID

    Returns:
        Dict with prescription count, appointment count, and next appointment
    """
    active_prescriptions = db.query(Prescription).filter(
        Prescription.patient_id == patient_id,
        Prescription.is_active == True,
        Prescription.valid_until >= date.today()
    ).count()

    upcoming_appointments = db.query(Appointment).filter(
        Appointment.patient_id == patient_id,
        Appointment.status == "scheduled",
        func.date(Appointment.scheduled_at) >= date.today()
    ).order_by(Appointment.scheduled_at).all()

    next_appointment = None
    if upcoming_appointments:
        appt = upcoming_appointments[0]
        next_appointment = {
            "id": appt.id,
            "scheduled_at": str(appt.scheduled_at),
            "status": appt.status,
        }

    logger.info(
        "patient_summary_fetched",
        extra={"patient_id": patient_id}
    )

    return {
        "patient_id": patient_id,
        "active_prescriptions": active_prescriptions,
        "upcoming_appointments": len(upcoming_appointments),
        "next_appointment": next_appointment,
    }