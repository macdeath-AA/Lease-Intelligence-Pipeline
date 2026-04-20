# rent_roll.py — compile rent roll, flag inconsistencies, surface opportunities

import csv
import io
from datetime import date
from models import PipelineResult, RentRollRow, RentRollReport

def build_rent_roll(results: list[PipelineResult]) -> RentRollReport:
    rows = _compile_rows(results)
    inconsistencies = _flag_inconsistencies(rows, results)
    opportunities = _find_opportunities(rows)
    return RentRollReport(rows=rows, inconsistencies=inconsistencies, opportunities=opportunities)

def to_csv(report: RentRollReport) -> str:
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=[
        "filename", "tenant_name", "property_address", "sqft",
        "rent_per_sqft", "base_rent_monthly", "lease_start", "lease_end",
        "rent_escalation_pct", "personal_guarantee", "risk_score",
    ])
    writer.writeheader()
    for row in report.rows:
        writer.writerow(row.model_dump())
    return output.getvalue()

def _compile_rows(results: list[PipelineResult]) -> list[RentRollRow]:
    rows = []
    for r in results:
        l = r.lease
        rent_per_sqft = (
            round(l.base_rent_monthly / l.sqft, 2)
            if l.base_rent_monthly and l.sqft else None
        )
        rows.append(RentRollRow(
            filename=r.filename,
            tenant_name=l.tenant_name,
            property_address=l.property_address,
            bedrooms=l.bedrooms,
            sqft=l.sqft,
            rent_per_sqft=rent_per_sqft,
            base_rent_monthly=l.base_rent_monthly,
            lease_start=l.lease_start,
            lease_end=l.lease_end,
            rent_escalation_pct=l.rent_escalation_pct,
            personal_guarantee=l.personal_guarantee,
            risk_score=r.risk.risk_score,
            risk_flags=r.risk.risk_flags,
        ))
    return rows

def _flag_inconsistencies(rows: list[RentRollRow], results: list[PipelineResult]) -> list[str]:
    flags = []

    # Missing critical fields
    for row in rows:
        missing = [f for f, v in {
            "tenant_name": row.tenant_name,
            "base_rent_monthly": row.base_rent_monthly,
            "lease_start": row.lease_start,
            "lease_end": row.lease_end,
        }.items() if v is None]
        if missing:
            flags.append(f"{row.filename}: missing {', '.join(missing)}")

    # Duplicate tenant names across leases
    names = [r.tenant_name for r in rows if r.tenant_name]
    seen = set()
    for name in names:
        if names.count(name) > 1 and name not in seen:
            flags.append(f"Duplicate tenant name across leases: '{name}'")
            seen.add(name)

    # Overlapping lease dates for same address
    addressed = [r for r in rows if r.property_address and r.lease_start and r.lease_end]
    for i, a in enumerate(addressed):
        for b in addressed[i+1:]:
            if a.property_address == b.property_address:
                if a.lease_start <= b.lease_end and b.lease_start <= a.lease_end:
                    flags.append(f"Overlapping lease dates at '{a.property_address}': {a.filename} and {b.filename}")

    # Lease end before lease start
    for row in rows:
        if row.lease_start and row.lease_end and row.lease_end <= row.lease_start:
            flags.append(f"{row.filename}: lease_end is before or equal to lease_start")

    return flags

def _find_opportunities(rows: list[RentRollRow]) -> list[str]:
    opportunities = []
    today = date.today()

    # Expiring within 90 days
    for row in rows:
        if row.lease_end:
            days_left = (row.lease_end - today).days
            if 0 < days_left <= 90:
                opportunities.append(f"{row.tenant_name or row.filename}: lease expires in {days_left} days — renegotiation window")

    # No escalation clause
    for row in rows:
        if row.rent_escalation_pct is None or row.rent_escalation_pct == 0:
            opportunities.append(f"{row.tenant_name or row.filename}: no rent escalation — add clause on renewal")

    # No personal guarantee
    for row in rows:
        if row.personal_guarantee is False:
            opportunities.append(f"{row.tenant_name or row.filename}: no personal guarantee — secure on renewal")

    # Below-portfolio $/sqft
    psf_values = [r.rent_per_sqft for r in rows if r.rent_per_sqft]
    if psf_values:
        avg_psf = sum(psf_values) / len(psf_values)
        for row in rows:
            if row.rent_per_sqft and row.rent_per_sqft < avg_psf * 0.85:
                opportunities.append(f"{row.tenant_name or row.filename}: rent ${row.rent_per_sqft}/sqft is >15% below portfolio avg (${avg_psf:.2f}) — underpriced unit")

    return opportunities
