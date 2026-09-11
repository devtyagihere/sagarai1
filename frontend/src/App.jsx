import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import AppShell from "./layout/AppShell";

import Home from "./pages/Home";
import Overview from "./pages/Overview";
import FreightForecast from "./pages/FreightForecast";
import VesselEconomics from "./pages/VesselEconomics";
import PortIntelligence from "./pages/PortIntelligence";
import RiskCenter from "./pages/RiskCenter";
import DecisionEngine from "./pages/DecisionEngine";
import ScenarioSimulator from "./pages/ScenarioSimulator";
import DecisionHistory from "./pages/DecisionHistory";

function App() {
  return (
    <BrowserRouter>
      <AppShell>
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/overview" element={<Overview />} />
          <Route path="/forecast" element={<FreightForecast />} />
          <Route path="/vessels" element={<VesselEconomics />} />
          <Route path="/ports" element={<PortIntelligence />} />
          <Route path="/risk" element={<RiskCenter />} />
          <Route path="/decision" element={<DecisionEngine />} />
          <Route path="/simulator" element={<ScenarioSimulator />} />
          <Route path="/history" element={<DecisionHistory />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </AppShell>
    </BrowserRouter>
  );
}

export default App;