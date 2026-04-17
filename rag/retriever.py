import pickle
import os
from config import CHUNKS_PATH, TOP_K

_chunks: list[dict] = []

def _load_chunks():
    global _chunks
    if _chunks:
        return
    if not os.path.exists(CHUNKS_PATH):
        raise FileNotFoundError(
            f"'{CHUNKS_PATH}' not found. Run `python build_index.py` first."
        )
    with open(CHUNKS_PATH, "rb") as f:
        _chunks = pickle.load(f)
    print(f"RAG: loaded {len(_chunks)} chunks from {CHUNKS_PATH}")

def retrieve(query: str, k: int = TOP_K) -> list[dict]:
    """
    Score each chunk by how many query words appear in it.
    Returns the top-k chunks.
    """
    _load_chunks()
    query_words = set(query.lower().split())

    scored = []
    for chunk in _chunks:
        text_lower = chunk["text"].lower()
        # Also boost by symptom keyword matches in metadata
        meta_symptoms = " ".join(chunk.get("metadata", {}).get("symptoms", []))
        combined = text_lower + " " + meta_symptoms.lower()
        score = sum(1 for w in query_words if w in combined)
        scored.append((score, chunk))

    scored.sort(key=lambda x: x[0], reverse=True)
    return [c for _, c in scored[:k]]

def format_context(chunks: list[dict]) -> str:
    """Join retrieved chunks into a single context string for the LLM."""
    parts = []
    for c in chunks:
        condition = c.get("metadata", {}).get("condition", "")
        header = f"[{condition}] " if condition else ""
        parts.append(header + c["text"])
    return "\n\n---\n\n".join(parts)