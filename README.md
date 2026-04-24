# Healthcare Patient Management API

A HIPAA-aware REST API for managing hospital patients, appointments, and prescriptions. Built with FastAPI and SQLAlchemy.

## Domain

Real hospital operations:
- Patient registration with auto-generated Medical Record Numbers (MRN)
- Appointment scheduling between patients and doctors
- Prescription management with refill tracking
- Soft-delete compliance (HIPAA requires 6-year record retention)

## Run locally

```bash
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # Mac/Linux

pip install -r requirements.txt
uvicorn app.main:app --reload
```

API docs: http://localhost:8000/docs

## Endpoints

| Method | URL | Description |
|--------|-----|-------------|
| POST | /patients/ | Register new patient |
| GET | /patients/ | List all patients |
| GET | /patients/{id} | Get patient by ID |
| GET | /patients/mrn/{mrn} | Get patient by MRN |
| PATCH | /patients/{id} | Update patient |
| DELETE | /patients/{id} | Soft-deactivate patient |
| GET | /patients/stats | Patient statistics |

## Run tests

```bash
pytest tests/ -v
```

## Architecture

```
app/
├── core/       → database connection
├── models/     → SQLAlchemy ORM models
├── schemas/    → Pydantic validation
├── routers/    → FastAPI routes
└── services/   → business logic
```

## Security note

Patient data contains PII (Personally Identifiable Information). In production:
- All PII fields encrypted at rest (AWS KMS)
- All API calls require JWT authentication
- Audit logs for every data access
- Deployed in private VPC — no public internet access
