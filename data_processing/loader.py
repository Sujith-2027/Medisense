import json
import csv
import os

RAW_DATA_DIR = "data/raw"

def load_json_dataset(filepath: str) -> list[dict]:
    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)
    print(f"Loaded {len(data)} records from {filepath}")
    return data

def load_csv_dataset(filepath: str) -> list[dict]:
    records = []
    with open(filepath, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            records.append(dict(row))
    print(f"Loaded {len(records)} records from {filepath}")
    return records

def load_all_datasets() -> list[dict]:
    all_records = []
    for fname in os.listdir(RAW_DATA_DIR):
        fpath = os.path.join(RAW_DATA_DIR, fname)
        if fname.endswith(".json"):
            all_records.extend(load_json_dataset(fpath))
        elif fname.endswith(".csv"):
            all_records.extend(load_csv_dataset(fpath))
    print(f"Total records loaded: {len(all_records)}")
    return all_records