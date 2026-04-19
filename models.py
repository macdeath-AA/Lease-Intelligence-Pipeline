# models.py — Pydantic schemas + SQLAlchemy ORM models

from datetime import date
from pydantic import BaseModel

# --- Pydantic (API / validation) ---

class LeaseData(BaseModel):
    tenant_name: str | None = None
    property_address: str | None = None
    lease_start: date | None = None
    lease_end: date | None = None
    term_months: int | None = None
    base_rent_monthly: float | None = None
    rent_escalation_pct: float | None = None
    security_deposit: float | None = None
    personal_guarantee: bool | None = None
    options: list[str] = []
    key_clauses: list[str] = []

class RiskAnalysis(BaseModel):
    risk_flags: list[str] = []
    summary: str | None = None
    risk_score: int | None = None  # 1–10

class PipelineResult(BaseModel):
    lease: LeaseData
    risk: RiskAnalysis

# --- SQLAlchemy (DB) ---

from sqlalchemy import Column, Integer, String, JSON, DateTime
from sqlalchemy.orm import DeclarativeBase
from datetime import datetime

class Base(DeclarativeBase):
    pass

class LeaseRecord(Base):
    __tablename__ = "leases"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String)
    lease_data = Column(JSON)
    risk_data = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
