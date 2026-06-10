import React from "react";

export default function Header() {
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
    </header>
  );
}
