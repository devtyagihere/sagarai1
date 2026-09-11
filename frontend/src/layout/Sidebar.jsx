import {
  LayoutDashboard,
  TrendingUp,
  Ship,
  Anchor,
  Waves,
  Target,
  GitCompare,
  History,
  Settings,
  X,
  ChevronRight,
} from "lucide-react";

const mainNavigation = [
  {
    label: "Overview",
    path: "/overview",
    icon: LayoutDashboard,
  },
];

const intelligenceNavigation = [
  {
    label: "Freight Forecast",
    path: "/forecast",
    icon: TrendingUp,
  },
  {
    label: "Vessel Economics",
    path: "/vessels",
    icon: Ship,
  },
  {
    label: "Port Intelligence",
    path: "/ports",
    icon: Anchor,
  },
  {
    label: "Risk Center",
    path: "/risk",
    icon: Waves,
  },
];

const decisionNavigation = [
  {
    label: "Decision Engine",
    path: "/decision",
    icon: Target,
  },
  {
    label: "Scenario Simulator",
    path: "/simulator",
    icon: GitCompare,
  },
  {
    label: "Decision History",
    path: "/history",
    icon: History,
  },
];

function NavItem({ item, onNavigate }) {
  const Icon = item.icon;

  return (
    <button
      className="sidebar-nav-item"
      onClick={() => onNavigate(item.path)}
    >
      <Icon size={18} strokeWidth={1.8} />
      <span>{item.label}</span>
      <ChevronRight className="nav-chevron" size={15} />
    </button>
  );
}

export default function Sidebar({ open, onClose, onNavigate }) {
  return (
    <>
      {open && (
        <div
          className="sidebar-overlay"
          onClick={onClose}
        />
      )}

      <aside className={`sidebar ${open ? "sidebar-open" : ""}`}>
        <div className="sidebar-header">
          <div className="brand-mark">
            <Anchor size={22} strokeWidth={2} />
          </div>

          <div className="brand-text">
            <strong>Maritime Freight</strong>
            <span>Decision Support</span>
          </div>

          <button
            className="sidebar-close"
            onClick={onClose}
            aria-label="Close navigation"
          >
            <X size={19} />
          </button>
        </div>

        <div className="sidebar-content">
          <div className="sidebar-section">
            <p className="sidebar-section-title">MAIN</p>

            {mainNavigation.map((item) => (
              <NavItem
                key={item.path}
                item={item}
                onNavigate={onNavigate}
              />
            ))}
          </div>

          <div className="sidebar-section">
            <p className="sidebar-section-title">INTELLIGENCE</p>

            {intelligenceNavigation.map((item) => (
              <NavItem
                key={item.path}
                item={item}
                onNavigate={onNavigate}
              />
            ))}
          </div>

          <div className="sidebar-section">
            <p className="sidebar-section-title">DECISION</p>

            {decisionNavigation.map((item) => (
              <NavItem
                key={item.path}
                item={item}
                onNavigate={onNavigate}
              />
            ))}
          </div>

          <div className="sidebar-section sidebar-bottom-section">
            <p className="sidebar-section-title">SYSTEM</p>

            <button className="sidebar-nav-item">
              <Settings size={18} strokeWidth={1.8} />
              <span>Settings</span>
            </button>
          </div>
        </div>

        <div className="sidebar-status">
          <div className="status-dot" />

          <div>
            <strong>System Online</strong>
            <span>Decision engine ready</span>
          </div>
        </div>
      </aside>
    </>
  );
}