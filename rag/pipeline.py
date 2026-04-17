from rag.retriever import retrieve, format_context
from rag.generator import generate_response
from safety.guardrails import filter_response

def run_rag_pipeline(
    symptoms: str,
    name: str = "Patient",
    age: int = None,
    gender: str = None,
    medical_history: str = "",
    allergies: str = "",
) -> dict:
    chunks  = retrieve(symptoms)
    context = format_context(chunks)
    result  = generate_response(symptoms, context, name, age, gender, medical_history, allergies)
    result  = filter_response(result)
    return result