import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";

import AppShell from "./layout/AppShell";
import Home from "./pages/Home";

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
          <Route path="/" element={<Home />} />

          <Route
            path="/overview"
            element={<PlaceholderPage title="Shipment Overview" />}
          />

          <Route
            path="/forecast"
            element={<PlaceholderPage title="Freight Forecast" />}
          />

          <Route
            path="/vessels"
            element={<PlaceholderPage title="Vessel Economics" />}
          />

          <Route
            path="/ports"
            element={<PlaceholderPage title="Port Intelligence" />}
          />

          <Route
            path="/risk"
            element={<PlaceholderPage title="Risk Center" />}
          />

          <Route
            path="/decision"
            element={<PlaceholderPage title="Decision Engine" />}
          />

          <Route
            path="/simulator"
            element={<PlaceholderPage title="Scenario Simulator" />}
          />

          <Route
            path="/history"
            element={<PlaceholderPage title="Decision History" />}
          />

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