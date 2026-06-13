"""
AI-Based Income Stability Score for Gig Workers
Flask Backend API
=====================================================
Endpoints:
  POST /api/predict         → Main prediction endpoint
  GET  /api/health          → Health check
  GET  /api/model-info      → Model metadata
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import pickle
import numpy as np
import os

app = Flask(__name__)
CORS(app)   # Allow React frontend to call this API

# ─────────────────────────────────────────────────
# LOAD MODELS (once at startup)
# ─────────────────────────────────────────────────
BASE_DIR    = os.path.dirname(os.path.abspath(__file__))
MODELS_DIR  = os.path.join(BASE_DIR, '..', 'models')

def load_pickle(filename):
    with open(os.path.join(MODELS_DIR, filename), 'rb') as f:
        return pickle.load(f)

rf_model  = load_pickle('rf_model.pkl')
lr_model  = load_pickle('lr_model.pkl')
linear_model = load_pickle('linear_model.pkl')
scaler    = load_pickle('scaler.pkl')
FEATURES  = load_pickle('features.pkl')
meta      = load_pickle('meta.pkl')

P33     = meta['p33']
P66     = meta['p66']
WEIGHTS = meta['weights']

print("Models loaded successfully")


# ─────────────────────────────────────────────────
# HELPER: COMPUTE STABILITY SCORE (0–100)
# ─────────────────────────────────────────────────
# Min/max reference values derived from training data
FEATURE_RANGES = {
    'monthly_income'        : (10000, 79995),
    'monthly_income_2'      : (10000, 79995),
    'income_volatility'     : (0.0,   1.0),
    'platform_count'        : (1,     5),
    'days_to_recover'       : (1,     30),
    'surplus_ratio'         : (0.0,   1.0),
    'working_days'          : (10,    30),
    'jobs_completed'        : (1,     300),
    'avg_daily_income'      : (100,   5000),
    'income_growth_rate'    : (-0.5,  0.5),
    'expense_ratio'         : (0.1,   0.95),
    'savings_amount'        : (0,     50000),
    'late_payment_count'    : (0,     9),
    'work_consistency_score': (0,     100),
}

def clamp01(val, low, high):
    """Normalize a value to [0,1] using min/max clamp."""
    return max(0.0, min(1.0, (val - low) / (high - low + 1e-9)))

def compute_stability_score(data: dict) -> float:
    """
    Domain-based scoring formula.
    Returns a float in [0, 100].
    
    Higher score = more stable income = better loan candidate.
    """
    mi1 = data['monthly_income']
    mi2 = data['monthly_income_2']
    income_avg = (mi1 + mi2) / 2

    # Normalize each feature to [0, 1]
    s_income      = clamp01(income_avg,                       10000, 79995)
    s_consistency = clamp01(data['work_consistency_score'],   0,     100)
    s_surplus     = clamp01(data['surplus_ratio'],            0.0,   1.0)
    s_savings     = clamp01(data['savings_amount'],           0,     50000)
    s_volatility  = 1 - clamp01(data['income_volatility'],   0.0,   1.0)   # inverted
    s_expense     = 1 - clamp01(data['expense_ratio'],       0.1,   0.95)  # inverted
    s_late        = 1 - clamp01(data['late_payment_count'],  0,     9)     # inverted
    s_recovery    = 1 - clamp01(data['days_to_recover'],     1,     30)    # inverted

    score = (
        WEIGHTS['s_consistency'] * s_consistency +
        WEIGHTS['s_income']      * s_income      +
        WEIGHTS['s_volatility']  * s_volatility  +
        WEIGHTS['s_surplus']     * s_surplus      +
        WEIGHTS['s_savings']     * s_savings      +
        WEIGHTS['s_expense']     * s_expense      +
        WEIGHTS['s_late']        * s_late         +
        WEIGHTS['s_recovery']    * s_recovery
    ) * 100

    return round(float(score), 2)


def build_feature_vector(data: dict) -> np.ndarray:
    """
    Construct the ML feature vector from raw input.
    Must match the order in FEATURES list used during training.
    """
    mi1 = data['monthly_income']
    mi2 = data['monthly_income_2']
    income_avg             = (mi1 + mi2) / 2
    income_stability_ratio = 1 - data['income_volatility']
    recovery_efficiency    = 1 / (data['days_to_recover'] + 1)
    savings_rate           = data['savings_amount'] / (income_avg + 1)
    job_efficiency         = data['jobs_completed'] / (data['working_days'] + 1)

    vector = [
        income_avg,
        income_stability_ratio,
        recovery_efficiency,
        savings_rate,
        data['work_consistency_score'],
        data['platform_count'],
        data['late_payment_count'],
        data['expense_ratio'],
        data['income_growth_rate'],
        data['working_days'],
        data['jobs_completed'],
        data['avg_daily_income'],
        data['surplus_ratio'],
        data['income_volatility'],
        job_efficiency,
        data['savings_amount'],
    ]
    return np.array(vector).reshape(1, -1)


def get_label(score: float) -> str:
    """Map numeric score to stability label."""
    if score <= 33:   return 'Low'
    elif score <= 66: return 'Medium'
    else:             return 'High'


def get_recommendations(label: str, data: dict) -> list:
    """Return actionable suggestions based on stability label and weak areas."""
    recs = []
    if data['income_volatility'] > 0.6:
        recs.append("Diversify income sources to reduce volatility.")
    if data['late_payment_count'] > 3:
        recs.append("Reduce late payments to improve credit behaviour.")
    if data['savings_amount'] < 5000:
        recs.append("Build an emergency savings fund of at least 3 months income.")
    if data['expense_ratio'] > 0.7:
        recs.append("Control monthly expenses; aim for expense ratio below 0.6.")
    if data['work_consistency_score'] < 40:
        recs.append("Work more consistently — irregular gig patterns lower your score.")
    if data['surplus_ratio'] < 0.2:
        recs.append("Increase income or reduce expenses to improve surplus ratio.")
    if not recs:
        recs.append("Excellent financial behaviour! Keep maintaining these habits.")
    return recs


# ─────────────────────────────────────────────────
# ROUTES
# ─────────────────────────────────────────────────

@app.route('/api/health', methods=['GET'])
def health():
    """Health check endpoint."""
    return jsonify({'status': 'ok', 'message': 'Gig Worker Stability API is running'})


@app.route('/api/model-info', methods=['GET'])
def model_info():
    """Return model metadata."""
    return jsonify({
        'models': ['Random Forest', 'Logistic Regression', 'Linear Regression'],
        'rf_accuracy': round(meta.get('rf_accuracy', 0.85) * 100, 2),
        'lr_accuracy': round(meta.get('lr_accuracy', 0.95) * 100, 2),
        'rf_r2': round(meta.get('rf_r2', 0) * 100, 2),
        'rf_mae': round(meta.get('rf_mae', 0), 2),
        'lr_r2': round(meta.get('lr_r2', 0) * 100, 2),
        'lr_mae': round(meta.get('lr_mae', 0), 2),
        'linear_r2': round(meta.get('linear_r2', 0) * 100, 2),
        'linear_mae': round(meta.get('linear_mae', 0), 2),
        'features': FEATURES,
        'score_thresholds': {'low': 33, 'medium': 66},
        'scoring_weights': WEIGHTS
    })


@app.route('/api/predict', methods=['POST'])
def predict():
    """
    Main prediction endpoint.
    
    Expected JSON body:
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
        "model": "rf"   // "rf", "lr", or "linear"
    }
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No JSON body provided'}), 400

        # ── Validate required fields ──
        required = [
            'monthly_income', 'monthly_income_2', 'income_volatility',
            'platform_count', 'days_to_recover', 'surplus_ratio',
            'working_days', 'jobs_completed', 'avg_daily_income',
            'income_growth_rate', 'expense_ratio', 'savings_amount',
            'late_payment_count', 'work_consistency_score'
        ]
        missing = [k for k in required if k not in data]
        if missing:
            return jsonify({'error': f'Missing fields: {missing}'}), 400

        # ── Choose model ──
        model_choice = data.get('model', 'rf').lower()
        models = {
            'rf': (rf_model, 'Random Forest'),
            'lr': (lr_model, 'Logistic Regression'),
            'linear': (linear_model, 'Linear Regression'),
        }
        if model_choice not in models:
            return jsonify({'error': 'Invalid model. Use "rf", "lr", or "linear".'}), 400

        model, model_name = models[model_choice]

        # ── Compute stability score (domain formula) ──
        stability_score = compute_stability_score(data)

        # ── ML classification ──
        X = build_feature_vector(data)
        X_scaled = scaler.transform(X)
        if model_choice == 'linear':
            predicted_score = round(float(np.clip(model.predict(X_scaled)[0], 0, 100)), 2)
            ml_label = get_label(predicted_score)
            probabilities = {}
        else:
            ml_label        = model.predict(X_scaled)[0]
            ml_proba        = model.predict_proba(X_scaled)[0]
            class_labels    = list(model.classes_)
            probabilities   = {cls: round(float(p)*100, 1) for cls, p in zip(class_labels, ml_proba)}

        # ── Score-based label ──
        score_label = get_label(stability_score)

        # ── Recommendations ──
        recommendations = get_recommendations(score_label, data)

        return jsonify({
            'stability_score'   : stability_score,
            'score_label'       : score_label,
            'ml_label'          : ml_label,
            'probabilities'     : probabilities,
            'model_used'        : model_name,
            'recommendations'   : recommendations,
            'breakdown': {
                'income_component'     : round(clamp01((data['monthly_income']+data['monthly_income_2'])/2, 10000, 79995)*100, 1),
                'consistency_component': round(clamp01(data['work_consistency_score'], 0, 100)*100, 1),
                'volatility_component' : round((1 - clamp01(data['income_volatility'], 0, 1))*100, 1),
                'savings_component'    : round(clamp01(data['savings_amount'], 0, 50000)*100, 1),
                'expense_component'    : round((1 - clamp01(data['expense_ratio'], 0.1, 0.95))*100, 1),
                'late_payment_component': round((1 - clamp01(data['late_payment_count'], 0, 9))*100, 1),
            }
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ─────────────────────────────────────────────────
# ENTRY POINT
# ─────────────────────────────────────────────────
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=True, host='0.0.0.0', port=port)
