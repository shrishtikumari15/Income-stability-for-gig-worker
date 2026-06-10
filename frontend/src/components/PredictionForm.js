import React, { useState } from "react";

const DEFAULTS = {
  monthly_income: 45000,
  monthly_income_2: 38000,
  income_volatility: 0.35,
  platform_count: 2,
  days_to_recover: 10,
  surplus_ratio: 0.45,
  working_days: 22,
  jobs_completed: 80,
  avg_daily_income: 1800,
  income_growth_rate: 0.05,
  expense_ratio: 0.55,
  savings_amount: 12000,
  late_payment_count: 1,
  work_consistency_score: 72.5,
  model: "rf",
};

const FIELD_CONFIG = [
  {
    section: "💰 Income Details",
    fields: [
      { key: "monthly_income",    label: "Monthly Income (₹)",         type: "number", min: 0, max: 200000, step: 500, tip: "Average monthly earnings in primary month" },
      { key: "monthly_income_2",  label: "Monthly Income – Last Month (₹)", type: "number", min: 0, max: 200000, step: 500 },
      { key: "avg_daily_income",  label: "Avg Daily Income (₹)",        type: "number", min: 0, max: 10000,  step: 50 },
      { key: "income_growth_rate",label: "Income Growth Rate",          type: "number", min: -1, max: 1,    step: 0.01, tip: "e.g. 0.05 = 5% growth, -0.1 = 10% decline" },
      { key: "income_volatility", label: "Income Volatility (0–1)",     type: "number", min: 0, max: 1,    step: 0.01, tip: "0 = very stable, 1 = highly unpredictable" },
    ],
  },
  {
    section: "📅 Work Pattern",
    fields: [
      { key: "working_days",           label: "Working Days per Month",   type: "number", min: 1,  max: 31, step: 1 },
      { key: "jobs_completed",         label: "Jobs Completed (Monthly)", type: "number", min: 0,  max: 500, step: 1 },
      { key: "platform_count",         label: "Number of Platforms Used", type: "number", min: 1,  max: 10, step: 1 },
      { key: "work_consistency_score", label: "Work Consistency Score (0–100)", type: "number", min: 0, max: 100, step: 0.5, tip: "Higher = more consistent work schedule" },
      { key: "days_to_recover",        label: "Days to Recover After Income Dip", type: "number", min: 0, max: 90, step: 1 },
    ],
  },
  {
    section: "📊 Financial Behaviour",
    fields: [
      { key: "surplus_ratio",      label: "Surplus Ratio (0–1)",    type: "number", min: 0,   max: 1,     step: 0.01, tip: "Income remaining after all expenses" },
      { key: "expense_ratio",      label: "Expense Ratio (0–1)",    type: "number", min: 0,   max: 1,     step: 0.01, tip: "Fraction of income spent on expenses" },
      { key: "savings_amount",     label: "Monthly Savings (₹)",    type: "number", min: 0,   max: 100000, step: 500 },
      { key: "late_payment_count", label: "Late Payment Count",     type: "number", min: 0,   max: 20,    step: 1 },
    ],
  },
];

export default function PredictionForm({ onSubmit, loading }) {
  const [form, setForm]         = useState(DEFAULTS);
  const [activeSection, setActiveSection] = useState(0);

  const handleChange = (key, value) => {
    setForm((prev) => ({ ...prev, [key]: parseFloat(value) || value }));
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    onSubmit(form);
  };

  const handleReset = () => setForm(DEFAULTS);

  return (
    <div className="form-card">
      <div className="form-header">
        <h2>Worker Details</h2>
        <p>Enter the gig worker's financial and work data</p>
      </div>

      {/* Section tabs */}
      <div className="section-tabs">
        {FIELD_CONFIG.map((sec, i) => (
          <button
            key={i}
            className={`tab-btn ${activeSection === i ? "active" : ""}`}
            onClick={() => setActiveSection(i)}
            type="button"
          >
            {sec.section}
          </button>
        ))}
      </div>

      <form onSubmit={handleSubmit}>
        {/* Active section fields */}
        <div className="fields-grid">
          {FIELD_CONFIG[activeSection].fields.map(({ key, label, type, min, max, step, tip }) => (
            <div className="field-group" key={key}>
              <label className="field-label">{label}</label>
              {tip && <span className="field-tip">{tip}</span>}
              <input
                className="field-input"
                type={type}
                min={min}
                max={max}
                step={step}
                value={form[key]}
                onChange={(e) => handleChange(key, e.target.value)}
                required
              />
            </div>
          ))}
        </div>

        {/* Model selector */}
        <div className="model-selector">
          <label className="field-label">🤖 Choose ML Model</label>
          <div className="model-options">
            {[
              { value: "rf", label: "Random Forest", metric: "Acc: 85%" },
              { value: "lr", label: "Logistic Regression", metric: "Acc: 95%" },
              { value: "linear", label: "Linear Regression", metric: "R2 score" },
            ].map((m) => (
              <label key={m.value} className={`model-option ${form.model === m.value ? "selected" : ""}`}>
                <input
                  type="radio"
                  name="model"
                  value={m.value}
                  checked={form.model === m.value}
                  onChange={() => setForm((p) => ({ ...p, model: m.value }))}
                />
                <span className="model-name">{m.label}</span>
                <span className="model-acc">{m.metric}</span>
              </label>
            ))}
          </div>
        </div>

        <div className="form-actions">
          <button type="button" className="btn-secondary" onClick={handleReset}>
            Reset
          </button>
          <button type="submit" className="btn-primary" disabled={loading}>
            {loading ? "⏳ Analysing..." : "🔍 Analyse Stability"}
          </button>
        </div>
      </form>
    </div>
  );
}
