import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { Lock, Mail, ArrowRight, ShieldCheck, Eye, EyeOff, UserCheck } from "lucide-react";
import SagarLogo from "../components/SagarLogo";
import "../styles/landing.css";

export default function LandingPage() {
  const navigate = useNavigate();
  const [email, setEmail] = useState("chartering@maritime-ops.com");
  const [password, setPassword] = useState("••••••••••••");
  const [showPassword, setShowPassword] = useState(false);
  const [rememberMe, setRememberMe] = useState(true);

  const handleLogin = (e) => {
    e?.preventDefault();
    navigate("/plan");
  };

  return (
    <div className="lp-video-root">
      {/* ── Fullscreen Background Video ── */}
      <div className="lp-video-container">
        <video
          className="lp-bg-video"
          autoPlay
          loop
          muted
          playsInline
          poster="/favicon.svg"
        >
          <source src="/ship-bg.mp4" type="video/mp4" />
          Your browser does not support the video tag.
        </video>
        {/* Cinematic Gradient Overlays */}
        <div className="lp-video-overlay" />
      </div>

      {/* ── Top Header / Status Bar ── */}
      <header className="lp-topbar">
        <div />
        <div className="lp-top-status">
          <span className="lp-status-pulse" />
          <span>22 Port Networks Online</span>
        </div>
      </header>

      {/* ── Main Layout: Left Login Portal Stack ── */}
      <main className="lp-main-split">
        {/* ── LEFT: Aligned Brand + Login Card ── */}
        <div className="lp-login-col">
          <div className="lp-brand-badge">
            <div className="lp-brand-icon">
              <SagarLogo size={22} />
            </div>
            <div className="lp-brand-titles">
              <strong>SagarAI</strong>
              <span>Maritime Freight Decision Intelligence</span>
            </div>
          </div>

          <div className="lp-login-card">
            <div className="lp-card-header">
              <div className="lp-badge-tag">
                <ShieldCheck size={14} />
                <span>ENTERPRISE PORTAL</span>
              </div>
              <h2>Sign in to SagarAI</h2>
              <p>Access AI freight forecasting, vessel economics &amp; real-time port risk models.</p>
            </div>

            <form className="lp-login-form" onSubmit={handleLogin}>
              <div className="lp-field-group">
                <label htmlFor="lp-email">Work Email</label>
                <div className="lp-input-wrap">
                  <Mail size={17} className="lp-input-icon" />
                  <input
                    id="lp-email"
                    type="email"
                    required
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    placeholder="name@chartering-co.com"
                  />
                </div>
              </div>

              <div className="lp-field-group">
                <div className="lp-field-label-row">
                  <label htmlFor="lp-pass">Password</label>
                  <a href="#forgot" onClick={(e) => { e.preventDefault(); navigate("/plan"); }} className="lp-forgot-link">
                    Demo Access
                  </a>
                </div>
                <div className="lp-input-wrap">
                  <Lock size={17} className="lp-input-icon" />
                  <input
                    id="lp-pass"
                    type={showPassword ? "text" : "password"}
                    required
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    placeholder="Enter security key"
                  />
                  <button
                    type="button"
                    className="lp-pw-toggle"
                    onClick={() => setShowPassword(!showPassword)}
                    aria-label="Toggle password visibility"
                  >
                    {showPassword ? <EyeOff size={16} /> : <Eye size={16} />}
                  </button>
                </div>
              </div>

              <div className="lp-form-row">
                <label className="lp-checkbox-label">
                  <input
                    type="checkbox"
                    checked={rememberMe}
                    onChange={(e) => setRememberMe(e.target.checked)}
                  />
                  <span>Keep session active</span>
                </label>
              </div>

              <button type="submit" className="lp-submit-btn">
                <span>Sign In to Decision Suite</span>
                <ArrowRight size={18} />
              </button>

              <div className="lp-or-divider">
                <span>OR EXPLORE INSTANTLY</span>
              </div>

              <button
                type="button"
                className="lp-guest-btn"
                onClick={() => navigate("/plan")}
              >
                <UserCheck size={17} />
                <span>Continue as Guest / Planner</span>
              </button>
            </form>

            <div className="lp-card-footer">
              <span>🔒 256-Bit Maritime Protocol</span>
              <span>•</span>
              <span>22 Verified Hubs</span>
              <span>•</span>
              <span>Dry Bulk AI Engine</span>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
