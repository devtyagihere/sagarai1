import { ArrowRight, Clock3, FileText, Ship, TrendingUp } from "lucide-react";
import { useNavigate } from "react-router-dom";
import { getShipment } from "../services/shipmentStorage";

export default function DecisionHistory() {
  const navigate = useNavigate();
  const shipment = getShipment();

  const route = shipment
    ? `${shipment.origin} → ${shipment.destination}`
    : "No shipment selected";

  const cargo = shipment?.cargo || "—";
  const quantity = shipment?.quantity
    ? `${Number(shipment.quantity).toLocaleString()} tonnes`
    : "—";

  const delivery = shipment?.deliveryDate
    ? new Date(shipment.deliveryDate).toLocaleDateString("en-GB", {
        day: "2-digit",
        month: "short",
        year: "numeric",
      })
    : "—";

  const priority = shipment?.priority || "Normal";

  return (
    <section className="history-page">
      {/* HEADER */}
      <div className="history-header">
        <div>
          <p className="section-label">DECISION HISTORY</p>

          <h1>Review your shipment decisions.</h1>

          <p className="history-subtitle">
            Keep track of the shipment currently being evaluated and the
            decisions made along the way.
          </p>
        </div>

        <button
          className="secondary-action"
          onClick={() => navigate("/")}
        >
          New shipment
          <ArrowRight size={16} />
        </button>
      </div>

      {/* CURRENT SHIPMENT */}
      {shipment ? (
        <div className="history-current">
          <div className="history-current-icon">
            <Ship size={21} />
          </div>

          <div className="history-current-main">
            <span className="history-kicker">CURRENT SHIPMENT</span>

            <h2>{route}</h2>

            <p>
              {cargo} · {quantity} · Delivery {delivery}
            </p>
          </div>

          <div className="history-current-meta">
            <span>Priority</span>
            <strong>{priority}</strong>
          </div>
        </div>
      ) : (
        <div className="history-empty">
          <FileText size={24} />

          <div>
            <strong>No shipment has been analysed yet.</strong>
            <p>
              Start with a shipment on the home page to build its decision
              history.
            </p>
          </div>

          <button
            className="primary-action"
            onClick={() => navigate("/")}
          >
            Plan shipment
            <ArrowRight size={16} />
          </button>
        </div>
      )}

      {/* SUMMARY */}
      <div className="history-summary-grid">
        <div className="history-summary-card">
          <span className="history-summary-icon">
            <Clock3 size={18} />
          </span>

          <div>
            <strong>Current analysis</strong>
            <p>In progress</p>
          </div>
        </div>

        <div className="history-summary-card">
          <span className="history-summary-icon">
            <TrendingUp size={18} />
          </span>

          <div>
            <strong>Decision path</strong>
            <p>Forecast → Vessel → Port → Risk</p>
          </div>
        </div>

        <div className="history-summary-card">
          <span className="history-summary-icon">
            <FileText size={18} />
          </span>

          <div>
            <strong>Shipment record</strong>
            <p>{shipment ? "Saved locally" : "Not created"}</p>
          </div>
        </div>
      </div>

      {/* TIMELINE */}
      <div className="history-section">
        <div className="history-section-heading">
          <div>
            <p className="section-label">ANALYSIS TIMELINE</p>
            <h2>How the decision was built</h2>
          </div>
        </div>

        <div className="history-timeline">
          <div className="history-step completed">
            <div className="history-step-marker">01</div>

            <div className="history-step-content">
              <span>SHIPMENT INPUT</span>

              <h3>Shipment requirements captured</h3>

              <p>
                Route, cargo, quantity, delivery requirement and procurement
                priority were recorded.
              </p>
            </div>

            <strong>Completed</strong>
          </div>

          <div className="history-step completed">
            <div className="history-step-marker">02</div>

            <div className="history-step-content">
              <span>FREIGHT FORECAST</span>

              <h3>Market outlook prepared</h3>

              <p>
                The shipment is ready to be evaluated against freight-market
                conditions.
              </p>
            </div>

            <strong>Completed</strong>
          </div>

          <div className="history-step completed">
            <div className="history-step-marker">03</div>

            <div className="history-step-content">
              <span>VESSEL ECONOMICS</span>

              <h3>Vessel economics reviewed</h3>

              <p>
                Vessel selection and voyage economics are included in the
                decision path.
              </p>
            </div>

            <strong>Completed</strong>
          </div>

          <div className="history-step completed">
            <div className="history-step-marker">04</div>

            <div className="history-step-content">
              <span>PORT & RISK</span>

              <h3>Operational conditions considered</h3>

              <p>
                Port conditions and shipment risk are considered before the
                final recommendation.
              </p>
            </div>

            <strong>Completed</strong>
          </div>

          <div className="history-step current">
            <div className="history-step-marker">05</div>

            <div className="history-step-content">
              <span>DECISION</span>

              <h3>Final recommendation</h3>

              <p>
                Review the recommended course of action and compare alternative
                scenarios.
              </p>
            </div>

            <button
              className="history-step-action"
              onClick={() => navigate("/decision")}
            >
              Open
              <ArrowRight size={15} />
            </button>
          </div>
        </div>
      </div>

      {/* FOOTER ACTION */}
      <div className="history-footer">
        <div>
          <span className="history-kicker">READY TO CONTINUE?</span>

          <h2>
            {shipment
              ? "Continue analysing this shipment."
              : "Start a new shipment analysis."}
          </h2>
        </div>

        <button
          className="primary-action"
          onClick={() => navigate(shipment ? "/decision" : "/")}
        >
          {shipment ? "Continue to decision" : "Plan shipment"}
          <ArrowRight size={16} />
        </button>
      </div>
    </section>
  );
}