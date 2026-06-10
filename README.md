# 🏦 AI-Based Income Stability Score for Gig Workers
### College Project | Banking & Finance Domain | ML + Full Stack

---

## 📌 Project Overview

This project builds an AI-powered system that evaluates the **income stability** of gig workers
(delivery agents, freelancers, cab drivers, etc.) and assigns a **stability score from 0 to 100**.
Financial institutions can use this score to make fairer, data-driven loan decisions.

---

## 🎯 Problem Statement

Gig workers often lack traditional payslips or fixed salaries, making it hard for banks to assess
their creditworthiness. This system fills that gap using machine learning on financial behaviour data.

---

## 📂 Project Structure

```
gigscore/
├── ml_pipeline/
│   └── train_model.py          # ML training script (run this first)
├── backend/
│   ├── app.py                  # Flask REST API
│   └── requirements.txt        # Python dependencies
├── frontend/
│   ├── public/index.html
│   ├── src/
│   │   ├── App.js              # Root React component
│   │   ├── App.css             # Styles
│   │   └── components/
│   │       ├── Header.js
│   │       ├── PredictionForm.js
│   │       └── ResultCard.js
│   └── package.json
├── models/                     # Auto-generated after training
│   ├── rf_model.pkl
│   ├── lr_model.pkl
│   ├── scaler.pkl
│   ├── features.pkl
│   └── meta.pkl
├── DEPLOYMENT.md               # PythonAnywhere deployment guide
└── README.md                   # This file
```

---

## 🧠 ML Approach

### Dataset
- **10,000 rows**, 16 features, no missing values
- Features: monthly income (×2), income volatility, platform count,
  days to recover, surplus ratio, working days, jobs completed,
  avg daily income, income growth rate, expense ratio, savings amount,
  late payment count, work consistency score

### Feature Engineering (5 new features)
| Feature | Formula | Meaning |
|---|---|---|
| `income_avg` | (income_1 + income_2) / 2 | Smoothed income |
| `income_stability_ratio` | 1 - volatility | How stable income is |
| `recovery_efficiency` | 1 / (days_to_recover + 1) | Speed of income recovery |
| `savings_rate` | savings / income_avg | Savings discipline |
| `job_efficiency` | jobs / working_days | Productivity rate |

### Scoring Formula (Weighted Sum)
```
Score = (0.20 × Consistency) + (0.15 × Income) + (0.15 × Stability)
      + (0.15 × Surplus)    + (0.10 × Savings) + (0.10 × Expense)
      + (0.10 × LatePayment)+ (0.05 × Recovery)
Score is scaled to [0, 100]
```

### Labels
| Score | Label | Loan Action |
|---|---|---|
| 67–100 | 🟢 High | Approve |
| 34–66  | 🟡 Medium | Conditional |
| 0–33   | 🔴 Low | Decline |

### Model Performance
| Model | Accuracy | Best For |
|---|---|---|
| Logistic Regression | **94.9%** | Interpretability, regulatory compliance |
| Random Forest | **85.0%** | Feature importance, non-linear patterns |

---

## 🚀 Quick Start

### 1. Train the Models
```bash
cd ml_pipeline
pip install -r ../backend/requirements.txt
python train_model.py
```

### 2. Start Flask Backend
```bash
cd backend
python app.py
# API running at http://localhost:5000
```

### 3. Start React Frontend
```bash
cd frontend
npm install
npm start
# UI running at http://localhost:3000
```

---

## 🌐 API Reference

### POST /api/predict
**Request body:**
```json
{
  "monthly_income": 45000,
  "monthly_income_2": 38000,
  "income_volatility": 0.35,
  "platform_count": 2,
  "days_to_recover": 10,
  "surplus_ratio": 0.45,
  "working_days": 22,
  "jobs_completed": 80,
  "avg_daily_income": 1800,
  "income_growth_rate": 0.05,
  "expense_ratio": 0.55,
  "savings_amount": 12000,
  "late_payment_count": 1,
  "work_consistency_score": 72.5,
  "model": "rf"
}
```

**Response:**
```json
{
  "stability_score": 72.4,
  "score_label": "High",
  "ml_label": "High",
  "probabilities": {"High": 87.3, "Medium": 9.1, "Low": 3.6},
  "model_used": "Random Forest",
  "recommendations": ["Excellent financial behaviour! Keep maintaining these habits."],
  "breakdown": { ... }
}
```

---

## 🔮 Future Enhancements
- **SHAP Explainability** — per-feature contribution for RBI audit compliance
- **LSTM Model** — analyse 6-month income time series for seasonal patterns
- **UPI Data Integration** — auto-fill fields from live transaction data
- **XGBoost** — typically outperforms RF on tabular financial data
- **Streamlit Demo** — quick alternative frontend for college demo

---

## 👨‍💻 Tech Stack
| Layer | Technology |
|---|---|
| Frontend | React 18, CSS3 |
| Backend | Flask 3.0, Flask-CORS |
| ML | scikit-learn, pandas, numpy |
| Deployment | PythonAnywhere (backend), Netlify (frontend) |
| Models | Random Forest, Logistic Regression |

---

## 📖 References
- scikit-learn Documentation: https://scikit-learn.org
- Flask Documentation: https://flask.palletsprojects.com
- PythonAnywhere Deployment: https://help.pythonanywhere.com
- Financial Inclusion Report, RBI 2023
