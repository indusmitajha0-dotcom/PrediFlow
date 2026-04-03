from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, field_validator
from datetime import datetime, timedelta
from typing import Optional
import statistics

app = FastAPI(title="PrediFlow Backend", version="2.0")

# Allow frontend to call this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------- Models ----------

class PredictionInput(BaseModel):
    last_period_date: str
    cycle_length: int
    period_duration: Optional[int] = 5          # how many days period lasts
    past_cycle_lengths: Optional[list[int]] = [] # history for better prediction
    symptoms: Optional[list[str]] = []

    @field_validator("cycle_length")
    @classmethod
    def validate_cycle_length(cls, v):
        if not (15 <= v <= 60):
            raise ValueError("Cycle length must be between 15 and 60 days.")
        return v

    @field_validator("period_duration")
    @classmethod
    def validate_period_duration(cls, v):
        if v is not None and not (1 <= v <= 10):
            raise ValueError("Period duration must be between 1 and 10 days.")
        return v

    @field_validator("past_cycle_lengths")
    @classmethod
    def validate_past_cycles(cls, v):
        if v:
            for length in v:
                if not (15 <= length <= 60):
                    raise ValueError("All past cycle lengths must be between 15 and 60 days.")
        return v

    @field_validator("last_period_date")
    @classmethod
    def validate_date(cls, v):
        try:
            parsed = datetime.strptime(v, "%Y-%m-%d")
        except ValueError:
            raise ValueError("Date must be in YYYY-MM-DD format.")
        if parsed > datetime.today():
            raise ValueError("Last period date cannot be in the future.")
        return v


class HealthTipInput(BaseModel):
    last_period_date: str
    cycle_length: int

    @field_validator("last_period_date")
    @classmethod
    def validate_date(cls, v):
        try:
            datetime.strptime(v, "%Y-%m-%d")
        except ValueError:
            raise ValueError("Date must be in YYYY-MM-DD format.")
        return v


# ---------- Symptom Scoring ----------

SYMPTOM_SCORES = {
    # Minor symptoms → slight adjustment
    "bloating":          {"delay": -1, "severity": 1},
    "cramps":            {"delay": -1, "severity": 1},
    "mood swings":       {"delay": 0,  "severity": 1},
    "breast tenderness": {"delay": 0,  "severity": 1},
    "acne":              {"delay": 0,  "severity": 1},
    "headache":          {"delay": 0,  "severity": 1},
    "fatigue":           {"delay": 0,  "severity": 1},

    # Moderate symptoms
    "severe cramps":     {"delay": -2, "severity": 3},
    "heavy bleeding":    {"delay": -1, "severity": 3},
    "nausea":            {"delay": -1, "severity": 2},
    "back pain":         {"delay": -1, "severity": 2},

    # Serious / anomaly-indicating symptoms
    "extreme fatigue":   {"delay": 0,  "severity": 5},
    "spotting":          {"delay": 0,  "severity": 4},
    "missed period":     {"delay": 7,  "severity": 5},
    "prolonged bleeding":{"delay": 0,  "severity": 5},
    "pelvic pain":       {"delay": 0,  "severity": 4},
}

ANOMALY_THRESHOLD = 8  # total severity score that triggers anomaly flag


def analyze_symptoms(symptoms: list[str]):
    total_delay = 0
    total_severity = 0
    matched = []
    unrecognized = []

    for s in symptoms:
        s_lower = s.lower().strip()
        if s_lower in SYMPTOM_SCORES:
            total_delay += SYMPTOM_SCORES[s_lower]["delay"]
            total_severity += SYMPTOM_SCORES[s_lower]["severity"]
            matched.append(s_lower)
        else:
            unrecognized.append(s)

    return total_delay, total_severity, matched, unrecognized


# ---------- Cycle Regularity ----------

def check_cycle_regularity(cycle_length: int, past_cycles: list[int]):
    all_cycles = past_cycles + [cycle_length]

    if len(all_cycles) < 2:
        return cycle_length, "insufficient_data"

    avg = statistics.mean(all_cycles)
    stdev = statistics.stdev(all_cycles) if len(all_cycles) > 1 else 0

    # Irregular if standard deviation > 7 days
    if stdev > 7:
        regularity = "irregular"
    elif stdev > 3:
        regularity = "slightly_irregular"
    else:
        regularity = "regular"

    return round(avg), regularity


# ---------- Endpoints ----------

@app.post("/predict")
def predict_cycle(data: PredictionInput):
    last_date = datetime.strptime(data.last_period_date, "%Y-%m-%d")

    # Use averaged cycle length if history is provided
    effective_cycle_length, regularity = check_cycle_regularity(
        data.cycle_length, data.past_cycle_lengths or []
    )

    # Base prediction
    predicted_date = last_date + timedelta(days=effective_cycle_length)

    # Symptom analysis
    symptom_delay, symptom_severity, matched_symptoms, unrecognized = analyze_symptoms(
        data.symptoms or []
    )
    predicted_date += timedelta(days=symptom_delay)

    # Anomaly detection
    anomaly = False
    anomaly_reasons = []

    if symptom_severity >= ANOMALY_THRESHOLD:
        anomaly = True
        anomaly_reasons.append("High-severity symptom combination detected.")

    if regularity == "irregular":
        anomaly = True
        anomaly_reasons.append("Significant cycle length variation across history.")

    if effective_cycle_length < 21 or effective_cycle_length > 35:
        anomaly = True
        anomaly_reasons.append(
            f"Average cycle length of {effective_cycle_length} days is outside the typical 21–35 day range."
        )

    # Confidence level
    if anomaly:
        confidence = "Low"
    elif regularity == "slightly_irregular" or symptom_severity >= 4:
        confidence = "Medium"
    else:
        confidence = "High"

    # Fertile window (ovulation ≈ cycle_length - 14 days after last period)
    ovulation_day = last_date + timedelta(days=effective_cycle_length - 14)
    fertile_start = ovulation_day - timedelta(days=5)
    fertile_end = ovulation_day + timedelta(days=1)

    # Build explanation
    if anomaly:
        explanation = "Anomaly detected: " + " | ".join(anomaly_reasons)
    elif matched_symptoms:
        explanation = f"Prediction adjusted based on symptoms: {', '.join(matched_symptoms)}."
    else:
        explanation = "Cycle appears normal based on provided data."

    if regularity == "regular" and len(data.past_cycle_lengths or []) > 0:
        explanation += " Cycle history shows consistent regularity."
    elif regularity == "slightly_irregular":
        explanation += " Minor cycle variation noted in history."

    response = {
        "predicted_next_period": predicted_date.strftime("%Y-%m-%d"),
        "confidence_level": confidence,
        "anomaly_detected": anomaly,
        "anomaly_reasons": anomaly_reasons,
        "explanation": explanation,
        "cycle_regularity": regularity,
        "effective_cycle_length_used": effective_cycle_length,
        "ovulation_date": ovulation_day.strftime("%Y-%m-%d"),
        "fertile_window": {
            "start": fertile_start.strftime("%Y-%m-%d"),
            "end": fertile_end.strftime("%Y-%m-%d"),
        },
    }

    if unrecognized:
        response["unrecognized_symptoms"] = unrecognized
        response["note"] = "Some symptoms were not recognized. Consult a doctor if concerned."

    return response


@app.post("/health-tips")
def health_tips(data: HealthTipInput):
    last_date = datetime.strptime(data.last_period_date, "%Y-%m-%d")
    today = datetime.today()
    days_since = (today - last_date).days
    cycle_day = days_since % data.cycle_length

    if cycle_day <= 5:
        phase = "menstrual"
        tips = [
            "Rest and stay hydrated.",
            "Use a heating pad for cramp relief.",
            "Eat iron-rich foods like spinach and lentils.",
            "Light yoga or walking can ease discomfort.",
        ]
    elif cycle_day <= 13:
        phase = "follicular"
        tips = [
            "Energy levels are rising — good time to start new tasks.",
            "Focus on strength training or cardio.",
            "Eat foods rich in estrogen-supporting nutrients like flaxseeds.",
            "Great time for social activities and creative work.",
        ]
    elif cycle_day <= 16:
        phase = "ovulatory"
        tips = [
            "Peak energy — ideal for high-intensity workouts.",
            "Stay hydrated and eat light, balanced meals.",
            "You may feel more social and communicative today.",
            "Track any ovulation symptoms like mild pelvic pain.",
        ]
    else:
        phase = "luteal"
        tips = [
            "You may feel more tired — prioritize sleep.",
            "Reduce caffeine and sugar to ease PMS symptoms.",
            "Magnesium-rich foods (nuts, dark chocolate) can help with mood.",
            "Gentle exercise like yoga or swimming is beneficial.",
        ]

    return {
        "current_cycle_day": cycle_day,
        "current_phase": phase,
        "health_tips": tips,
    }


@app.get("/symptoms/list")
def list_symptoms():
    return {
        "recognized_symptoms": list(SYMPTOM_SCORES.keys()),
        "note": "Pass these as strings in the 'symptoms' array for accurate predictions.",
    }


@app.get("/")
def root():
    return {"status": "PrediFlow backend v2.0 running"}