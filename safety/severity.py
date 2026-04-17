HIGH_RISK_PHRASES = [
    "chest pain", "chest tightness", "chest pressure", "heart attack", "cardiac arrest",
    "crushing chest pain", "chest pain radiating to arm", "chest pain with sweating",
    "pulmonary embolism", "blood clot in lung", "heart failure",
    "can't breathe", "cannot breathe", "difficulty breathing", "severe shortness of breath",
    "breathing stopped", "choking", "suffocating", "wheezing severely",
    "respiratory failure", "gasping for air", "blue lips", "blue fingernails",
    "stroke", "seizure", "convulsion", "unconscious", "unresponsive",
    "sudden confusion", "sudden weakness one side", "facial drooping", "slurred speech",
    "worst headache of my life", "sudden severe headache", "loss of consciousness",
    "paralysis", "brain bleed", "meningitis",
    "coughing blood", "vomiting blood", "severe bleeding", "hemorrhage",
    "anaphylaxis", "throat swelling", "tongue swelling", "severe allergic reaction",
    "poisoning", "overdose", "drug overdose", "attempted suicide",
    "severe burns", "electric shock", "carbon monoxide poisoning",
    "diabetic coma", "heatstroke", "hypothermia severe",
]

MEDIUM_RISK_PHRASES = [
    "high fever", "fever for 3 days", "fever for 4 days", "fever 39", "fever 40",
    "fever with rash", "fever with stiff neck", "fever with confusion",
    "vomiting repeatedly", "diarrhea for 2 days", "severe abdominal pain",
    "can't keep water down", "dehydration", "appendix pain",
    "cough for 2 weeks", "wheezing moderate", "difficulty swallowing",
    "sore throat severe", "pneumonia symptoms",
    "burning urination", "blood in urine", "kidney pain", "flank pain",
    "severe headache", "migraine severe", "vision changes sudden", "blurred vision",
    "eye pain severe", "ear pain severe", "hearing loss sudden", "dizziness severe",
    "panic attack", "suicidal thoughts", "hallucination", "psychosis",
    "rash spreading rapidly", "infected wound", "abscess", "cellulitis",
    "joint pain severe", "back pain severe", "can't walk",
    "blood pressure very high", "blood sugar very high", "jaundice",
    "yellowing skin", "night sweats with fever", "unexplained weight loss",
    "pregnancy bleeding", "contractions early", "miscarriage symptoms",
]

MILD_PHRASES = [
    "runny nose", "stuffy nose", "sneezing", "mild cough", "dry cough",
    "sore throat mild", "mild fever", "low grade fever", "cold symptoms",
    "nausea mild", "indigestion", "heartburn", "acid reflux", "gas",
    "bloating mild", "loose stool", "mild constipation", "stomach ache mild",
    "itching mild", "dry skin", "mild rash", "insect bite", "sunburn mild",
    "acne", "minor cut", "bruise",
    "fatigue", "tiredness", "mild dizziness", "mild back pain",
    "muscle soreness", "mild joint pain", "stiff neck mild",
    "mild anxiety", "stress", "insomnia", "difficulty sleeping",
    "seasonal allergy", "hay fever", "mild allergic reaction",
    "frequent urination mild", "mild period pain", "morning sickness mild",
]

def classify_severity(symptoms: str) -> tuple[str, str]:
    """
    Returns (level, color) where level is 'high', 'medium', or 'mild'.
    Color is a hex code for UI display.
    """
    s = symptoms.lower()

    for phrase in HIGH_RISK_PHRASES:
        if phrase in s:
            return "high", "#ef4444"

    for phrase in MEDIUM_RISK_PHRASES:
        if phrase in s:
            return "medium", "#f97316"

    for phrase in MILD_PHRASES:
        if phrase in s:
            return "mild", "#22c55e"

    return "medium", "#f97316"  # unknown → treat as medium (safer)