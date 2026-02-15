from fastapi import FastAPI
from pydantic import BaseModel
from datetime import datetime, timedelta

app = FastAPI(title="PrediFlow Backend")

class PredictionInput(BaseModel):
    last_period_date: str
    cycle_length: int
    symptoms: list[str]

@app.post("/predict")
def predict_cycle(data: PredictionInput):
    last_date = datetime.strptime(data.last_period_date, "%Y-%m-%d")
    predicted_date = last_date + timedelta(days=data.cycle_length)

    anomaly = False
    confidence = "High"
    explanation = "Cycle appears normal based on provided data."

    # Symptom-based adjustments
    if "cramps" in data.symptoms or "bloating" in data.symptoms:
        predicted_date -= timedelta(days=1)
        confidence = "Medium"
        explanation = "Symptoms indicate pre-menstrual phase."

    if "severe cramps" in data.symptoms or "extreme fatigue" in data.symptoms:
        anomaly = True
        confidence = "Low"
        explanation = "Unusual symptom combination detected."

    return {
        "predicted_next_period": predicted_date.strftime("%Y-%m-%d"),
        "confidence_level": confidence,
        "anomaly_detected": anomaly,
        "explanation": explanation
    }


@app.get("/")
def root():
    return {"status": "PrediFlow backend running"}
