"""
app/services/search_service.py
───────────────────────────────
Search and analytics service — added in feature branch.
This file contains intentional real-world issues
that the autonomous code review agent will catch:

  1. SQL injection via f-string query building
  2. PII exposed in logs (patient name printed to console)
  3. Bare except hiding real errors
  4. Hardcoded pagination limit
  5. Missing docstrings
  6. No input validation on search term
"""
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.models.patient import Patient
from app.models.appointment import Appointment
from app.models.prescription import Prescription


# ── INTENTIONAL ISSUE 1: SQL Injection ────────────────────────────────────────
# Building SQL with f-string = SQL injection vulnerability
# Attacker can pass: " OR 1=1 --  and get ALL patient records
def search_patients_by_name(db: Session, name: str):
    query = f"SELECT * FROM patients WHERE first_name LIKE '%{name}%' OR last_name LIKE '%{name}%'"
    result = db.execute(text(query))
    return result.fetchall()


# ── INTENTIONAL ISSUE 2: PII in logs ─────────────────────────────────────────
# Patient full name + date of birth printed to console log
# Violates HIPAA — PII must never appear in plain text logs
def get_patient_details(db: Session, patient_id: int):
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if patient:
        print(f"Fetching patient: {patient.first_name} {patient.last_name}, DOB: {patient.date_of_birth}")
    return patient


# ── INTENTIONAL ISSUE 3: Bare except ─────────────────────────────────────────
# Swallows ALL exceptions including database errors
# Doctor will never know if prescription lookup failed
def get_patient_prescriptions(db: Session, patient_id: int):
    try:
        prescriptions = db.query(Prescription).filter(
            Prescription.patient_id == patient_id,
            Prescription.is_active == True
        ).all()
        return prescriptions
    except:
        return []


# ── INTENTIONAL ISSUE 4: Hardcoded values ────────────────────────────────────
# LIMIT 1000 hardcoded — will crash database on large hospitals
# No pagination, no filtering — returns everything
def get_all_appointments_today(db: Session):
    # TODO: add date filtering
    # TODO: add pagination
    from datetime import date
    today = date.today()
    result = db.execute(
        text(f"SELECT * FROM appointments WHERE DATE(scheduled_at) = '{today}' LIMIT 1000")
    )
    return result.fetchall()


# ── INTENTIONAL ISSUE 5: No input validation ─────────────────────────────────
# department can be anything — no validation
# SQL built directly with user input
def get_doctors_by_department(db: Session, department: str):
    query = f"SELECT * FROM doctors WHERE department = '{department}'"
    result = db.execute(text(query))
    return result.fetchall()


# ── INTENTIONAL ISSUE 6: Business logic error ────────────────────────────────
# Prescription refill allowed even if prescription is expired
# No date check — patient could get medication after valid_until date
def request_prescription_refill(db: Session, prescription_id: int):
    prescription = db.query(Prescription).filter(
        Prescription.id == prescription_id
    ).first()

    if not prescription:
        return None

    # BUG: Should check prescription.valid_until >= today
    # BUG: Should check prescription.refills_remaining > 0
    prescription.refills_remaining -= 1
    db.commit()
    return prescription
