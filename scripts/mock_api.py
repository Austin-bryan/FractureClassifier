# This is where the mock API will be until we have the actual API ready.
# This will allow us to ensure that our frontend can communicate with the backend.

import pandas as pd
import numpy as np
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from collections import Counter
from pathlib import Path


app = FastAPI(title="mock_api")
df = pd.read_csv('./data/dataset.csv')

app.add_middleware( # Allows CORS to connect frontend and backend during development
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Precompute class counts once
all_codes = []
for entry in df['ao_classification'].dropna():
    all_codes.extend([c.strip() for c in str(entry).split(';') if c.strip()])

class_counts = Counter(all_codes)
max_class_count = max(class_counts.values()) if class_counts else 1

# Root endpoint to verify API is running
@app.get("/")
def root():
    return {"message": "FrACT API is running!"}

# Health check for API
@app.get("/health")
def health():
    return {"status": "ok"}

# Endpoint to list all classes and their counts in the dataset
@app.get("/classes")
def list_classes():
    codes = []
    for entry in df['ao_classification'].dropna():
        codes.extend([c.strip() for c in entry.split(';') if c.strip()])
    counts = Counter(codes)
    items = sorted(counts.items(), key=lambda kv: kv[1], reverse=True)
    return {"classes": [{"code": c, "count": n} for c, n in items]}

# Count how many codes per image
@app.get("/multiplicity")
def multiplicity():
    mult = df['ao_classification'].fillna('').apply(
        lambda x: len([c for c in x.split(';') if c.strip()])
    ).value_counts().sort_index().to_dict()
    return {"multiplicity": mult}

# Look up metadata from the dataset for a given filestem
@app.get("/image/{filestem}")
def image_metadata(filestem: str):
    row = df[df["filestem"] == filestem] # Look up the row in the dataset that matches the filestem
    if row.empty: # If a row is not found, return a 404 error
        raise HTTPException(status_code=404, detail="Image wasn't found")
    record = row.iloc[0].replace([np.inf, -np.inf], np.nan)
    
    # Convert row to dict and replace NaN with None for JSON serialization
    clean_data = record.astype(object).where(pd.notna(record), None).to_dict()
    
    return clean_data

# Predict endpoint that returns the AO classification codes for a given image filestem
class PredictRequest(BaseModel):
    filestem: str

def mock_confidence(code: str, num_labels: int) -> float:
# Generate a mock confidence score based on how common the code is and how many labels are present for the image
    """
    Create a mocked confidence score for frontend testing.
    """
    freq = class_counts.get(code, 1) / max_class_count

    # Base confidence range: 0.62 to 0.90 depending on how common the code is
    confidence = 0.62 + (freq * 0.28)

    # Penalize multi-label predictions slightly by reducing confidence as the number of labels increases
    confidence -= max(0, num_labels - 1) * 0.04

    # Clamp to safe range and round
    confidence = max(0.55, min(confidence, 0.93))
    return round(confidence, 2)


# This endpoint simulates predictions by looking up the AO classification codes for the given filestem
@app.post("/predict")
def predict(req: PredictRequest):
    row = df[df["filestem"] == req.filestem]
    if row.empty:
        raise HTTPException(status_code=404, detail="Image not found")

    labels = str(row.iloc[0]["ao_classification"])
    codes = [c.strip() for c in labels.split(';') if c.strip()] if labels and labels.lower() != "nan" else []

    predictions = [ # Create a list of predictions with mock confidence scores
        {
            "code": c,
            "confidence": mock_confidence(c, len(codes))
        }
        for c in codes
    ]

    return {
        "filestem": req.filestem,
        "predictions": predictions,
        "num_labels": len(codes)
    }

# To run api: uvicorn scripts.mock_api:app --reload --port 8000
# URL should look like this: http://127.0.0.1:8000/
