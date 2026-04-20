# pipeline.py — core processing pipeline

import os
import fitz  # PyMuPDF
import anthropic
from dotenv import load_dotenv
from pathlib import Path
from models import LeaseData, RiskAnalysis, PipelineResult

load_dotenv(Path(__file__).parent / ".env")
client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

def extract_text_from_pdf(file_bytes: bytes) -> str:
    doc = fitz.open(stream=file_bytes, filetype="pdf")
    return "\n".join(page.get_text() for page in doc)

EXTRACTION_SYSTEM_PROMPT = "You are a lease abstraction expert. Extract structured data from the lease text provided. Use null for any field you cannot find."

LEASE_EXTRACTION_TOOL = {
    "name": "extract_lease_data",
    "description": "Extract structured lease data from raw text",
    "input_schema": {
        "type": "object",
        "properties": {
            "tenant_name":          {"type": ["string", "null"]},
            "property_address":     {"type": ["string", "null"]},
            "lease_start":          {"type": ["string", "null"], "description": "YYYY-MM-DD"},
            "lease_end":            {"type": ["string", "null"], "description": "YYYY-MM-DD"},
            "term_months":          {"type": ["integer", "null"]},
            "base_rent_monthly":    {"type": ["number", "null"]},
            "rent_escalation_pct":  {"type": ["number", "null"]},
            "security_deposit":     {"type": ["number", "null"]},
            "personal_guarantee":   {"type": ["boolean", "null"]},
            "sqft":                 {"type": ["number", "null"]},
            "options":              {"type": "array", "items": {"type": "string"}},
            "key_clauses":          {"type": "array", "items": {"type": "string"}},
        },
    },
}

async def extract_structured_data(raw_text: str) -> LeaseData:
    response = client.messages.create(
        model="claude-haiku-4-5",
        max_tokens=1024,
        system=[{"type": "text", "text": EXTRACTION_SYSTEM_PROMPT, "cache_control": {"type": "ephemeral"}}],
        tools=[LEASE_EXTRACTION_TOOL],
        tool_choice={"type": "tool", "name": "extract_lease_data"},
        messages=[{"role": "user", "content": raw_text}],
    )
    tool_input = response.content[0].input
    return LeaseData(**tool_input)

RISK_SYSTEM_PROMPT = "You are a commercial real estate attorney advising a landlord. Analyze the structured lease data and identify risks to the landlord — such as missing guarantees, no escalation, below-market rent, short term, weak security deposit, or problematic clauses."

RISK_ANALYSIS_TOOL = {
    "name": "analyze_lease_risk",
    "description": "Identify risk flags and produce a plain-English summary with a risk score",
    "input_schema": {
        "type": "object",
        "properties": {
            "risk_flags": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Short, specific risk flags (e.g. 'No rent cap on escalation')",
            },
            "summary": {
                "type": "string",
                "description": "2-3 sentence plain-English summary of the lease risk profile",
            },
            "risk_score": {
                "type": "integer",
                "description": "Overall risk score from 1 (low) to 10 (high)",
                "minimum": 1,
                "maximum": 10,
            },
        },
        "required": ["risk_flags", "summary", "risk_score"],
    },
}

async def extract_risk_flags(lease_data: LeaseData) -> RiskAnalysis:
    response = client.messages.create(
        model="claude-haiku-4-5",
        max_tokens=1024,
        system=[{"type": "text", "text": RISK_SYSTEM_PROMPT, "cache_control": {"type": "ephemeral"}}],
        tools=[RISK_ANALYSIS_TOOL],
        tool_choice={"type": "tool", "name": "analyze_lease_risk"},
        messages=[{"role": "user", "content": lease_data.model_dump_json()}],
    )
    tool_input = response.content[0].input
    return RiskAnalysis(**tool_input)

async def run_pipeline(file_bytes: bytes, filename: str) -> PipelineResult:
    raw_text = extract_text_from_pdf(file_bytes)
    lease_data = await extract_structured_data(raw_text)
    risk = await extract_risk_flags(lease_data)
    return PipelineResult(filename=filename, lease=lease_data, risk=risk)
