from fastapi import APIRouter
from pydantic import BaseModel
from rag.generator import generate_followup

router = APIRouter()

class FollowupRequest(BaseModel):
    report_id: str
    name: str
    original_symptoms: str
    question: str
    chat_history: list[dict] = []
    user_location: str = "Mumbai"

@router.post("/followup")
def followup(req: FollowupRequest):
    answer, updated_history = generate_followup(
        original_symptoms=req.original_symptoms,
        question=req.question,
        chat_history=req.chat_history,
        name=req.name,
        user_location=req.user_location,
    )
    return {"answer": answer, "chat_history": updated_history}