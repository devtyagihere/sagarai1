import { Menu, Bell, CircleUserRound } from "lucide-react";
import { useNavigate } from "react-router-dom";
import SagarLogo from "../components/SagarLogo";

export default function TopBar({ onMenuClick }) {
  const navigate = useNavigate();

  return (
    <header className="topbar">
      <div className="topbar-left">
        <button
          className="menu-button"
          onClick={onMenuClick}
          aria-label="Open navigation"
        >
          <Menu size={23} strokeWidth={1.8} />
        </button>

        {/* Clicking the brand takes you back to the landing page */}
        <button
          className="topbar-home-btn"
          onClick={() => navigate("/")}
          aria-label="Go to landing page"
          title="Back to Home"
        >
          <SagarLogo size={20} />
          <span className="topbar-home-label">Home</span>
        </button>

        <div className="topbar-title">
          <span className="topbar-eyebrow">
            SAGARAI OPERATIONS
          </span>

          <span className="topbar-page-title">
            SagarAI Decision Support
          </span>
        </div>
      </div>

      <div className="topbar-right">
        <div className="connection-status">
          <span className="connection-dot" />
          <span>System Online</span>
        </div>

        <button className="topbar-icon-button" aria-label="Notifications">
          <Bell size={18} strokeWidth={1.8} />
        </button>

        <button className="profile-button" aria-label="User profile">
          <CircleUserRound size={20} strokeWidth={1.7} />
        </button>
      </div>
    </header>
  );
}