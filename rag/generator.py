import os
import json
import re
from groq import Groq
from dotenv import load_dotenv
from config import GROQ_MODEL

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

SYSTEM_PROMPT = """You are a caring, professional medical assistant.
You MUST respond with ONLY a raw JSON object. No markdown fences. No text before or after. Start with { end with }

{
  "possible_conditions": ["Exact Condition Name 1", "Exact Condition Name 2", "Exact Condition Name 3"],
  "explanation": "Write 4-5 detailed sentences addressing the patient by name. Explain WHY their symptoms suggest each condition. Use **term** to bold key medical words. Be thorough and personal.",
  "advice": ["Specific actionable advice point 1 in full sentence", "Specific actionable advice point 2", "Specific actionable advice point 3", "Specific actionable advice point 4"],
  "otc": ["Medicine Name (dosage and use)", "Medicine Name (dosage and use)", "Medicine Name (dosage and use)"],
  "warning": ["Specific warning if red flags exist — be explicit about what to watch for"]
}

RULES:
- possible_conditions: exactly 3, real medical names, NO asterisks or markdown in names
- explanation: minimum 4 sentences, detailed, personal, reference their history/age/gender
- advice: minimum 4 points, each a complete sentence
- otc: exactly 3 medicines with dosage
- warning: at least 1 specific warning, or empty list [] if truly no concerns"""


def _extract_json(text: str) -> dict:
    text = text.strip()
    # Strip markdown fences
    text = re.sub(r"^```(?:json)?", "", text, flags=re.MULTILINE).strip()
    text = re.sub(r"```$", "", text, flags=re.MULTILINE).strip()
    # Direct parse
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass
    # Find outermost {}
    start = text.find("{")
    if start != -1:
        depth = 0
        for i, ch in enumerate(text[start:], start):
            if ch == "{": depth += 1
            elif ch == "}":
                depth -= 1
                if depth == 0:
                    candidate = text[start:i+1]
                    # Fix trailing commas
                    candidate = re.sub(r",\s*([}\]])", r"\1", candidate)
                    try:
                        return json.loads(candidate)
                    except:
                        break
    return None


def _clean_condition_name(name: str) -> str:
    """Remove any markdown bold markers from condition names."""
    return re.sub(r"\*\*(.+?)\*\*", r"\1", name).strip()


def generate_response(
    symptoms: str,
    context: str,
    name: str = "Patient",
    age: int = None,
    gender: str = None,
    medical_history: str = "",
    allergies: str = "",
) -> dict:
    history_line = f"Past Medical History: {medical_history}" if medical_history else ""
    allergy_line = f"Known Allergies: {allergies} — NEVER suggest these" if allergies else ""

    user_content = f"""Patient: {name}
{"Age: " + str(age) if age else ""}{"  Gender: " + gender if gender else ""}
{history_line}
{allergy_line}
Symptoms: {symptoms}

Medical Context:
{context}

Write a detailed, personalized JSON response. Explanation must be 4-5 sentences minimum.
Condition names must be plain text — no asterisks.
Start response with {{ end with }}"""

    response = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_content},
        ],
        temperature=0.2,
        max_tokens=1200,
    )

    raw = response.choices[0].message.content.strip()
    result = _extract_json(raw)

    if result and isinstance(result, dict) and "possible_conditions" in result:
        # Clean condition names of any markdown
        result["possible_conditions"] = [_clean_condition_name(c) for c in result.get("possible_conditions", [])]
        # Ensure minimum counts
        while len(result.get("otc", [])) < 3:
            defaults = ["Paracetamol 500mg (every 6 hrs for fever/pain)", "ORS Solution (for hydration)", "Vitamin C 500mg (immune support)"]
            result["otc"] = (result.get("otc") or []) + defaults
        result["otc"] = result["otc"][:3]
        while len(result.get("advice", [])) < 4:
            result["advice"] = (result.get("advice") or []) + [
                "Rest adequately and avoid strenuous activity until symptoms improve.",
                "Stay well hydrated — drink at least 8-10 glasses of water daily.",
                "Monitor your temperature every 4-6 hours and note any changes.",
                "Consult a doctor if symptoms persist beyond 48 hours or worsen suddenly.",
            ]
        if not result.get("warning"):
            result["warning"] = ["Monitor closely and seek immediate medical attention if symptoms worsen rapidly."]
        return result

    # Safe fallback
    return {
        "possible_conditions": ["Viral Infection", "Bacterial Illness", "General Fatigue Syndrome"],
        "explanation": f"{name}, based on your symptoms, you may be experiencing a common viral or bacterial infection. Your symptoms suggest inflammation or infection in the body that needs attention. Given your medical history, it is important to monitor these symptoms carefully and not ignore any worsening. I strongly recommend consulting a qualified doctor for a proper examination and diagnosis.",
        "advice": [
            "Rest at home and avoid any strenuous physical activity.",
            "Drink plenty of fluids — water, coconut water, or electrolyte drinks.",
            "Monitor your temperature every 4-6 hours and keep a record.",
            "See a doctor immediately if symptoms worsen or new symptoms appear.",
        ],
        "otc": ["Paracetamol 500mg (every 6 hrs for fever/pain)", "ORS Solution (for hydration)", "Vitamin C 500mg (immune support)"],
        "warning": ["If you experience difficulty breathing, severe chest pain, or loss of consciousness, call emergency services immediately."],
    }


def explain_medicine(medicine_name: str) -> str:
    prompt = f"""You are a friendly pharmacist. Explain "{medicine_name}" in plain language.
Cover: (1) primary use, (2) how it works, (3) typical OTC dosage, (4) important cautions.
3-4 sentences. No markdown. No asterisks."""
    response = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
    )
    return response.choices[0].message.content.strip()


def generate_followup(
    original_symptoms: str,
    question: str,
    chat_history: list[dict],
    name: str = "Patient",
    user_location: str = "Mumbai",
) -> tuple[str, list[dict]]:
    history_text = ""
    for msg in chat_history[-6:]:
        role = name if msg["role"] == "user" else "MediSense AI"
        history_text += f"{role}: {msg['content']}\n"

    # Detect location/hospital queries
    location_query = any(w in question.lower() for w in ["nearby", "hospital", "clinic", "doctor near", "where to go", "which hospital"])

    location_hint = ""
    if location_query:
        location_hint = f"""
The patient is likely located near {user_location}, India.
For hospital/clinic questions, suggest specific real hospital names in areas like:
Bhandup, Mulund, Thane, Ghatkopar, Powai, Vikhroli, Kurla (Mumbai suburbs).
Give top 3-5 real hospitals with their area. Examples you can mention:
- Fortis Hospital Mulund
- Jupiter Hospital Thane
- Hiranandani Hospital Powai
- Kokilaben Dhirubhai Ambani Hospital (Andheri)
- Rajawadi Hospital Ghatkopar
- ESIS Hospital Bhandup
- Bethany Hospital Thane
Be clear these are suggestions to search/call, not guaranteed availability."""

    prompt = f"""You are MediSense AI — a medical information assistant (NOT a booking system).
Patient: {name}
Original symptoms: {original_symptoms}
{location_hint}

Conversation:
{history_text}

Question: {question}

You CAN:
- Explain conditions and their types in detail
- Name specific real hospitals/clinics in the patient's area (top 3-5 with location)
- Explain medicines
- Give health/lifestyle advice
- Recommend specialist type to see

You CANNOT:
- Book appointments
- Access live availability
- Prescribe medications
- Give definitive diagnosis

Be warm, specific, and helpful. Write plain sentences — no markdown asterisks."""

    response = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.5,
    )
    answer = response.choices[0].message.content.strip()
    answer = re.sub(r'\*\*(.+?)\*\*', r'\1', answer)

    updated_history = chat_history + [
        {"role": "user", "content": question},
        {"role": "assistant", "content": answer},
    ]
    return answer, updated_history