import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { Ship, ArrowRight, Lock, Mail } from "lucide-react";
import { loginUser } from "../../services/authStorage";

export default function Login({ onLogin }) {
  const navigate = useNavigate();

  const [form, setForm] = useState({
    email: "",
    password: "",
  });

  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const updateField = (field, value) => {
    setForm((previous) => ({
      ...previous,
      [field]: value,
    }));
  };

  const handleSubmit = (event) => {
    event.preventDefault();

    setError("");

    if (!form.email.trim() || !form.password) {
      setError("Please enter your email and password.");
      return;
    }

    setLoading(true);

    try {
      const loggedInUser = loginUser(form);

onLogin(loggedInUser);

navigate("/", {
  replace: true,
});
    } catch (loginError) {
      setError(loginError.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="login-page">
      <div className="login-shell">

        <div className="login-brand">
          <div className="login-logo">
            <Ship size={26} strokeWidth={1.8} />
          </div>

          <div>
            <strong>Freight Intelligence</strong>
            <span>Maritime decision platform</span>
          </div>
        </div>

        <div className="login-card">

          <div className="login-header">
            <p className="section-label">
              SECURE ACCESS
            </p>

            <h1>
              Welcome back.
            </h1>

            <p>
              Sign in to manage your voyages, analyse
              freight markets and review shipment history.
            </p>
          </div>

          <form onSubmit={handleSubmit}>

            <div className="login-field">
              <label>Email address</label>

              <div className="login-input">
                <Mail size={17} />

                <input
                  type="email"
                  placeholder="you@example.com"
                  value={form.email}
                  onChange={(event) =>
                    updateField(
                      "email",
                      event.target.value
                    )
                  }
                />
              </div>
            </div>

            <div className="login-field">
              <label>Password</label>

              <div className="login-input">
                <Lock size={17} />

                <input
                  type="password"
                  placeholder="Enter your password"
                  value={form.password}
                  onChange={(event) =>
                    updateField(
                      "password",
                      event.target.value
                    )
                  }
                />
              </div>
            </div>

            {error && (
              <div className="login-error">
                {error}
              </div>
            )}

            <button
              type="submit"
              className="login-button"
              disabled={loading}
            >
              {loading
                ? "Signing in..."
                : "Sign in"}

              {!loading && (
                <ArrowRight size={18} />
              )}
            </button>

          </form>

          <div className="login-footer">
            <span>
              New to Freight Intelligence?
            </span>

            <button
              type="button"
              onClick={() => navigate("/signup")}
            >
              Create account
            </button>
          </div>

        </div>

        <div className="login-note">
          Your workspace keeps your voyage activity
          separate from other users.
        </div>

      </div>
    </div>
  );
}