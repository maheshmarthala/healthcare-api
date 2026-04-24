"""
app/core/database.py
─────────────────────
Database connection setup using SQLAlchemy.
Uses SQLite for local development.
In production this would point to PostgreSQL on AWS RDS.
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

DATABASE_URL = "sqlite:///./healthcare.db"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_tables():
    from app.models.patient import Patient
    from app.models.appointment import Appointment
    from app.models.prescription import Prescription
    from app.models.doctor import Doctor
    Base.metadata.create_all(bind=engine)
