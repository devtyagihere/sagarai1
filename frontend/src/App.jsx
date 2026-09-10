import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";

import AppShell from "./layout/AppShell";
import Home from "./pages/Home";
import Overview from "./pages/Overview";
import FreightForecast from "./pages/FreightForecast";
import VesselEconomics from "./pages/VesselEconomics";
import PortIntelligence from "./pages/PortIntelligence";
import RiskCenter from "./pages/RiskCenter";
import DecisionEngine from "./pages/DecisionEngine";
import DecisionHistory from "./pages/DecisionHistory";

function PlaceholderPage({ title }) {
  return (
    <section className="placeholder-page">
      <p className="placeholder-label">MARITIME FREIGHT</p>

      <h1>{title}</h1>

      <p>
        This section will be built as part of the decision
        support system.
      </p>
    </section>
  );
}

function App() {
  return (
    <BrowserRouter>
      <AppShell>
        <Routes>
          {/* HOME */}
          <Route path="/" element={<Home />} />

          {/* OVERVIEW */}
          <Route path="/overview" element={<Overview />} />

          {/* FREIGHT FORECAST */}
          <Route
  path="/forecast"
  element={<FreightForecast />}
/>

          {/* VESSEL ECONOMICS */}
          <Route
  path="/vessels"
  element={<VesselEconomics />}
/>

          {/* PORT INTELLIGENCE */}
          <Route
  path="/ports"
  element={<PortIntelligence />}
/>

          {/* RISK CENTER */}
          <Route
  path="/risk"
  element={<RiskCenter />}
/>

          {/* DECISION ENGINE */}
          <Route
  path="/decision"
  element={<DecisionEngine />}
/>

          {/* SCENARIO SIMULATOR */}
          <Route
  path="/simulator"
  element={<ScenarioSimulator />}
/>

          {/* DECISION HISTORY */}
          <Route
  path="/history"
  element={<DecisionHistory />}
/>

          {/* UNKNOWN URL */}
          <Route
            path="*"
            element={<Navigate to="/" replace />}
          />
        </Routes>
      </AppShell>
    </BrowserRouter>
  );
}

export default App;