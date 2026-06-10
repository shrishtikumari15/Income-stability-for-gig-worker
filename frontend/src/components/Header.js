import React from "react";

const NAV_ITEMS = [
  { key: "predict", label: "Predict" },
  { key: "learn", label: "Project & Dataset" },
  { key: "future", label: "Future Scope" },
];

export default function Header({ activePage, onPageChange }) {
  return (
    <header className="header">
      <div className="header-inner">
        <div className="logo">
          <span className="logo-icon">🏦</span>
          <div>
            <h1 className="logo-title">GigScore AI</h1>
            <p className="logo-subtitle">Income Stability Analyser for Gig Workers</p>
          </div>
        </div>
        <div className="header-badge">
          <span className="badge">Banking &amp; Finance</span>
          <span className="badge ml">ML Powered</span>
        </div>
      </div>
      <nav className="top-nav" aria-label="Primary navigation">
        {NAV_ITEMS.map((item) => (
          <button
            key={item.key}
            type="button"
            className={`nav-btn ${activePage === item.key ? "active" : ""}`}
            onClick={() => onPageChange(item.key)}
          >
            {item.label}
          </button>
        ))}
      </nav>
    </header>
  );
}
