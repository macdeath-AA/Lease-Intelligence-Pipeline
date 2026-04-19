# pipeline.py — core processing pipeline

# def extract_text_from_pdf(file_bytes: bytes) -> str:
#     ...

# async def extract_structured_data(raw_text: str) -> LeaseData:
#     # Claude call 1: raw text → structured JSON

# async def extract_risk_flags(lease_data: LeaseData) -> RiskAnalysis:
#     # Claude call 2: structured data → risk flags + summary

# async def run_pipeline(file_bytes: bytes) -> PipelineResult:
#     # orchestrates all three steps above
