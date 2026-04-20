# models.py — Pydantic schemas + SQLAlchemy ORM models

from datetime import date
from pydantic import BaseModel, model_validator

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
    sqft: float | None = None
    options: list[str] = []
    key_clauses: list[str] = []

    @model_validator(mode='before')
    @classmethod
    def coerce_invalid_to_none(cls, values):
        from datetime import date as _date
        import re
        numeric = {'term_months', 'base_rent_monthly', 'rent_escalation_pct', 'security_deposit', 'sqft'}
        dates   = {'lease_start', 'lease_end'}
        for field in numeric:
            if isinstance(values.get(field), str):
                values[field] = None
        for field in dates:
            val = values.get(field)
            if isinstance(val, str) and not re.match(r'^\d{4}-\d{2}-\d{2}$', val):
                values[field] = None
        return values

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
