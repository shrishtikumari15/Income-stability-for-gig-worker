import React, { useState } from "react";
import PredictionForm from "./components/PredictionForm";
import ResultCard from "./components/ResultCard";
import Header from "./components/Header";
import "./App.css";

const API_BASE = process.env.REACT_APP_API_URL || "http://localhost:5000";

function App() {
  const [result, setResult]   = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError]     = useState(null);

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
      <Header />
      <main className="main-content">
        <div className="container">
          <div className="layout">
            <section className="form-section">
              <PredictionForm onSubmit={handleSubmit} loading={loading} />
            </section>
            <section className="result-section">
              {error && (
                <div className="error-card">
                  <span>⚠️ {error}</span>
                </div>
              )}
              {result && <ResultCard result={result} />}
              {!result && !error && (
                <div className="placeholder-card">
                  <div className="placeholder-icon">📊</div>
                  <h3>Your Stability Score</h3>
                  <p>Fill in the gig worker details on the left and click <strong>Analyse</strong> to generate an AI-powered income stability score.</p>
                </div>
              )}
            </section>
          </div>
        </div>
      </main>
      <footer className="footer">
        <p>AI-Based Income Stability Score for Gig Workers &nbsp;|&nbsp; Banking & Finance Project &nbsp;|&nbsp; Powered by Random Forest, Logistic Regression &amp; Linear Regression</p>
      </footer>
    </div>
  );
}

export default App;
