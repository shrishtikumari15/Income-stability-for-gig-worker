import React, { useState } from "react";
import PredictionForm from "./components/PredictionForm";
import ResultCard from "./components/ResultCard";
import Header from "./components/Header";
import "./App.css";

const API_BASE = process.env.REACT_APP_API_URL || "http://localhost:5000";

const FUTURE_ITEMS = [
  {
    title: "Real-Time Data Integration",
    text: "Connect bank statements, platform earnings, UPI transactions, or gig platform APIs to reduce manual entry.",
  },
  {
    title: "Explainable AI",
    text: "Show which factors most affected a worker's result so users and lenders can understand the decision.",
  },
  {
    title: "Personalised Recommendations",
    text: "Generate targeted improvement plans based on weak areas such as savings, volatility, or late payments.",
  },
  {
    title: "Model Monitoring",
    text: "Track prediction drift, retrain models with fresh data, and compare model performance over time.",
  },
  {
    title: "Secure User Accounts",
    text: "Add authentication, saved reports, encrypted financial data, and role-based lender dashboards.",
  },
  {
    title: "Loan Product Matching",
    text: "Map stability scores to suitable credit limits, interest ranges, repayment terms, and risk categories.",
  },
];

function LearnPage() {
  return (
    <div className="info-page">
      <section className="info-hero">
        <span className="info-kicker">Project overview</span>
        <h2>Income Stability Score for Gig Workers</h2>
        <p>
          This project estimates how stable a gig worker's income is by combining financial behaviour,
          work consistency, recovery from income dips, and machine learning predictions.
        </p>
      </section>

      <section className="info-grid three">
        <div className="info-card">
          <span className="info-number">10,000</span>
          <h3>Dataset Records</h3>
          <p>Worker-level samples with income, work pattern, savings, expense, and payment behaviour fields.</p>
        </div>
        <div className="info-card">
          <span className="info-number">16</span>
          <h3>Model Features</h3>
          <p>Engineered signals include average income, recovery efficiency, savings rate, and job efficiency.</p>
        </div>
        <div className="info-card">
          <span className="info-number">3</span>
          <h3>ML Models</h3>
          <p>Random Forest, Logistic Regression, and Linear Regression are available for comparison.</p>
        </div>
      </section>

      <section className="info-split">
        <div className="info-panel">
          <h3>How The Score Works</h3>
          <p>
            The app calculates a stability score from 0 to 100 using weighted components. Higher values
            represent stronger income stability and better repayment confidence.
          </p>
          <div className="metric-list">
            <span>Work consistency</span>
            <span>Average income</span>
            <span>Income volatility</span>
            <span>Surplus ratio</span>
            <span>Savings behaviour</span>
            <span>Expense control</span>
            <span>Late payments</span>
            <span>Recovery speed</span>
          </div>
        </div>

        <div className="info-panel">
          <h3>Dataset Fields</h3>
          <div className="dataset-table">
            <div><strong>Income</strong><span>monthly income, last month income, average daily income, income growth</span></div>
            <div><strong>Work</strong><span>working days, jobs completed, platform count, consistency score</span></div>
            <div><strong>Risk</strong><span>income volatility, days to recover, late payment count</span></div>
            <div><strong>Finance</strong><span>surplus ratio, expense ratio, savings amount</span></div>
          </div>
        </div>
      </section>

      <section className="info-panel">
        <h3>Model Output</h3>
        <p>
          Classification models return Low, Medium, or High stability with class probabilities. Linear
          Regression predicts a numeric stability score, which is mapped into the same labels for a
          consistent user experience.
        </p>
      </section>
    </div>
  );
}

function FuturePage() {
  return (
    <div className="info-page">
      <section className="info-hero">
        <span className="info-kicker">Future scope</span>
        <h2>Where This Project Can Grow Next</h2>
        <p>
          The current version proves the scoring concept. Future work can improve accuracy, trust,
          deployment quality, and real banking use cases.
        </p>
      </section>

      <section className="timeline">
        {FUTURE_ITEMS.map((item, index) => (
          <div className="timeline-item" key={item.title}>
            <span className="timeline-index">{String(index + 1).padStart(2, "0")}</span>
            <div>
              <h3>{item.title}</h3>
              <p>{item.text}</p>
            </div>
          </div>
        ))}
      </section>
    </div>
  );
}

function App() {
  const [activePage, setActivePage] = useState("predict");
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [modelInfo, setModelInfo] = useState(null);

  React.useEffect(() => {
    fetch(`${API_BASE}/api/model-info`)
      .then((res) => (res.ok ? res.json() : null))
      .then((data) => setModelInfo(data))
      .catch(() => setModelInfo(null));
  }, []);

  const handleSubmit = async (formData) => {
    setLoading(true);
    setError(null);
    setResult(null);
    try {
      const res = await fetch(`${API_BASE}/api/predict`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(formData),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.error || "Server error");
      setResult(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="app">
      <Header activePage={activePage} onPageChange={setActivePage} />
      <main className="main-content">
        <div className="container">
          {activePage === "predict" && (
            <div className="layout">
              <section className="form-section">
                <PredictionForm onSubmit={handleSubmit} loading={loading} modelInfo={modelInfo} />
              </section>
              <section className="result-section">
                {error && (
                  <div className="error-card">
                    <span>Warning: {error}</span>
                  </div>
                )}
                {result && <ResultCard result={result} />}
                {!result && !error && (
                  <div className="placeholder-card">
                    <div className="placeholder-icon">Score</div>
                    <h3>Your Stability Score</h3>
                    <p>Fill in the gig worker details on the left and click <strong>Analyse</strong> to generate an AI-powered income stability score.</p>
                  </div>
                )}
              </section>
            </div>
          )}
          {activePage === "learn" && <LearnPage />}
          {activePage === "future" && <FuturePage />}
        </div>
      </main>
      <footer className="footer">
        <p>AI-Based Income Stability Score for Gig Workers &nbsp;|&nbsp; Banking & Finance Project &nbsp;|&nbsp; Powered by Random Forest, Logistic Regression &amp; Linear Regression</p>
      </footer>
    </div>
  );
}

export default App;
