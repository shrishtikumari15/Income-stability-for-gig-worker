"""
AI-Based Income Stability Score for Gig Workers
ML Training Pipeline
=====================================================
Run: python train_model.py
Output: Saves trained models to ../models/
"""

import pandas as pd
import numpy as np
import pickle
import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt


from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
# linear regression s
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score, mean_absolute_error
from sklearn.metrics import (
    classification_report, accuracy_score,
    confusion_matrix, ConfusionMatrixDisplay
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.abspath(os.path.join(BASE_DIR, '..'))
DATA_PATH = os.path.join(PROJECT_DIR, 'data.csv')
MODELS_DIR = os.path.join(PROJECT_DIR, 'models')
FEATURE_IMPORTANCE_PATH = os.path.join(BASE_DIR, 'feature_importance.png')

# ─────────────────────────────────────────────────
# 1. LOAD DATA
# ─────────────────────────────────────────────────
print("="*60)
print("STEP 1: Loading Dataset")
print("="*60)

df = pd.read_csv(DATA_PATH)
print(f"  Rows: {df.shape[0]}  |  Columns: {df.shape[1]}")
print(f"  Missing values: {df.isnull().sum().sum()}")


# ─────────────────────────────────────────────────
# 2. FEATURE ENGINEERING
# ─────────────────────────────────────────────────
print("\nSTEP 2: Feature Engineering")

df['income_avg']              = (df['monthly_income'] + df['monthly_income_2']) / 2
df['income_stability_ratio']  = 1 - df['income_volatility']          # high = stable
df['recovery_efficiency']     = 1 / (df['days_to_recover'] + 1)      # high = recovers fast
df['savings_rate']            = df['savings_amount'] / (df['income_avg'] + 1)
df['job_efficiency']          = df['jobs_completed'] / (df['working_days'] + 1)

print("  New features added: income_avg, income_stability_ratio,")
print("  recovery_efficiency, savings_rate, job_efficiency")


# ─────────────────────────────────────────────────
# 3. DOMAIN-BASED STABILITY SCORING
#    (This is the primary scoring engine)
# ─────────────────────────────────────────────────
print("\nSTEP 3: Computing Domain-Based Stability Score")

def minmax_scale(series):
    """Normalize a series to 0-100 range."""
    return (series - series.min()) / (series.max() - series.min()) * 100

# Normalize features (some inverted: lower raw value = better stability)
df['s_income']      = minmax_scale(df['income_avg'])
df['s_consistency'] = minmax_scale(df['work_consistency_score'])
df['s_surplus']     = minmax_scale(df['surplus_ratio'])
df['s_savings']     = minmax_scale(df['savings_amount'])
df['s_volatility']  = 100 - minmax_scale(df['income_volatility'])   # inverted
df['s_expense']     = 100 - minmax_scale(df['expense_ratio'])        # inverted
df['s_late']        = 100 - minmax_scale(df['late_payment_count'])   # inverted
df['s_recovery']    = 100 - minmax_scale(df['days_to_recover'])      # inverted

# Weighted scoring formula (weights sum to 1.0)
WEIGHTS = {
    's_consistency' : 0.20,   # Work regularity is most important
    's_income'      : 0.15,   # Average income level
    's_volatility'  : 0.15,   # Income stability
    's_surplus'     : 0.15,   # Income surplus after expenses
    's_savings'     : 0.10,   # Savings behaviour
    's_expense'     : 0.10,   # Expense control
    's_late'        : 0.10,   # Payment discipline
    's_recovery'    : 0.05,   # Recovery speed after income dip
}

df['computed_score'] = sum(df[k] * v for k, v in WEIGHTS.items())
print(f"  Score range: {df['computed_score'].min():.2f} - {df['computed_score'].max():.2f}")
print(f"  Mean score : {df['computed_score'].mean():.2f}")


# ─────────────────────────────────────────────────
# 4. CREATE LABELS (percentile-based, balanced)
# ─────────────────────────────────────────────────
p33 = df['computed_score'].quantile(0.33)
p66 = df['computed_score'].quantile(0.66)

def assign_label(score):
    if score <= p33:   return 'Low'
    elif score <= p66: return 'Medium'
    else:              return 'High'

df['stability_label'] = df['computed_score'].apply(assign_label)
print(f"\n  Thresholds -> Low: <={p33:.2f}  |  Medium: <={p66:.2f}  |  High: >{p66:.2f}")
print("  Label distribution:")
print(df['stability_label'].value_counts().to_string())


# ─────────────────────────────────────────────────
# 5. PREPARE FEATURES & SPLIT
# ─────────────────────────────────────────────────
FEATURES = [
    'income_avg', 'income_stability_ratio', 'recovery_efficiency',
    'savings_rate', 'work_consistency_score', 'platform_count',
    'late_payment_count', 'expense_ratio', 'income_growth_rate',
    'working_days', 'jobs_completed', 'avg_daily_income',
    'surplus_ratio', 'income_volatility', 'job_efficiency', 'savings_amount'
]

X = df[FEATURES]
y = df['stability_label']
y_score = df['computed_score']

X_train, X_test, y_train, y_test, y_score_train, y_score_test = train_test_split(
    X, y, y_score, test_size=0.2, random_state=42, stratify=y
)

print(f"\n  Train size: {len(X_train)}  |  Test size: {len(X_test)}")

# Scale features
scaler = StandardScaler()
X_train_s = scaler.fit_transform(X_train.to_numpy())
X_test_s  = scaler.transform(X_test.to_numpy())




# ─────────────────────────────────────────────────
# 6. TRAIN MODELS
# ─────────────────────────────────────────────────
print("\nSTEP 4: Training Models")

class_score_map = y_score_train.groupby(y_train).mean().to_dict()

def expected_score_from_proba(model, probabilities):
    return np.array([
        sum(prob * class_score_map[label] for label, prob in zip(model.classes_, row))
        for row in probabilities
    ])

# --- Random Forest ---
print("\n  Training Random Forest...")
rf_model = RandomForestClassifier(
    n_estimators=150,
    max_depth=15,
    min_samples_leaf=3,
    random_state=42,
    n_jobs=-1
)
rf_model.fit(X_train_s, y_train)
rf_pred   = rf_model.predict(X_test_s)
rf_acc    = accuracy_score(y_test, rf_pred)
rf_cv     = cross_val_score(rf_model, X_train_s, y_train, cv=5).mean()
rf_score_pred = expected_score_from_proba(rf_model, rf_model.predict_proba(X_test_s))
rf_r2 = r2_score(y_score_test, rf_score_pred)
rf_mae = mean_absolute_error(y_score_test, rf_score_pred)
print(f"  RF  Test Accuracy:  {rf_acc:.4f}")
print(f"  RF  CV-5 Accuracy:  {rf_cv:.4f}")
print(f"  RF  R2:             {rf_r2:.4f}")
print(f"  RF  MAE:            {rf_mae:.4f}")
print(classification_report(y_test, rf_pred))

# --- Logistic Regression ---
print("  Training Logistic Regression...")
lr_model = LogisticRegression(max_iter=2000, C=1.0, random_state=42)
lr_model.fit(X_train_s, y_train)
lr_pred  = lr_model.predict(X_test_s)
lr_acc   = accuracy_score(y_test, lr_pred)
lr_cv    = cross_val_score(lr_model, X_train_s, y_train, cv=5).mean()
lr_score_pred = expected_score_from_proba(lr_model, lr_model.predict_proba(X_test_s))
lr_r2 = r2_score(y_score_test, lr_score_pred)
lr_mae = mean_absolute_error(y_score_test, lr_score_pred)
print(f"  LR  Test Accuracy:  {lr_acc:.4f}")
print(f"  LR  CV-5 Accuracy:  {lr_cv:.4f}")
print(f"  LR  R2:             {lr_r2:.4f}")
print(f"  LR  MAE:            {lr_mae:.4f}")
print(classification_report(y_test, lr_pred))


# --- Linear Regression ---
print("  Training Linear Regression...")

X_train_reg, X_test_reg, y_train_reg, y_test_reg = train_test_split(
    X,
    y_score,
    test_size=0.2,
    random_state=42
)
X_train_reg_s = scaler.transform(X_train_reg.to_numpy())
X_test_reg_s = scaler.transform(X_test_reg.to_numpy())

linear_model = LinearRegression()

linear_model.fit(X_train_reg_s, y_train_reg)

linear_pred = linear_model.predict(X_test_reg_s)

linear_r2 = r2_score(y_test_reg, linear_pred)
linear_mae = mean_absolute_error(y_test_reg, linear_pred)

print(f"  Linear Regression R2: {linear_r2:.4f}")
print(f"  Linear Regression MAE: {linear_mae:.4f}")


# ─────────────────────────────────────────────────
# 7. FEATURE IMPORTANCE PLOT
# ─────────────────────────────────────────────────
fi = pd.Series(rf_model.feature_importances_, index=FEATURES).sort_values()
fig, ax = plt.subplots(figsize=(8, 6))
fi.plot(kind='barh', ax=ax, color='steelblue')
ax.set_title("Feature Importance (Random Forest)")
ax.set_xlabel("Importance Score")
plt.tight_layout()
plt.savefig(FEATURE_IMPORTANCE_PATH, dpi=100)
print("  Saved feature_importance.png")


# ─────────────────────────────────────────────────
# 8. SAVE MODELS
# ─────────────────────────────────────────────────
os.makedirs(MODELS_DIR, exist_ok=True)

# meta = {
#     'p33': p33, 'p66': p66, 'weights': WEIGHTS,
#     'rf_accuracy': rf_acc, 'lr_accuracy': lr_acc,
#     'features': FEATURES
# }

#s
meta = {
    'p33': p33,
    'p66': p66,
    'weights': WEIGHTS,
    'rf_accuracy': rf_acc,
    'lr_accuracy': lr_acc,
    'rf_r2': rf_r2,
    'rf_mae': rf_mae,
    'lr_r2': lr_r2,
    'lr_mae': lr_mae,
    'linear_r2': linear_r2,
    'linear_mae': linear_mae,
    'features': FEATURES
}

with open(os.path.join(MODELS_DIR, "rf_model.pkl"),  'wb') as f: pickle.dump(rf_model, f)
with open(os.path.join(MODELS_DIR, "lr_model.pkl"),  'wb') as f: pickle.dump(lr_model, f)
with open(os.path.join(MODELS_DIR, "linear_model.pkl"),  'wb') as f: pickle.dump(linear_model, f)
with open(os.path.join(MODELS_DIR, "scaler.pkl"),    'wb') as f: pickle.dump(scaler, f)
with open(os.path.join(MODELS_DIR, "features.pkl"),  'wb') as f: pickle.dump(FEATURES, f)
with open(os.path.join(MODELS_DIR, "meta.pkl"),      'wb') as f: pickle.dump(meta, f)

print("\nSTEP 5: Models Saved -> ../models/")
print(f"  rf_model.pkl  (Accuracy: {rf_acc:.2%}, R2: {rf_r2:.2%}, MAE: {rf_mae:.2f})")
print(f"  lr_model.pkl  (Accuracy: {lr_acc:.2%}, R2: {lr_r2:.2%}, MAE: {lr_mae:.2f})")
print(f"  linear_model.pkl  (R2: {linear_r2:.2%}, MAE: {linear_mae:.2f})")
print(f"  scaler.pkl    (StandardScaler)")
print(f"  features.pkl  (Feature list)")
print(f"  meta.pkl      (Thresholds & weights)")
print("\nTraining complete!")
