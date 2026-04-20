# main.py — FastAPI app, routes, serves frontend

import asyncio
from typing import List
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import PlainTextResponse

from database import init_db
from pipeline import run_pipeline
from rent_roll import build_rent_roll, to_csv
from models import RentRollReport

app = FastAPI(title="Lease Intelligence Pipeline")
_last_report: RentRollReport | None = None

@app.on_event("startup")
def startup():
    init_db()

@app.post("/api/rent-roll", response_model=RentRollReport)
async def upload_leases(files: List[UploadFile] = File(...)):
    global _last_report
    contents = await asyncio.gather(*[f.read() for f in files])
    results = await asyncio.gather(*[run_pipeline(c, f.filename) for c, f in zip(contents, files)])
    _last_report = build_rent_roll(list(results))
    return _last_report

@app.get("/api/rent-roll/csv")
def export_csv():
    if not _last_report:
        raise HTTPException(status_code=404, detail="No report generated yet")
    return PlainTextResponse(to_csv(_last_report), media_type="text/csv", headers={"Content-Disposition": "attachment; filename=rent_roll.csv"})

app.mount("/", StaticFiles(directory="static", html=True), name="static")
