# models.py — Pydantic schemas + SQLAlchemy ORM models

# --- Pydantic (API / validation) ---

# class LeaseData(BaseModel):
#     tenant_name, property_address, lease_start, lease_end, term_months
#     base_rent_monthly, rent_escalation_pct, security_deposit
#     personal_guarantee: bool
#     options: list[str]
#     key_clauses: list[str]

# class RiskAnalysis(BaseModel):
#     risk_flags: list[str]
#     summary: str
#     risk_score: int  # 1–10

# class PipelineResult(BaseModel):
#     lease: LeaseData
#     risk: RiskAnalysis

# --- SQLAlchemy (DB) ---

# class LeaseRecord(Base):
#     # stores PipelineResult as JSON + metadata (filename, created_at)
