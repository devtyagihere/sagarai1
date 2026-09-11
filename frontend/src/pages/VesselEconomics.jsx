import {
  ArrowRight,
  CircleAlert,
  Fuel,
  Ship,
  TrendingDown,
  TrendingUp,
} from "lucide-react";
import { useNavigate } from "react-router-dom";
import { getShipment } from "../services/shipmentStorage";

export default function VesselEconomics() {
  const navigate = useNavigate();
  const shipment = getShipment();

  if (!shipment) {
    return (
      <div className="vessel-page">
        <section className="vessel-header">
          <div>
            <p className="section-label">VESSEL ECONOMICS</p>

            <h1>No shipment selected.</h1>

            <p>
              Start by entering your shipment details so vessel economics can
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
    priority,
  } = shipment;

  return (
    <div className="vessel-page">

      {/* HEADER */}

      <section className="vessel-header">
        <div>
          <p className="section-label">VESSEL ECONOMICS</p>

          <h1>Find the vessel that makes the voyage work.</h1>

          <p>
            Compare vessel capacity, operating cost, fuel exposure and
            voyage economics before making a chartering decision.
          </p>
        </div>

        <div className="vessel-header-status">
          <Ship size={17} />
          <span>Vessel comparison workspace</span>
        </div>
      </section>


      {/* SHIPMENT CONTEXT */}

      <section className="vessel-context">

        <div>
          <p className="section-label">SHIPMENT CONTEXT</p>

          <h2>
            {origin} → {destination}
          </h2>

          <p>
            {cargo} · {Number(quantity).toLocaleString()} MT
          </p>
        </div>

        <div className="context-items">

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

        </div>

      </section>


      {/* ECONOMIC SUMMARY */}

      <section className="vessel-section">

        <div className="vessel-section-heading">
          <div>
            <p className="section-label">ECONOMIC SUMMARY</p>

            <h2>What matters most for this voyage</h2>
          </div>
        </div>


        <div className="vessel-summary-grid">

          <div className="vessel-summary-card">

            <div className="vessel-card-icon">
              <Ship size={20} />
            </div>

            <span>BEST FIT</span>

            <strong>Panamax</strong>

            <p>
              Capacity aligns closely with the planned cargo.
            </p>

          </div>


          <div className="vessel-summary-card">

            <div className="vessel-card-icon">
              <Fuel size={20} />
            </div>

            <span>FUEL EXPOSURE</span>

            <strong>Moderate</strong>

            <p>
              Bunker consumption remains manageable for the route.
            </p>

          </div>


          <div className="vessel-summary-card">

            <div className="vessel-card-icon">
              <TrendingDown size={20} />
            </div>

            <span>UNIT COST</span>

            <strong>$18.40 / MT</strong>

            <p>
              Indicative voyage operating cost.
            </p>

          </div>


          <div className="vessel-summary-card">

            <div className="vessel-card-icon">
              <TrendingUp size={20} />
            </div>

            <span>ECONOMIC SIGNAL</span>

            <strong>Favourable</strong>

            <p>
              Current vessel economics support the voyage plan.
            </p>

          </div>

        </div>

      </section>


      {/* VESSEL COMPARISON */}

      <section className="vessel-section">

        <div className="vessel-section-heading">

          <div>
            <p className="section-label">
              VESSEL COMPARISON
            </p>

            <h2>Compare available vessel classes</h2>

            <p>
              The final model will rank vessels using cargo fit, cost,
              fuel efficiency and operational constraints.
            </p>
          </div>

        </div>


        <div className="vessel-table-card">

          <div className="vessel-table-row vessel-table-header">
            <span>VESSEL</span>
            <span>CAPACITY</span>
            <span>FUEL / DAY</span>
            <span>EST. COST</span>
            <span>FIT</span>
          </div>


          <div className="vessel-table-row">

            <div className="vessel-name">
              <div className="mini-ship">
                <Ship size={17} />
              </div>

              <strong>Panamax</strong>
            </div>

            <span>70–82K MT</span>

            <span>24 MT</span>

            <strong>$18.40 / MT</strong>

            <span className="fit-good">
              Strong fit
            </span>

          </div>


          <div className="vessel-table-row">

            <div className="vessel-name">
              <div className="mini-ship">
                <Ship size={17} />
              </div>

              <strong>Supramax</strong>
            </div>

            <span>50–65K MT</span>

            <span>21 MT</span>

            <strong>$20.10 / MT</strong>

            <span className="fit-warning">
              Partial fit
            </span>

          </div>


          <div className="vessel-table-row">

            <div className="vessel-name">
              <div className="mini-ship">
                <Ship size={17} />
              </div>

              <strong>Post-Panamax</strong>
            </div>

            <span>85–95K MT</span>

            <span>28 MT</span>

            <strong>$19.20 / MT</strong>

            <span className="fit-good">
              Good fit
            </span>

          </div>

        </div>

      </section>


      {/* COST BREAKDOWN */}

      <section className="vessel-section">

        <div className="vessel-section-heading">

          <div>
            <p className="section-label">
              VOYAGE COST
            </p>

            <h2>Where the money goes</h2>

            <p>
              A transparent breakdown makes the economic recommendation
              easier to understand.
            </p>
          </div>

        </div>


        <div className="cost-breakdown">

          <div className="cost-item">

            <div className="cost-item-heading">
              <span>Fuel</span>
              <strong>42%</strong>
            </div>

            <div className="cost-bar">
              <div
                className="cost-bar-fill"
                style={{ width: "42%" }}
              />
            </div>

          </div>


          <div className="cost-item">

            <div className="cost-item-heading">
              <span>Charter hire</span>
              <strong>31%</strong>
            </div>

            <div className="cost-bar">
              <div
                className="cost-bar-fill"
                style={{ width: "31%" }}
              />
            </div>

          </div>


          <div className="cost-item">

            <div className="cost-item-heading">
              <span>Port & handling</span>
              <strong>17%</strong>
            </div>

            <div className="cost-bar">
              <div
                className="cost-bar-fill"
                style={{ width: "17%" }}
              />
            </div>

          </div>


          <div className="cost-item">

            <div className="cost-item-heading">
              <span>Other voyage costs</span>
              <strong>10%</strong>
            </div>

            <div className="cost-bar">
              <div
                className="cost-bar-fill"
                style={{ width: "10%" }}
              />
            </div>

          </div>

        </div>

      </section>


      {/* ECONOMIC NOTE */}

      <section className="vessel-note">

        <div className="vessel-note-icon">
          <CircleAlert size={20} />
        </div>

        <div>

          <p className="section-label">
            ECONOMIC NOTE
          </p>

          <h2>
            The cheapest vessel is not always the best vessel.
          </h2>

          <p>
            Capacity utilisation, fuel consumption, port compatibility,
            voyage duration and freight conditions all influence the true
            economics of a charter.
          </p>

        </div>

        <button
          className="text-action"
          onClick={() => navigate("/ports")}
          type="button"
        >
          Continue to port intelligence
          <ArrowRight size={16} />
        </button>

      </section>

    </div>
  );
}