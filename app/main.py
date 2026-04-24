"""
app/main.py
────────────
Healthcare Patient Management API entry point.
"""
from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.core.database import create_tables
from app.routers.patients import router as patients_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_tables()
    yield


app = FastAPI(
    title="Healthcare Patient Management API",
    description="""
    A HIPAA-aware REST API for managing hospital patients,
    appointments, and prescriptions.

    Designed for use in mid-size hospitals and clinics.
    All patient data (PII) is handled with strict access controls.
    """,
    version="1.0.0",
    lifespan=lifespan,
)

app.include_router(patients_router, prefix="/patients", tags=["patients"])


@app.get("/health")
def health():
    return {
        "status": "healthy",
        "service": "Healthcare Patient Management API",
        "version": "1.0.0"
    }
