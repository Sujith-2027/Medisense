import json
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel

from rag.pipeline import run_rag_pipeline
from rag.generator import explain_medicine
from safety.severity import classify_severity
from report import create_report
from db.database import save_report, get_by_id, get_dashboard_stats

router = APIRouter()

class SymptomRequest(BaseModel):
    name: str
    age: int | None = None
    gender: str | None = None
    symptoms: str
    medical_history: str = ""
    allergies: str = ""

class MedicineRequest(BaseModel):
    medicine: str

@router.post("/analyze")
def analyze(req: SymptomRequest):
    severity_level, severity_color = classify_severity(req.symptoms)
    result = run_rag_pipeline(
        symptoms=req.symptoms,
        name=req.name,
        age=req.age,
        gender=req.gender,
        medical_history=req.medical_history,
        allergies=req.allergies,
    )
    report_id, _ = create_report({
        "name": req.name, "age": req.age, "gender": req.gender,
        "symptoms": req.symptoms, "severity": severity_level,
        "medical_history": req.medical_history, "allergies": req.allergies,
        **result,
    })
    save_report(report_id, req.name, req.symptoms, severity_level,
                json.dumps(result), req.medical_history, req.allergies)
    return {"report_id": report_id, "severity": severity_level, "severity_color": severity_color, **result}

@router.get("/report/{report_id}")
def download_report(report_id: str):
    path = f"reports/{report_id}.pdf"
    return FileResponse(path, media_type="application/pdf", filename=f"MediSense_Report_{report_id}.pdf")

@router.get("/fetch-report/{report_id}")
def fetch_report_data(report_id: str):
    # Try both upper and as-is
    row = get_by_id(report_id.upper()) or get_by_id(report_id)
    if not row:
        raise HTTPException(status_code=404, detail="Report not found")
    result = json.loads(row[4]) if row[4] else {}
    return {
        "report_id": row[0],
        "name": row[1],
        "symptoms": row[2],
        "severity": row[3],
        "medical_history": row[5] if len(row) > 5 else "",
        "allergies": row[6] if len(row) > 6 else "",
        "created_at": row[7] if len(row) > 7 else "",
        **result,
    }

@router.post("/explain-medicine")
def medicine_explainer(req: MedicineRequest):
    return {"medicine": req.medicine, "explanation": explain_medicine(req.medicine)}

@router.get("/dashboard-stats")
def dashboard_stats():
    return get_dashboard_stats()