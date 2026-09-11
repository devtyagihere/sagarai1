import { useEffect, useState } from "react";
import {
  BrowserRouter,
  Routes,
  Route,
  Navigate,
  useLocation,
} from "react-router-dom";

import AppShell from "./layout/AppShell";

import Home from "./pages/Home";
import Overview from "./pages/Overview";
import FreightForecast from "./pages/FreightForecast";
import VesselEconomics from "./pages/VesselEconomics";
import PortIntelligence from "./pages/PortIntelligence";
import RiskCenter from "./pages/RiskCenter";
import DecisionEngine from "./pages/DecisionEngine";
import DecisionHistory from "./pages/DecisionHistory";
import ScenarioSimulator from "./pages/ScenarioSimulator";
import Signup from "./pages/auth/Signup";
import Login from "./pages/auth/Login";

function AppRoutes({ user, setUser }) {
  const location = useLocation();

  const isLoginPage = location.pathname === "/login";

  const handleLogin = (userData) => {
    setUser(userData);
  };

  const handleLogout = () => {
    localStorage.removeItem("freight_intelligence_current_user");
    setUser(null);
  };

  // User is NOT logged in
  if (!user) {
    return (
      <Routes>
        <Route
  path="/login"
  element={<Login onLogin={handleLogin} />}
/>

<Route
  path="/signup"
  element={<Signup onLogin={handleLogin} />}
/>
        {/* Every other page requires login */}
        <Route
          path="*"
          element={
            <Navigate
              to="/login"
              replace
            />
          }
        />
      </Routes>
    );
  }

  // User IS logged in
  return (
    <AppShell
      user={user}
      onLogout={handleLogout}
    >
      <Routes>

        {/* HOME */}
        <Route
          path="/"
          element={<Home />}
        />

        {/* OVERVIEW */}
        <Route
          path="/overview"
          element={<Overview />}
        />

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

        {/* DECISION / SHIPMENT HISTORY */}
        <Route
          path="/history"
          element={<DecisionHistory />}
        />

        {/* UNKNOWN URL */}
        <Route
          path="*"
          element={
            <Navigate
              to="/"
              replace
            />
          }
        />

      </Routes>
    </AppShell>
  );
}

function App() {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  // Restore logged-in user after refresh
  useEffect(() => {
    try {
      const savedUser = localStorage.getItem(
        "freight_intelligence_current_user"
      );

      if (savedUser) {
        setUser(JSON.parse(savedUser));
      }
    } catch (error) {
      console.error(
        "Unable to restore user session:",
        error
      );

      localStorage.removeItem(
        "freight_intelligence_current_user"
      );
    } finally {
      setLoading(false);
    }
  }, []);

  // Prevent a brief flash of the login page
  // while the saved session is being restored.
  if (loading) {
    return (
      <div className="app-loading">
        <div className="loading-mark">
          ⚓
        </div>

        <p>
          Loading Freight Intelligence...
        </p>
      </div>
    );
  }

  return (
    <BrowserRouter>
      <AppRoutes
        user={user}
        setUser={setUser}
      />
    </BrowserRouter>
  );
}

export default App;