import { Menu, Bell, CircleUserRound } from "lucide-react";

export default function TopBar({ onMenuClick }) {
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

        <div className="topbar-title">
          <span className="topbar-eyebrow">
            MARITIME OPERATIONS
          </span>

          <span className="topbar-page-title">
            Freight Decision Support
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