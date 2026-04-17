import re

def clean_text(text: str) -> str:
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"http\S+", "", text)
    text = re.sub(r"[^\w\s.,;:?!()\-]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text

def clean_record(record: dict) -> dict:
    cleaned = {}
    for key, val in record.items():
        if isinstance(val, str):
            cleaned[key] = clean_text(val)
        elif isinstance(val, list):
            cleaned[key] = [clean_text(v) if isinstance(v, str) else v for v in val]
        else:
            cleaned[key] = val
    return cleaned

def clean_dataset(records: list[dict]) -> list[dict]:
    cleaned = [clean_record(r) for r in records]
    cleaned = [r for r in cleaned if r.get("description")]
    print(f"Cleaned dataset: {len(cleaned)} records")
    return cleaned