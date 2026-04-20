# main.py — FastAPI app, routes, serves frontend

from fastapi import FastAPI, UploadFile, File, Depends, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from database import init_db, get_db, save_lease, fetch_lease, fetch_all_leases
from pipeline import run_pipeline
from models import PipelineResult

app = FastAPI(title="Lease Intelligence Pipeline")

@app.on_event("startup")
def startup():
    init_db()

@app.post("/api/leases", response_model=PipelineResult)
async def upload_lease(file: UploadFile = File(...), db: Session = Depends(get_db)):
    contents = await file.read()
    result = await run_pipeline(contents)
    save_lease(db, result, file.filename)
    return result

@app.get("/api/leases/{lease_id}")
def get_lease(lease_id: int, db: Session = Depends(get_db)):
    record = fetch_lease(db, lease_id)
    if not record:
        raise HTTPException(status_code=404, detail="Lease not found")
    return {"id": record.id, "filename": record.filename, "lease": record.lease_data, "risk": record.risk_data, "created_at": record.created_at}

@app.get("/api/leases")
def list_leases(db: Session = Depends(get_db)):
    records = fetch_all_leases(db)
    return [{"id": r.id, "filename": r.filename, "risk_score": r.risk_data.get("risk_score"), "created_at": r.created_at} for r in records]

app.mount("/", StaticFiles(directory="static", html=True), name="static")
