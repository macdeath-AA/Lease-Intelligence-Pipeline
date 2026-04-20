# main.py — FastAPI app, routes, serves frontend

import asyncio
from typing import List
from fastapi import FastAPI, UploadFile, File
from fastapi.staticfiles import StaticFiles
from fastapi.responses import PlainTextResponse

from database import init_db
from pipeline import run_pipeline
from rent_roll import build_rent_roll, to_csv
from models import RentRollReport

app = FastAPI(title="Lease Intelligence Pipeline")

@app.on_event("startup")
def startup():
    init_db()

@app.post("/api/rent-roll", response_model=RentRollReport)
async def upload_leases(files: List[UploadFile] = File(...)):
    contents = await asyncio.gather(*[f.read() for f in files])
    results = await asyncio.gather(*[run_pipeline(c, f.filename) for c, f in zip(contents, files)])
    return build_rent_roll(list(results))

@app.post("/api/rent-roll/csv")
async def upload_leases_csv(files: List[UploadFile] = File(...)):
    contents = await asyncio.gather(*[f.read() for f in files])
    results = await asyncio.gather(*[run_pipeline(c, f.filename) for c, f in zip(contents, files)])
    report = build_rent_roll(list(results))
    return PlainTextResponse(to_csv(report), media_type="text/csv", headers={"Content-Disposition": "attachment; filename=rent_roll.csv"})

app.mount("/", StaticFiles(directory="static", html=True), name="static")
