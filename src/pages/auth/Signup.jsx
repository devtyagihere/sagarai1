import { useState } from "react";
import { useNavigate } from "react-router-dom";
import {
  Ship,
  ArrowRight,
  Lock,
  Mail,
  User,
} from "lucide-react";
import { signupUser } from "../../services/authStorage";

export default function Signup({ onLogin }) {
  const navigate = useNavigate();

  const [form, setForm] = useState({
    name: "",
    email: "",
    password: "",
    confirmPassword: "",
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

    if (
      !form.name.trim() ||
      !form.email.trim() ||
      !form.password ||
      !form.confirmPassword
    ) {
      setError("Please complete all fields.");
      return;
    }

    if (form.password.length < 6) {
      setError("Password must be at least 6 characters.");
      return;
    }

    if (form.password !== form.confirmPassword) {
      setError("Passwords do not match.");
      return;
    }

    setLoading(true);

    try {
      const newUser = signupUser({
        name: form.name,
        email: form.email,
        password: form.password,
      });

      onLogin(newUser);

      navigate("/", {
        replace: true,
      });
    } catch (signupError) {
      setError(signupError.message);
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
              CREATE WORKSPACE
            </p>

            <h1>
              Start your voyage.
            </h1>

            <p>
              Create your account to manage shipments,
              analyse freight markets and keep your
              decision history.
            </p>
          </div>

          <form onSubmit={handleSubmit}>

            <div className="login-field">
              <label>Full name</label>

              <div className="login-input">
                <User size={17} />

                <input
                  type="text"
                  placeholder="Your name"
                  value={form.name}
                  onChange={(event) =>
                    updateField(
                      "name",
                      event.target.value
                    )
                  }
                />
              </div>
            </div>

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
                  placeholder="Minimum 6 characters"
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

            <div className="login-field">
              <label>Confirm password</label>

              <div className="login-input">
                <Lock size={17} />

                <input
                  type="password"
                  placeholder="Repeat your password"
                  value={form.confirmPassword}
                  onChange={(event) =>
                    updateField(
                      "confirmPassword",
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
                ? "Creating account..."
                : "Create account"}

              {!loading && (
                <ArrowRight size={18} />
              )}
            </button>

          </form>

          <div className="login-footer">
            <span>
              Already have an account?
            </span>

            <button
              type="button"
              onClick={() => navigate("/login")}
            >
              Sign in
            </button>
          </div>

        </div>

        <div className="login-note">
          Your voyage activity will be stored in your
          personal workspace.
        </div>

      </div>
    </div>
  );
}