"""
app/routers/patients.py
────────────────────────
Patient API routes.
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional, List

from app.core.database import get_db
from app.schemas.patient import PatientCreate, PatientUpdate, PatientResponse
from app.services import patient_service

router = APIRouter()


@router.post("/", response_model=PatientResponse, status_code=201)
def create_patient(data: PatientCreate, db: Session = Depends(get_db)):
    return patient_service.create_patient(db, data)


@router.get("/", response_model=List[PatientResponse])
def list_patients(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    is_active: Optional[bool] = None,
    db: Session = Depends(get_db)
):
    return patient_service.get_all_patients(db, skip=skip, limit=limit, is_active=is_active)


@router.get("/stats")
def patient_stats(db: Session = Depends(get_db)):
    return patient_service.get_patient_stats(db)


@router.get("/mrn/{mrn}", response_model=PatientResponse)
def get_by_mrn(mrn: str, db: Session = Depends(get_db)):
    patient = patient_service.get_patient_by_mrn(db, mrn)
    if not patient:
        raise HTTPException(status_code=404, detail=f"Patient with MRN {mrn} not found")
    return patient


@router.get("/{patient_id}", response_model=PatientResponse)
def get_patient(patient_id: int, db: Session = Depends(get_db)):
    patient = patient_service.get_patient(db, patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    return patient


@router.patch("/{patient_id}", response_model=PatientResponse)
def update_patient(patient_id: int, data: PatientUpdate, db: Session = Depends(get_db)):
    patient = patient_service.update_patient(db, patient_id, data)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    return patient


@router.delete("/{patient_id}", status_code=204)
def deactivate_patient(patient_id: int, db: Session = Depends(get_db)):
    success = patient_service.deactivate_patient(db, patient_id)
    if not success:
        raise HTTPException(status_code=404, detail="Patient not found")
