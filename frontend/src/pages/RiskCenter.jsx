import {
  AlertTriangle,
  Anchor,
  ArrowRight,
  CloudRain,
  Fuel,
  MapPin,
  ShieldCheck,
  Ship,
  TrendingUp,
  Wind,
} from "lucide-react";
import { useNavigate } from "react-router-dom";
import { getShipment } from "../services/shipmentStorage";

export default function RiskCenter() {
  const navigate = useNavigate();
  const shipment = getShipment();

  if (!shipment) {
    return (
      <div className="risk-page">
        <section className="risk-header">
          <div>
            <p className="section-label">RISK CENTER</p>

            <h1>No shipment selected.</h1>

            <p>
              Start by entering your shipment details so voyage risks can be
              evaluated for your planned route.
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
    priority,
  } = shipment;

  return (
    <div className="risk-page">

      {/* HEADER */}

      <section className="risk-header">
        <div>
          <p className="section-label">RISK CENTER</p>

          <h1>See what could disrupt the voyage.</h1>

          <p>
            Review the operational, weather, market and vessel risks
            that may affect cost, timing and the final charter decision.
          </p>
        </div>

        <div className="risk-header-status">
          <ShieldCheck size={17} />
          <span>Risk assessment workspace</span>
        </div>
      </section>


      {/* SHIPMENT CONTEXT */}

      <section className="risk-shipment-context">

        <div>
          <span>ROUTE</span>
          <strong>
            {origin} → {destination}
          </strong>
        </div>

        <div>
          <span>CARGO</span>
          <strong>{cargo}</strong>
        </div>

        <div>
          <span>QUANTITY</span>
          <strong>
            {Number(quantity).toLocaleString()} MT
          </strong>
        </div>

        <div>
          <span>DELIVERY</span>
          <strong>{deliveryDate}</strong>
        </div>

        <div>
          <span>PRIORITY</span>
          <strong>{priority}</strong>
        </div>

      </section>


      {/* OVERALL RISK */}

      <section className="risk-overview-card">

        <div className="risk-overview-main">

          <div className="risk-score-circle">
            <strong>42</strong>
            <span>/ 100</span>
          </div>

          <div className="risk-overview-copy">
            <p className="section-label">
              OVERALL VOYAGE RISK
            </p>

            <h2>Moderate risk</h2>

            <p>
              Current conditions do not indicate a major disruption,
              but several factors should be monitored before fixing.
            </p>
          </div>

        </div>


        <div className="risk-overview-status">

          <div>
            <span>RISK LEVEL</span>
            <strong>Moderate</strong>
          </div>

          <div>
            <span>FACTORS REVIEWED</span>
            <strong>4</strong>
          </div>

          <div>
            <span>ATTENTION ITEMS</span>
            <strong>2</strong>
          </div>

        </div>

      </section>


      {/* RISK FACTORS */}

      <section className="risk-section">

        <div className="risk-section-heading">

          <div>
            <p className="section-label">
              RISK FACTORS
            </p>

            <h2>What needs attention</h2>

            <p>
              Each factor contributes differently to the overall voyage
              risk assessment.
            </p>
          </div>

        </div>


        <div className="risk-factor-grid">

          {/* WEATHER */}

          <div className="risk-factor-card">

            <div className="risk-factor-top">

              <div className="risk-factor-icon">
                <CloudRain size={20} />
              </div>

              <span className="risk-low">
                Low
              </span>

            </div>

            <span>WEATHER</span>

            <h3>Limited weather exposure</h3>

            <p>
              No major weather disruption is currently indicated along
              the planned voyage.
            </p>

            <div className="risk-factor-footer">
              <Wind size={15} />
              <span>Weather conditions stable</span>
            </div>

          </div>


          {/* PORT */}

          <div className="risk-factor-card risk-attention">

            <div className="risk-factor-top">

              <div className="risk-factor-icon">
                <Anchor size={20} />
              </div>

              <span className="risk-medium">
                Moderate
              </span>

            </div>

            <span>PORT OPERATIONS</span>

            <h3>Destination congestion</h3>

            <p>
              Increased activity at the destination may result in
              additional waiting time.
            </p>

            <div className="risk-factor-footer">
              <MapPin size={15} />
              <span>{destination} requires monitoring</span>
            </div>

          </div>


          {/* MARKET */}

          <div className="risk-factor-card">

            <div className="risk-factor-top">

              <div className="risk-factor-icon">
                <TrendingUp size={20} />
              </div>

              <span className="risk-medium">
                Moderate
              </span>

            </div>

            <span>FREIGHT MARKET</span>

            <h3>Rates trending upward</h3>

            <p>
              Waiting for a later fixing opportunity may increase the
              effective freight cost.
            </p>

            <div className="risk-factor-footer">
              <TrendingUp size={15} />
              <span>Upward market pressure</span>
            </div>

          </div>


          {/* VESSEL */}

          <div className="risk-factor-card">

            <div className="risk-factor-top">

              <div className="risk-factor-icon">
                <Ship size={20} />
              </div>

              <span className="risk-low">
                Low
              </span>

            </div>

            <span>VESSEL EXPOSURE</span>

            <h3>Suitable vessel supply</h3>

            <p>
              Current vessel availability provides reasonable flexibility
              for the planned cargo.
            </p>

            <div className="risk-factor-footer">
              <Ship size={15} />
              <span>Supply conditions balanced</span>
            </div>

          </div>

        </div>

      </section>


      {/* RISK BREAKDOWN */}

      <section className="risk-section">

        <div className="risk-section-heading">

          <div>
            <p className="section-label">
              RISK BREAKDOWN
            </p>

            <h2>Where exposure is coming from</h2>

            <p>
              A simple view of the factors contributing to the current
              risk level.
            </p>
          </div>

        </div>


        <div className="risk-breakdown-card">

          <div className="risk-breakdown-item">

            <div className="risk-breakdown-label">
              <span>Port congestion</span>
              <strong>32%</strong>
            </div>

            <div className="risk-progress">
              <div
                className="risk-progress-fill"
                style={{ width: "32%" }}
              />
            </div>

          </div>


          <div className="risk-breakdown-item">

            <div className="risk-breakdown-label">
              <span>Freight market</span>
              <strong>28%</strong>
            </div>

            <div className="risk-progress">
              <div
                className="risk-progress-fill"
                style={{ width: "28%" }}
              />
            </div>

          </div>


          <div className="risk-breakdown-item">

            <div className="risk-breakdown-label">
              <span>Weather</span>
              <strong>18%</strong>
            </div>

            <div className="risk-progress">
              <div
                className="risk-progress-fill"
                style={{ width: "18%" }}
              />
            </div>

          </div>


          <div className="risk-breakdown-item">

            <div className="risk-breakdown-label">
              <span>Vessel exposure</span>
              <strong>12%</strong>
            </div>

            <div className="risk-progress">
              <div
                className="risk-progress-fill"
                style={{ width: "12%" }}
              />
            </div>

          </div>

        </div>

      </section>


      {/* WATCH ITEMS */}

      <section className="risk-watch-card">

        <div className="risk-watch-icon">
          <AlertTriangle size={21} />
        </div>

        <div className="risk-watch-copy">

          <p className="section-label">
            WATCH ITEMS
          </p>

          <h2>
            Two things deserve attention before fixing.
          </h2>

          <div className="risk-watch-list">

            <div>
              <span>01</span>
              <p>
                Destination port congestion could increase waiting costs.
              </p>
            </div>

            <div>
              <span>02</span>
              <p>
                Rising freight rates could make delaying the charter more
                expensive.
              </p>
            </div>

          </div>

        </div>

        <button
          className="text-action"
          onClick={() => navigate("/decision")}
          type="button"
        >
          Continue to decision engine
          <ArrowRight size={16} />
        </button>

      </section>


      {/* SAFETY NOTE */}

      <section className="risk-note">

        <div className="risk-note-icon">
          <Fuel size={19} />
        </div>

        <div>

          <p className="section-label">
            DECISION CONTEXT
          </p>

          <p>
            Risk should be considered alongside freight rates, vessel
            economics and shipment priorities rather than viewed in
            isolation.
          </p>

        </div>

      </section>

    </div>
  );
}