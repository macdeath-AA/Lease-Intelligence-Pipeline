# Lease Intelligence Pipeline

A web-based tool for commercial real estate professionals to analyze lease PDFs using AI. Upload lease documents and get structured rent rolls, risk assessments, inconsistency detection, and portfolio-wide opportunity analysis.

## What It Does

- Extracts structured lease data from PDFs (tenant, rent, escalations, guarantees, options, key clauses)
- Scores landlord risk 1–10 using a commercial real estate attorney perspective
- Compiles a rent roll across all uploaded leases
- Flags inconsistencies (missing fields, duplicate tenants, overlapping dates)
- Surfaces opportunities (expiring leases, below-market units, missing guarantees)
- Exports results to CSV

## Tech Stack

- **Backend**: FastAPI, SQLAlchemy + SQLite, PyMuPDF
- **AI**: Anthropic Claude (Haiku 4.5) with tool use and prompt caching
- **Frontend**: Vanilla JS, Tailwind CSS, Chart.js

## Setup

**Prerequisites:** Python 3.9+, Anthropic API key

```bash
# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Add your key to .env:
# ANTHROPIC_API_KEY=sk-ant-...

# Run the app
uvicorn main:app --reload
```

Open `http://localhost:8000` in your browser.

```

## Usage

1. Open the app and drag-and-drop one or more lease PDFs
2. The pipeline extracts data and runs risk analysis via Claude
3. View the rent roll table, risk chart, inconsistencies, and opportunities
4. Download a CSV export for Excel or accounting tools

## Key Features

- Batch processing of multiple PDFs
- Prompt caching for faster, cheaper repeated requests
- Portfolio-wide analytics (rent/sqft comparison, expiration alerts)
- SQLite persistence for audit trail
```
