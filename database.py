# database.py — SQLite setup via SQLAlchemy

from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from models import Base, LeaseRecord, PipelineResult

DATABASE_URL = "sqlite:///./leases.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

def init_db():
    Base.metadata.create_all(bind=engine)

def get_db():
    db = Session(engine)
    try:
        yield db
    finally:
        db.close()

def save_lease(db: Session, result: PipelineResult, filename: str) -> LeaseRecord:
    record = LeaseRecord(
        filename=filename,
        lease_data=result.lease.model_dump(mode="json"),
        risk_data=result.risk.model_dump(mode="json"),
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record

def fetch_lease(db: Session, lease_id: int) -> LeaseRecord | None:
    return db.get(LeaseRecord, lease_id)

def fetch_all_leases(db: Session) -> list[LeaseRecord]:
    return db.query(LeaseRecord).order_by(LeaseRecord.created_at.desc()).all()
