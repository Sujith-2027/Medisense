from config import CHUNK_SIZE, CHUNK_OVERLAP

def chunk_text(text: str, metadata: dict = {}) -> list[dict]:
    """Split text into overlapping chunks."""
    chunks = []
    start = 0
    while start < len(text):
        end = start + CHUNK_SIZE
        chunk = text[start:end]
        chunks.append({"text": chunk, "metadata": metadata})
        start += CHUNK_SIZE - CHUNK_OVERLAP
    return chunks

def chunk_records(records: list[dict]) -> list[dict]:
    """
    Convert medical records into searchable chunks.
    Each record gets a rich text blob combining all its fields.
    """
    all_chunks = []
    for rec in records:
        description = rec.get("description", "")
        symptoms = rec.get("symptoms", [])
        condition = rec.get("condition", "")
        source = rec.get("source", "")

        # Build a rich text blob for better keyword matching
        symptoms_str = ", ".join(symptoms) if isinstance(symptoms, list) else symptoms
        full_text = (
            f"Condition: {condition}. "
            f"Symptoms: {symptoms_str}. "
            f"{description}"
        )

        meta = {
            "condition": condition,
            "source": source,
            "symptoms": symptoms,
        }
        all_chunks.extend(chunk_text(full_text, metadata=meta))

    print(f"Total chunks created: {len(all_chunks)}")
    return all_chunks