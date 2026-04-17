import os
from dotenv import load_dotenv

load_dotenv()

# ── LLM ──────────────────────────────────────────────
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL   = "llama-3.1-8b-instant"

# ── RAG ──────────────────────────────────────────────
CHUNKS_PATH  = "db/chunks.pkl"
TOP_K        = 3
CHUNK_SIZE   = 300
CHUNK_OVERLAP = 50

# ── Safety ───────────────────────────────────────────
BLOCKED_DRUGS = [
    "morphine", "oxycodone", "fentanyl", "codeine", "tramadol",
    "diazepam", "alprazolam", "lorazepam", "clonazepam",
    "amphetamine", "methylphenidate", "ketamine", "methadone",
]