from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from routes.symptom import router as symptom_router
from routes.followup import router as followup_router
from db.database import init_db

app = FastAPI(title="MediSense AI", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(symptom_router, prefix="/api")
app.include_router(followup_router, prefix="/api")

@app.get("/health")
def health():
    return {"status": "ok"}

init_db()

# Must be last — serves frontend/
app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")