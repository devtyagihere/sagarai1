import {
  ArrowDownRight,
  ArrowRight,
  ArrowUpRight,
  BarChart3,
  CalendarDays,
  CircleAlert,
  Info,
  TrendingUp,
} from "lucide-react";
import { useNavigate } from "react-router-dom";
import { getShipment } from "../services/shipmentStorage";

export default function FreightForecast() {
  const navigate = useNavigate();
  const shipment = getShipment();

  if (!shipment) {
    return (
      <div className="forecast-page">
        <section className="forecast-header">
          <div>
            <p className="section-label">FREIGHT FORECAST</p>

            <h1>No shipment selected.</h1>

            <p>
              Start by entering your shipment details so the freight forecast
              can be prepared for your route.
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
    <div className="forecast-page">

      {/* HEADER */}

      <section className="forecast-header">
        <div>
          <p className="section-label">FREIGHT FORECAST</p>

          <h1>Understand where freight is heading.</h1>

          <p>
            Review the current market, forecast direction, and the signals
            that may influence your next freight decision.
          </p>
        </div>

        <div className="forecast-date">
          <CalendarDays size={16} />
          <span>Forecast workspace</span>
        </div>
      </section>


      {/* SHIPMENT CONTEXT */}

      <section className="forecast-shipment-context">

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


      {/* CURRENT MARKET */}

      <section className="forecast-market-card">

        <div className="forecast-market-heading">
          <div>
            <p className="section-label">CURRENT MARKET</p>

            <h2>Freight rate outlook</h2>
          </div>

          <div className="market-direction">
            <TrendingUp size={17} />
            <span>Market rising</span>
          </div>
        </div>


        <div className="forecast-main-grid">

          <div className="forecast-primary-rate">
            <span className="card-label">
              CURRENT FREIGHT RATE
            </span>

            <div className="forecast-rate">
              $24.50
            </div>

            <span className="forecast-rate-unit">
              USD / MT
            </span>

            <div className="forecast-change positive">
              <ArrowUpRight size={16} />
              <span>3.8% this week</span>
            </div>
          </div>


          <div className="forecast-stat">
            <span className="card-label">
              NEXT WEEK
            </span>

            <strong>$25.10</strong>

            <p>
              Expected market level
            </p>
          </div>


          <div className="forecast-stat">
            <span className="card-label">
              30 DAY OUTLOOK
            </span>

            <strong>Moderate</strong>

            <p>
              Upward pressure expected
            </p>
          </div>

        </div>

      </section>


      {/* CHART */}

      <section className="forecast-section">

        <div className="forecast-section-heading">

          <div>
            <p className="section-label">
              RATE TREND
            </p>

            <h2>Freight market movement</h2>

            <p>
              Historical movement and forecast direction for the selected
              freight route.
            </p>
          </div>

          <button
            className="forecast-filter"
            type="button"
          >
            <CalendarDays size={15} />
            Last 30 days
          </button>

        </div>


        <div className="forecast-chart-card">

          <div className="chart-y-axis">
            <span>$30</span>
            <span>$27</span>
            <span>$24</span>
            <span>$21</span>
            <span>$18</span>
          </div>

          <div className="chart-area">

            <div className="chart-grid-line" />
            <div className="chart-grid-line" />
            <div className="chart-grid-line" />
            <div className="chart-grid-line" />
            <div className="chart-grid-line" />

            <div className="chart-placeholder-line">
              <span />
              <span />
              <span />
              <span />
              <span />
              <span />
              <span />
            </div>

            <div className="chart-overlay-message">
              <BarChart3 size={22} />

              <strong>
                Forecast chart
              </strong>

              <p>
                Live rate history will appear here once market data is
                connected.
              </p>
            </div>

          </div>

        </div>

      </section>


      {/* MARKET SIGNALS */}

      <section className="forecast-section">

        <div className="forecast-section-heading">
          <div>
            <p className="section-label">
              FORECAST SIGNALS
            </p>

            <h2>Why the market may move</h2>

            <p>
              Key factors considered when forming the freight outlook.
            </p>
          </div>
        </div>


        <div className="forecast-signals-grid">

          <div className="forecast-signal-card">

            <div className="forecast-signal-top">
              <div className="forecast-signal-icon">
                <TrendingUp size={19} />
              </div>

              <span className="signal-positive">
                Positive
              </span>
            </div>

            <span>DRY BULK DEMAND</span>

            <strong>Increasing</strong>

            <p>
              Stronger cargo demand can place upward pressure on freight
              rates.
            </p>

          </div>


          <div className="forecast-signal-card">

            <div className="forecast-signal-top">
              <div className="forecast-signal-icon">
                <BarChart3 size={19} />
              </div>

              <span className="signal-neutral">
                Neutral
              </span>
            </div>

            <span>VESSEL SUPPLY</span>

            <strong>Balanced</strong>

            <p>
              Available vessel capacity is currently keeping market
              pressure moderate.
            </p>

          </div>


          <div className="forecast-signal-card">

            <div className="forecast-signal-top">
              <div className="forecast-signal-icon">
                <CircleAlert size={19} />
              </div>

              <span className="signal-warning">
                Watch
              </span>
            </div>

            <span>FUEL COST</span>

            <strong>Elevated</strong>

            <p>
              Higher bunker costs may increase the effective cost of the
              voyage.
            </p>

          </div>


          <div className="forecast-signal-card">

            <div className="forecast-signal-top">
              <div className="forecast-signal-icon">
                <ArrowDownRight size={19} />
              </div>

              <span className="signal-neutral">
                Neutral
              </span>
            </div>

            <span>PORT CONDITIONS</span>

            <strong>Moderate</strong>

            <p>
              Current port activity does not indicate significant
              disruption.
            </p>

          </div>

        </div>

      </section>


      {/* FORECAST INTERPRETATION */}

      <section className="forecast-interpretation">

        <div className="interpretation-icon">
          <Info size={20} />
        </div>

        <div>
          <p className="section-label">
            MARKET INTERPRETATION
          </p>

          <h2>
            The market is showing moderate upward pressure.
          </h2>

          <p>
            A rising freight environment can make waiting more expensive.
            The final fixing recommendation should therefore consider the
            forecast together with vessel economics, port conditions, and
            operational risk.
          </p>
        </div>

        <button
          className="text-action"
          onClick={() => navigate("/vessels")}
          type="button"
        >
          Continue to vessel economics
          <ArrowRight size={16} />
        </button>

      </section>

    </div>
  );
}