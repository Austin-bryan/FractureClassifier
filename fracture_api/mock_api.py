# # This is where the mock API will be until we have the actual API ready.
# # This will allow us to ensure that our frontend can communicate with the backend.

# from fastapi import FastAPI, HTTPException
# from fastapi.middleware.cors import CORSMiddleware
# from pydantic import BaseModel
# import pandas as pd

# app = FastAPI(title="Mock Fracture Classification API")
# df = pd.read_csv('dataset.csv')

# app.add_middleware( # Allows CORS to connect frontend and backend during development
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# #Health check for API
# @app.get("/health")
# def health():
#     return {"status": "ok"}

# # Endpoint to list all classes and their counts in the dataset
# @app.get("/classes")
# def list_classes(limit: int = None):
#     codes = []
#     for entry in df['ao_classification'].dropna():
#         codes.extend([c.strip() for c in entry.split(';') if c.strip()])
#     from collections import Counter
#     counts = Counter(codes)
#     items = sorted(counts.items(), key=lambda kv: kv[1], reverse=True)
#     if limit:
#         items = items[:limit]
#     return {"classes": [{"code": c, "count": n} for c, n in items]}

# # Count how many codes per image
# @app.get("/multiplicity")
# def multiplicity():
#     mult = df['ao_classification'].fillna('').apply(
#         lambda x: len([c for c in x.split(';') if c.strip()])
#     ).value_counts().sort_index().to_dict()
#     return {"multiplicity": mult}

# #Image Metadata
# @app.get("/image/{filestem}")
# def image_metadata(filestem: str):
#     row = df[df["filestem"] == filestem]
#     if row.empty:
#         raise HTTPException(status_code=404, detail="Image wasn't found")
#     record = row.iloc[0]
#     return record.to_dict()

# # Predict endpoint that returns the AO classification codes for a given image filestem
# class PredictRequest(BaseModel):
#     filestem: str

# # This is a mock implementation that looks up the AO classification from the dataset based on the filestem.
# @app.post("/predict")
# def predict(req: PredictRequest):
#     row = df[df["filestem"] == req.filestem]
#     if row.empty:
#         raise HTTPException(status_code=404, detail="Image not found")
#     labels = str(row.iloc[0]["ao_classification"])
#     codes = [c.strip() for c in labels.split(';') if c.strip()] if labels and labels.lower() != "nan" else []
#     return {
#         "filestem": req.filestem,
#         "predictions": [{"code": c, "confidence": 1.0} for c in codes],
#         "num_labels": len(codes)
#     }


#Runs api: uvicorn mock_api:app --reload --port 8000
