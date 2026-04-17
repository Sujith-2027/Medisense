"""
Run this once before starting the server:
    python build_index.py

Reads all JSON/CSV files from data/raw/, cleans and chunks them,
then saves db/chunks.pkl for the RAG retriever.
"""
import os
import pickle

from data_processing.loader import load_all_datasets
from data_processing.cleaner import clean_dataset
from data_processing.chunker import chunk_records

def main():
    print("=" * 50)
    print("Building RAG knowledge index")
    print("=" * 50)

    os.makedirs("db", exist_ok=True)

    records = load_all_datasets()
    cleaned = clean_dataset(records)
    chunks  = chunk_records(cleaned)

    with open("db/chunks.pkl", "wb") as f:
        pickle.dump(chunks, f)

    print(f"\n✅ db/chunks.pkl saved — {len(chunks)} chunks ready.")

if __name__ == "__main__":
    main()