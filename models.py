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
    bedrooms: int | None = None
    sqft: float | None = None
    options: list[str] = []
    key_clauses: list[str] = []

class RiskAnalysis(BaseModel):
    risk_flags: list[str] = []
    summary: str | None = None
    risk_score: int | None = None  # 1–10

class PipelineResult(BaseModel):
    filename: str
    lease: LeaseData
    risk: RiskAnalysis

class RentRollRow(BaseModel):
    filename: str
    tenant_name: str | None
    property_address: str | None
    bedrooms: int | None
    sqft: float | None
    rent_per_sqft: float | None
    base_rent_monthly: float | None
    lease_start: date | None
    lease_end: date | None
    rent_escalation_pct: float | None
    personal_guarantee: bool | None
    risk_score: int | None
    risk_flags: list[str] = []

class RentRollReport(BaseModel):
    rows: list[RentRollRow]
    inconsistencies: list[str]
    opportunities: list[str]

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
