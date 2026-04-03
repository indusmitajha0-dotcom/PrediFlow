# 🌸 PrediFlow – AI-Driven Menstrual Health Tracker

> BTech Project Based Learning (PBL) – Phase 2  
> 🌐 Live Demo: https://indusmitajha0-dotcom.github.io/PrediFlow/
> An intelligent menstrual cycle prediction system with rule-based AI, anomaly detection, and a frontend interface.

---

## 📌 Project Overview

PrediFlow is a web-based menstrual health tracker that uses rule-based AI logic to:

- Predict the next menstrual cycle date
- Calculate ovulation date and fertile window
- Detect anomalies based on symptom severity and cycle irregularity
- Provide phase-based daily health tips
- Display confidence levels for each prediction

---

## ✨ Features

| Feature | Description |
|---|---|
| Cycle Prediction | Predicts next period using cycle history averaging |
| Symptom Scoring | 15 symptoms scored by severity for accurate adjustment |
| Anomaly Detection | Flags irregular cycles, extreme lengths, severe symptoms |
| Fertile Window | Calculates ovulation date and 6-day fertile window |
| Health Tips | Phase-based tips (menstrual, follicular, ovulatory, luteal) |
| Input Validation | Validates all inputs with clear error messages |
| Frontend UI | Clean pink & white HTML/CSS/JS interface |

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python 3.12, FastAPI |
| Server | Uvicorn |
| Frontend | HTML, CSS, JavaScript |
| API Docs | Swagger UI (auto-generated) |

---

## 📁 Project Structure

```
PrediFlow/
├── main.py           # FastAPI backend with all prediction logic
├── index.html        # Frontend user interface
├── requirements.txt  # Python dependencies
└── README.md         # Project documentation
```

---

## 🚀 How to Run

### 1. Clone the repository
```bash
git clone https://github.com/indusmitajha0-dotcom/PrediFlow.git
cd PrediFlow
```

### 2. Create and activate virtual environment
```bash
python -m venv venv
venv\Scripts\activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Start the backend server
```bash
uvicorn main:app --reload
```

### 5. Open the frontend
Open `index.html` directly in your browser by double clicking it.

---

## 🔗 API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| POST | `/predict` | Predict next cycle, anomaly, fertile window |
| POST | `/health-tips` | Get today's phase and health tips |
| GET | `/symptoms/list` | List all recognized symptoms |
| GET | `/` | Check if backend is running |

### Sample Request – `/predict`
```json
{
  "last_period_date": "2026-03-10",
  "cycle_length": 28,
  "period_duration": 5,
  "past_cycle_lengths": [27, 29, 28],
  "symptoms": ["cramps", "bloating"]
}
```

### Sample Response
```json
{
  "predicted_next_period": "2026-04-07",
  "confidence_level": "High",
  "anomaly_detected": false,
  "ovulation_date": "2026-03-24",
  "fertile_window": {
    "start": "2026-03-19",
    "end": "2026-03-25"
  },
  "cycle_regularity": "regular",
  "explanation": "Cycle appears normal based on provided data."
}
```

---

## 🧠 How the AI Logic Works

1. **Cycle Averaging** – If past cycle lengths are provided, the system averages them for a more accurate prediction instead of using a single fixed value.

2. **Symptom Scoring** – Each symptom has a severity score (1–5). The total score determines confidence level and whether an anomaly is flagged.

3. **Anomaly Detection** – An anomaly is flagged if:
   - Total symptom severity score exceeds threshold (≥ 8)
   - Cycle history shows high variation (standard deviation > 7 days)
   - Average cycle length is outside the normal 21–35 day range

4. **Fertile Window** – Calculated as 5 days before ovulation to 1 day after. Ovulation is estimated at cycle length minus 14 days.

---

## 📊 Current Status

- [x] Backend API with FastAPI
- [x] Rule-based prediction logic
- [x] Symptom-based anomaly detection
- [x] Fertile window and ovulation calculation
- [x] Health tips by cycle phase
- [x] Input validation
- [x] Frontend HTML/CSS/JS interface
- [ ] Database integration (planned)
- [ ] User authentication (planned)

---

## ⚠️ Disclaimer

PrediFlow is developed for educational purposes as part of a BTech PBL project. It is not a medical device and should not be used as a substitute for professional medical advice.

---

## 👩‍💻 Developer

**Indusmita Jha**  
BTech Student | PBL Phase 2 Project
