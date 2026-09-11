import {
  Anchor,
  ArrowRight,
  CircleAlert,
  Clock3,
  CloudRain,
  MapPin,
  Ship,
  TrendingUp,
} from "lucide-react";
import { useNavigate } from "react-router-dom";
import { getShipment } from "../services/shipmentStorage";

export default function PortIntelligence() {
  const navigate = useNavigate();
  const shipment = getShipment();

  if (!shipment) {
    return (
      <div className="port-page">
        <section className="port-header">
          <div>
            <p className="section-label">PORT INTELLIGENCE</p>

            <h1>No shipment selected.</h1>

            <p>
              Start by entering your shipment details so port conditions can
              be evaluated for your voyage.
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
  } = shipment;

  return (
    <div className="port-page">

      {/* HEADER */}

      <section className="port-header">
        <div>
          <p className="section-label">PORT INTELLIGENCE</p>

          <h1>Know what is happening at the ports.</h1>

          <p>
            Review port activity, congestion, turnaround conditions and
            operational signals that can affect your voyage.
          </p>
        </div>

        <div className="port-header-status">
          <Anchor size={17} />
          <span>Port operations workspace</span>
        </div>
      </section>


      {/* ROUTE */}

      <section className="port-route-card">

        <div className="port-route-heading">
          <div>
            <p className="section-label">VOYAGE PORTS</p>

            <h2>
              {origin} → {destination}
            </h2>

            <p>
              Origin and destination operational overview
            </p>
          </div>

          <div className="route-status">
            <span className="route-status-dot" />
            Monitoring
          </div>
        </div>


        <div className="port-route">

          <div className="port-location">

            <div className="port-location-icon">
              <MapPin size={20} />
            </div>

            <div>
              <span>ORIGIN</span>
              <strong>{origin}</strong>
              <small>Loading port</small>
            </div>

          </div>


          <div className="port-route-line">
            <div />
            <Ship size={20} />
            <div />
          </div>


          <div className="port-location destination">

            <div className="port-location-icon">
              <MapPin size={20} />
            </div>

            <div>
              <span>DESTINATION</span>
              <strong>{destination}</strong>
              <small>Discharge port</small>
            </div>

          </div>

        </div>


        <div className="port-shipment-context">

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

        </div>

      </section>


      {/* PORT STATUS */}

      <section className="port-section">

        <div className="port-section-heading">

          <div>
            <p className="section-label">
              OPERATIONAL STATUS
            </p>

            <h2>How the ports are performing</h2>

            <p>
              Current operational indicators that may influence voyage
              timing and cost.
            </p>
          </div>

        </div>


        <div className="port-status-grid">

          {/* ORIGIN */}

          <div className="port-status-card">

            <div className="port-status-top">

              <div className="port-card-icon">
                <Anchor size={19} />
              </div>

              <span className="status-good">
                Normal
              </span>

            </div>

            <span>{origin.toUpperCase()}</span>

            <h3>Operationally stable</h3>

            <p>
              Current activity does not indicate significant loading
              disruption.
            </p>

            <div className="port-mini-metrics">

              <div>
                <span>WAIT TIME</span>
                <strong>1.8 hrs</strong>
              </div>

              <div>
                <span>ACTIVITY</span>
                <strong>Moderate</strong>
              </div>

            </div>

          </div>


          {/* DESTINATION */}

          <div className="port-status-card">

            <div className="port-status-top">

              <div className="port-card-icon">
                <Anchor size={19} />
              </div>

              <span className="status-warning">
                Watch
              </span>

            </div>

            <span>{destination.toUpperCase()}</span>

            <h3>Moderate congestion</h3>

            <p>
              Increased vessel activity may result in longer turnaround
              times.
            </p>

            <div className="port-mini-metrics">

              <div>
                <span>WAIT TIME</span>
                <strong>5.2 hrs</strong>
              </div>

              <div>
                <span>ACTIVITY</span>
                <strong>High</strong>
              </div>

            </div>

          </div>

        </div>

      </section>


      {/* OPERATIONAL INDICATORS */}

      <section className="port-section">

        <div className="port-section-heading">

          <div>
            <p className="section-label">
              PORT INDICATORS
            </p>

            <h2>Signals worth watching</h2>

            <p>
              Operational conditions can change the effective economics
              of a voyage even when freight rates remain unchanged.
            </p>
          </div>

        </div>


        <div className="port-indicator-grid">

          <div className="port-indicator">

            <div className="port-indicator-icon">
              <Clock3 size={19} />
            </div>

            <div>
              <span>AVERAGE WAIT</span>
              <strong>3.5 hrs</strong>
              <p>Across selected ports</p>
            </div>

          </div>


          <div className="port-indicator">

            <div className="port-indicator-icon">
              <Ship size={19} />
            </div>

            <div>
              <span>VESSEL ACTIVITY</span>
              <strong>High</strong>
              <p>Increased arrivals observed</p>
            </div>

          </div>


          <div className="port-indicator">

            <div className="port-indicator-icon">
              <CloudRain size={19} />
            </div>

            <div>
              <span>WEATHER IMPACT</span>
              <strong>Low</strong>
              <p>No major disruption expected</p>
            </div>

          </div>


          <div className="port-indicator">

            <div className="port-indicator-icon">
              <TrendingUp size={19} />
            </div>

            <div>
              <span>THROUGHPUT</span>
              <strong>Increasing</strong>
              <p>Recent port activity</p>
            </div>

          </div>

        </div>

      </section>


      {/* PORT IMPACT */}

      <section className="port-impact">

        <div className="port-impact-icon">
          <CircleAlert size={21} />
        </div>

        <div className="port-impact-copy">

          <p className="section-label">
            VOYAGE IMPACT
          </p>

          <h2>
            {destination} deserves closer attention.
          </h2>

          <p>
            Current destination conditions could increase turnaround time.
            The final voyage economics should account for potential waiting
            costs before fixing the vessel.
          </p>

        </div>

        <button
          className="text-action"
          onClick={() => navigate("/risk")}
          type="button"
        >
          Continue to risk center
          <ArrowRight size={16} />
        </button>

      </section>

    </div>
  );
}