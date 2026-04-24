"""
tests/test_patients.py
───────────────────────
Tests for the Patient Management API.
Uses in-memory SQLite — no file created, no cleanup needed.
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import date

from app.main import app
from app.core.database import Base, get_db

TEST_DB = "sqlite:///:memory:"
engine = create_engine(TEST_DB, connect_args={"check_same_thread": False})
TestSession = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    db = TestSession()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(autouse=True)
def setup():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


client = TestClient(app)

SAMPLE_PATIENT = {
    "first_name": "Mahesh",
    "last_name": "Marthala",
    "date_of_birth": "1998-05-15",
    "gender": "male",
    "blood_type": "O+",
    "phone": "+91-9876543210",
    "email": "mahesh@example.com",
    "insurance_id": "INS-12345"
}


def test_health_check():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "healthy"


def test_create_patient():
    r = client.post("/patients/", json=SAMPLE_PATIENT)
    assert r.status_code == 201
    data = r.json()
    assert data["first_name"] == "Mahesh"
    assert data["mrn"].startswith("MRN-")
    assert data["is_active"] is True


def test_mrn_is_unique():
    r1 = client.post("/patients/", json=SAMPLE_PATIENT)
    r2 = client.post("/patients/", json=SAMPLE_PATIENT)
    assert r1.json()["mrn"] != r2.json()["mrn"]


def test_get_patient_by_id():
    created = client.post("/patients/", json=SAMPLE_PATIENT).json()
    r = client.get(f"/patients/{created['id']}")
    assert r.status_code == 200
    assert r.json()["id"] == created["id"]


def test_get_patient_by_mrn():
    created = client.post("/patients/", json=SAMPLE_PATIENT).json()
    r = client.get(f"/patients/mrn/{created['mrn']}")
    assert r.status_code == 200
    assert r.json()["mrn"] == created["mrn"]


def test_patient_not_found():
    r = client.get("/patients/99999")
    assert r.status_code == 404


def test_list_patients():
    client.post("/patients/", json=SAMPLE_PATIENT)
    client.post("/patients/", json=SAMPLE_PATIENT)
    r = client.get("/patients/")
    assert len(r.json()) == 2


def test_update_patient():
    created = client.post("/patients/", json=SAMPLE_PATIENT).json()
    r = client.patch(f"/patients/{created['id']}", json={"phone": "+91-1111111111"})
    assert r.status_code == 200
    assert r.json()["phone"] == "+91-1111111111"


def test_deactivate_patient():
    created = client.post("/patients/", json=SAMPLE_PATIENT).json()
    r = client.delete(f"/patients/{created['id']}")
    assert r.status_code == 204
    detail = client.get(f"/patients/{created['id']}").json()
    assert detail["is_active"] is False


def test_patient_stats():
    client.post("/patients/", json=SAMPLE_PATIENT)
    client.post("/patients/", json=SAMPLE_PATIENT)
    r = client.get("/patients/stats")
    data = r.json()
    assert data["total_patients"] == 2
    assert data["active_patients"] == 2


def test_invalid_gender_rejected():
    bad = {**SAMPLE_PATIENT, "gender": "unknown"}
    r = client.post("/patients/", json=bad)
    assert r.status_code == 422


def test_soft_delete_not_hard_delete():
    created = client.post("/patients/", json=SAMPLE_PATIENT).json()
    client.delete(f"/patients/{created['id']}")
    r = client.get(f"/patients/{created['id']}")
    assert r.status_code == 200
    assert r.json()["is_active"] is False
