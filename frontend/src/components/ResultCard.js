import React from "react";

const LABEL_CONFIG = {
  High:   { color: "#22c55e", bg: "#f0fdf4", border: "#bbf7d0", icon: "✅", text: "High Stability" },
  Medium: { color: "#f59e0b", bg: "#fffbeb", border: "#fde68a", icon: "⚠️", text: "Medium Stability" },
  Low:    { color: "#ef4444", bg: "#fef2f2", border: "#fecaca", icon: "❌", text: "Low Stability" },
};

function ScoreGauge({ score }) {
  const radius   = 80;
  const stroke   = 14;
  const cx       = 110;
  const cy       = 110;
  // Semi-circle: use 180° arc (half of circumference)
  const halfCirc = Math.PI * radius;
  const dashArr  = halfCirc;
  const dashOff  = halfCirc - (score / 100) * halfCirc;

  let color = "#ef4444";
  if (score > 66) color = "#22c55e";
  else if (score > 33) color = "#f59e0b";

  return (
    <div className="gauge-container">
      <svg width="220" height="130" viewBox="0 0 220 130">
        {/* Background arc */}
        <path
          d={`M ${cx - radius} ${cy} A ${radius} ${radius} 0 0 1 ${cx + radius} ${cy}`}
          fill="none"
          stroke="#e5e7eb"
          strokeWidth={stroke}
          strokeLinecap="round"
        />
        {/* Score arc */}
        <path
          d={`M ${cx - radius} ${cy} A ${radius} ${radius} 0 0 1 ${cx + radius} ${cy}`}
          fill="none"
          stroke={color}
          strokeWidth={stroke}
          strokeLinecap="round"
          strokeDasharray={`${dashArr}`}
          strokeDashoffset={`${dashOff}`}
          style={{ transition: "stroke-dashoffset 1s ease" }}
        />
        <text x={cx} y={cy - 10} textAnchor="middle" fontSize="36" fontWeight="bold" fill={color}>
          {score}
        </text>
        <text x={cx} y={cy + 12} textAnchor="middle" fontSize="13" fill="#6b7280">
          out of 100
        </text>
        {/* Labels */}
        <text x={cx - radius - 2} y={cy + 20} textAnchor="middle" fontSize="10" fill="#ef4444">Low</text>
        <text x={cx} y={cy + 20} textAnchor="middle" fontSize="10" fill="#f59e0b">Med</text>
        <text x={cx + radius + 2} y={cy + 20} textAnchor="middle" fontSize="10" fill="#22c55e">High</text>
      </svg>
    </div>
  );
}

function BreakdownBar({ label, value, color }) {
  return (
    <div className="breakdown-bar">
      <span className="breakdown-label">{label}</span>
      <div className="bar-track">
        <div className="bar-fill" style={{ width: `${value}%`, background: color }} />
      </div>
      <span className="breakdown-value">{value}</span>
    </div>
  );
}

function ProbabilityBadge({ label, value }) {
  const cfg = LABEL_CONFIG[label];
  return (
    <div className="prob-badge" style={{ borderColor: cfg.border, background: cfg.bg }}>
      <span className="prob-icon">{cfg.icon}</span>
      <span className="prob-label" style={{ color: cfg.color }}>{label}</span>
      <span className="prob-value">{value}%</span>
    </div>
  );
}

export default function ResultCard({ result }) {
  const { stability_score, score_label, probabilities, model_used, recommendations, breakdown } = result;
  const cfg = LABEL_CONFIG[score_label];
  const hasProbabilities = probabilities && Object.keys(probabilities).length > 0;

  const breakdownItems = [
    { label: "Consistency",   key: "consistency_component",   color: "#6366f1" },
    { label: "Income Level",  key: "income_component",        color: "#0ea5e9" },
    { label: "Volatility",    key: "volatility_component",    color: "#f59e0b" },
    { label: "Savings",       key: "savings_component",       color: "#22c55e" },
    { label: "Expenses",      key: "expense_component",       color: "#ec4899" },
    { label: "Late Payments", key: "late_payment_component",  color: "#ef4444" },
  ];

  return (
    <div className="result-card" style={{ borderColor: cfg.border }}>
      {/* Score header */}
      <div className="result-header" style={{ background: cfg.bg, borderBottom: `2px solid ${cfg.border}` }}>
        <div className="score-badge" style={{ background: cfg.color }}>
          {cfg.icon} {cfg.text}
        </div>
        <ScoreGauge score={stability_score} />
        <p className="model-info">Predicted by: <strong>{model_used}</strong></p>
      </div>

      {/* ML Probabilities */}
      {hasProbabilities && (
        <>
          <div className="result-section-title">ML Class Probabilities</div>
          <div className="prob-grid">
            {Object.entries(probabilities).sort().map(([lbl, val]) => (
              <ProbabilityBadge key={lbl} label={lbl} value={val} />
            ))}
          </div>
        </>
      )}

      {/* Score breakdown */}
      <div className="result-section-title">Score Breakdown</div>
      <div className="breakdown-list">
        {breakdownItems.map(({ label, key, color }) => (
          <BreakdownBar
            key={key}
            label={label}
            value={Math.round(breakdown[key])}
            color={color}
          />
        ))}
      </div>

      {/* Recommendations */}
      <div className="result-section-title">💡 Recommendations</div>
      <ul className="recs-list">
        {recommendations.map((rec, i) => (
          <li key={i} className="rec-item">
            <span className="rec-dot" style={{ background: cfg.color }} />
            {rec}
          </li>
        ))}
      </ul>

      {/* Loan guidance */}
      <div className="loan-box" style={{ borderColor: cfg.border, background: cfg.bg }}>
        <strong>🏦 Loan Decision Guidance:</strong>
        {score_label === "High" && " Worker demonstrates strong income stability. Loan approval recommended with standard terms."}
        {score_label === "Medium" && " Moderate stability. Consider conditional approval with a co-signer or smaller loan amount."}
        {score_label === "Low" && " Income instability detected. Advise the worker to improve financial habits before reapplying."}
      </div>
    </div>
  );
}
