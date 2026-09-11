import {
  ArrowRight,
  ArrowUpRight,
  CalendarDays,
  CircleAlert,
  Fuel,
  MapPin,
  Ship,
  TrendingUp,
} from "lucide-react";
import { useNavigate } from "react-router-dom";
import { getShipment } from "../services/shipmentStorage";

export default function Overview() {
  const navigate = useNavigate();
  const shipment = getShipment();

  // If no shipment has been created yet, send the user back to Home.
  if (!shipment) {
    return (
      <div className="overview-page">
        <section className="overview-header">
          <div>
            <p className="section-label">SHIPMENT OVERVIEW</p>
            <h1>No shipment planned yet.</h1>
            <p>
              Start by entering your shipment details so the decision workspace
              can be prepared for you.
            </p>

            <button
              className="text-action"
              onClick={() => navigate("/")}
              type="button"
            >
              Plan a shipment
              <ArrowRight size={16} />
            </button>
          </div>
        </section>
      </div>
    );
  }

  const {
    origin,
    destination,
    cargo,
    quantity,
    deliveryDate,
    contractDuration,
    priority,
  } = shipment;

  return (
    <div className="overview-page">

      {/* HEADER */}

      <section className="overview-header">
        <div>
          <p className="section-label">SHIPMENT OVERVIEW</p>

          <h1>Your freight at a glance.</h1>

          <p>
            A quick operational view of the market, shipment,
            and signals influencing your next chartering decision.
          </p>
        </div>

        <div className="overview-date">
          <CalendarDays size={16} />
          <span>Planning workspace</span>
        </div>
      </section>


      {/* SHIPMENT CARD */}

      <section className="overview-shipment">

        <div className="overview-section-heading">
          <div>
            <p className="section-label">CURRENT SHIPMENT</p>
            <h2>Voyage plan</h2>
          </div>

          <span className="planning-status">
            Planning
          </span>
        </div>


        <div className="voyage-route">

          <div className="voyage-port">
            <span>ORIGIN</span>

            <strong>{origin}</strong>

            <small>Departure port</small>
          </div>


          <div className="voyage-line">
            <div className="voyage-line-track" />
            <Ship size={22} />
            <ArrowRight size={18} />
          </div>


          <div className="voyage-port destination">
            <span>DESTINATION</span>

            <strong>{destination}</strong>

            <small>Discharge port</small>
          </div>

        </div>


        <div className="shipment-metrics">

          <div>
            <span>CARGO</span>
            <strong>{cargo}</strong>
          </div>

          <div>
            <span>QUANTITY</span>
            <strong>{Number(quantity).toLocaleString()} MT</strong>
          </div>

          <div>
            <span>DELIVERY</span>
            <strong>{deliveryDate}</strong>
          </div>

          <div>
            <span>PRIORITY</span>
            <strong>{priority}</strong>
          </div>

        </div>


        <div className="shipment-extra">

          <div>
            <span>CONTRACT</span>
            <strong>{contractDuration}</strong>
          </div>

          <div>
            <span>ROUTE</span>
            <strong>
              {origin} → {destination}
            </strong>
          </div>

        </div>

      </section>


      {/* FREIGHT OUTLOOK */}

      <section className="overview-section">

        <div className="overview-section-heading">
          <div>
            <p className="section-label">FREIGHT OUTLOOK</p>

            <h2>Where the market is heading</h2>
          </div>

          <button
            className="text-action"
            onClick={() => navigate("/forecast")}
            type="button"
          >
            View forecast
            <ArrowRight size={16} />
          </button>
        </div>


        <div className="forecast-overview-grid">

          <div className="overview-rate-card">

            <div className="card-label">
              CURRENT FREIGHT RATE
            </div>

            <div className="rate-value">
              $24.50
            </div>

            <div className="rate-unit">
              USD / MT
            </div>

            <div className="rate-change positive">
              <ArrowUpRight size={16} />
              3.8% this week
            </div>

          </div>


          <div className="overview-rate-card">

            <div className="card-label">
              NEXT WEEK
            </div>

            <div className="rate-value">
              $25.10
            </div>

            <div className="rate-unit">
              Forecast
            </div>

            <div className="rate-change warning">
              <ArrowUpRight size={16} />
              Expected increase
            </div>

          </div>


          <div className="forecast-direction-card">

            <div className="card-label">
              MARKET DIRECTION
            </div>

            <div className="direction-icon">
              <TrendingUp size={24} />
            </div>

            <strong>Moderately rising</strong>

            <p>
              Freight conditions currently favour
              watching the market before fixing.
            </p>

          </div>

        </div>

      </section>


      {/* MARKET SIGNALS */}

      <section className="overview-section">

        <div className="overview-section-heading">

          <div>
            <p className="section-label">
              MARKET SIGNALS
            </p>

            <h2>What is influencing the decision</h2>
          </div>

        </div>


        <div className="signal-grid">

          <div className="signal-card">

            <div className="signal-icon">
              <TrendingUp size={19} />
            </div>

            <div>
              <span>BDI</span>

              <strong>1,842</strong>

              <p className="positive">
                +5.2% this week
              </p>
            </div>

          </div>


          <div className="signal-card">

            <div className="signal-icon">
              <Fuel size={19} />
            </div>

            <div>
              <span>FUEL</span>

              <strong>$78.20</strong>

              <p>
                USD / barrel
              </p>
            </div>

          </div>


          <div className="signal-card">

            <div className="signal-icon">
              <Ship size={19} />
            </div>

            <div>
              <span>VESSEL SUPPLY</span>

              <strong>Balanced</strong>

              <p>
                Current market
              </p>
            </div>

          </div>


          <div className="signal-card">

            <div className="signal-icon">
              <MapPin size={19} />
            </div>

            <div>
              <span>PORT ACTIVITY</span>

              <strong>Moderate</strong>

              <p>
                Across monitored ports
              </p>
            </div>

          </div>

        </div>

      </section>


      {/* DECISION STATUS */}

      <section className="decision-overview">

        <div className="decision-copy">

          <p className="section-label">
            DECISION READINESS
          </p>

          <h2>
            Three areas are being evaluated
          </h2>

          <p>
            The final recommendation will combine freight
            market conditions, vessel economics and
            operational risk.
          </p>

        </div>


        <div className="decision-status-grid">

          <div className="decision-status">

            <div className="decision-status-top">
              <span>01</span>
              <TrendingUp size={18} />
            </div>

            <strong>Freight market</strong>

            <p>
              Market data available
            </p>

            <span className="status-ready">
              Ready
            </span>

          </div>


          <div className="decision-status">

            <div className="decision-status-top">
              <span>02</span>
              <Ship size={18} />
            </div>

            <strong>Vessel economics</strong>

            <p>
              Vessel comparison required
            </p>

            <span className="status-ready">
              Ready
            </span>

          </div>


          <div className="decision-status status-attention">

            <div className="decision-status-top">
              <span>03</span>
              <CircleAlert size={18} />
            </div>

            <strong>Operational risk</strong>

            <p>
              Review port and weather signals
            </p>

            <span className="status-review">
              Review
            </span>

          </div>

        </div>

      </section>

    </div>
  );
}