import { useState } from "react";
import { useNavigate } from "react-router-dom";

import Sidebar from "./Sidebar";
import TopBar from "./TopBar";

export default function AppShell({ children }) {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const navigate = useNavigate();

  const handleNavigate = (path) => {
    navigate(path);
    setSidebarOpen(false);
  };

  return (
    <div className="app-shell">
      <Sidebar
        open={sidebarOpen}
        onClose={() => setSidebarOpen(false)}
        onNavigate={handleNavigate}
      />

      <div className="app-main">
        <TopBar
          onMenuClick={() => setSidebarOpen(true)}
        />

        <main className="page-content">
          {children}
        </main>
      </div>
    </div>
  );
}