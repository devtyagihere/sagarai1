import React from "react";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import AppShell from "./layout/AppShell";

import LandingPage from "./pages/LandingPage";
import Home from "./pages/Home";
import Overview from "./pages/Overview";
import FreightForecast from "./pages/FreightForecast";
import VesselEconomics from "./pages/VesselEconomics";
import PortIntelligence from "./pages/PortIntelligence";
import RiskCenter from "./pages/RiskCenter";
import DecisionEngine from "./pages/DecisionEngine";
import ScenarioSimulator from "./pages/ScenarioSimulator";
import DecisionHistory from "./pages/DecisionHistory";
import ScrollToTop from "./components/ScrollToTop";
import "./styles/interactive.css";

class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null };
  }
  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }
  componentDidCatch(error, errorInfo) {
    console.error("ErrorBoundary caught an error:", error, errorInfo);
  }
  render() {
    if (this.state.hasError) {
      return (
        <div style={{ padding: "48px 24px", textAlign: "center", maxWidth: 600, margin: "40px auto" }}>
          <h2 style={{ fontSize: "1.5rem", fontWeight: 600, marginBottom: "12px", color: "#111827" }}>
            Shipment Analysis Ready
          </h2>
          <p style={{ color: "#4b5563", marginBottom: "24px" }}>
            The workspace encountered an unexpected display issue. Click below to return to the planner.
          </p>
          <button
            type="button"
            onClick={() => {
              this.setState({ hasError: false });
              window.location.href = "/plan";
            }}
            style={{
              padding: "10px 24px",
              backgroundColor: "#0f766e",
              color: "#ffffff",
              border: "none",
              borderRadius: "8px",
              fontWeight: 500,
              cursor: "pointer",
            }}
          >
            Plan Another Shipment
          </button>
        </div>
      );
    }
    return this.props.children;
  }
}

function App() {
  return (
    <BrowserRouter>
      <ScrollToTop />
      <Routes>
        {/* Landing page – full screen, no sidebar/topbar */}
        <Route path="/" element={<LandingPage />} />

        {/* App shell wraps all inner routes */}
        <Route
          path="/*"
          element={
            <AppShell>
              <ErrorBoundary>
                <Routes>
                  <Route path="/plan" element={<Home />} />
                  <Route path="/overview" element={<Overview />} />
                  <Route path="/forecast" element={<FreightForecast />} />
                  <Route path="/vessels" element={<VesselEconomics />} />
                  <Route path="/ports" element={<PortIntelligence />} />
                  <Route path="/risk" element={<RiskCenter />} />
                  <Route path="/decision" element={<DecisionEngine />} />
                  <Route path="/simulator" element={<ScenarioSimulator />} />
                  <Route path="/history" element={<DecisionHistory />} />
                  <Route path="*" element={<Navigate to="/plan" replace />} />
                </Routes>
              </ErrorBoundary>
            </AppShell>
          }
        />
      </Routes>
    </BrowserRouter>
  );
}

export default App;