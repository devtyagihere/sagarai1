import { useState } from "react";
import {
  ArrowDownRight,
  ArrowRight,
  ArrowUpRight,
  BarChart3,
  CalendarDays,
  CircleAlert,
  Info,
  TrendingUp,
  TrendingDown,
  SlidersHorizontal,
  Sparkles,
  RefreshCw,
} from "lucide-react";
import { useNavigate } from "react-router-dom";
import { getShipment, getAnalysisResult } from "../services/shipmentStorage";
import FreightRateChart from "../components/forecast/FreightRateChart";

export default function FreightForecast() {
  const navigate = useNavigate();
  const shipment = getShipment();
  const analysis = getAnalysisResult();

  const [activeTab, setActiveTab] = useState("all");
  const [bdiDelta, setBdiDelta] = useState(0);
  const [oilDelta, setOilDelta] = useState(0);

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

  const forecast = analysis?.market_intelligence?.freight_forecast;
  const evaluation = analysis?.market_intelligence?.model_evaluation;
  const marketSnapshot = analysis?.market_intelligence?.market_snapshot;
  const portOps = analysis?.port_operations;
  const destOps = portOps?.destination;
  const originOps = portOps?.origin;
  const economics = analysis?.vessel_economics;

  const baseRate = forecast?.current_rate_usd_mt ?? 24.50;
  // Dynamic market sensitivity calculation
  const simulatedRate = (baseRate * (1 + (bdiDelta * 0.0035) + (oilDelta * 0.002))).toFixed(2);
  const simulatedDeltaPct = (((simulatedRate - baseRate) / baseRate) * 100).toFixed(1);

  return (
    <div className="forecast-page">

      {/* HEADER */}

      <section className="forecast-header">
        <div>
          <p className="section-label">FREIGHT FORECAST &amp; SENSITIVITY ENGINE</p>

          <h1>Understand where freight is heading.</h1>

          <p>
            Review machine learning forecast curves, test live market sensitivities, and evaluate price trajectory.
          </p>
        </div>

        <div className="forecast-date">
          <CalendarDays size={16} />
          <span>ML Forecast workspace</span>
        </div>
      </section>

      {/* INTERACTIVE TIMEFRAME SELECTOR */}
      <div className="interactive-tabs-bar">
        <button
          type="button"
          className={`interactive-tab-btn ${activeTab === "all" ? "active" : ""}`}
          onClick={() => setActiveTab("all")}
        >
          <BarChart3 size={15} /> All Horizons (7d / 15d / 30d)
        </button>
        <button
          type="button"
          className={`interactive-tab-btn ${activeTab === "7d" ? "active" : ""}`}
          onClick={() => setActiveTab("7d")}
        >
          7-Day Short Term
        </button>
        <button
          type="button"
          className={`interactive-tab-btn ${activeTab === "30d" ? "active" : ""}`}
          onClick={() => setActiveTab("30d")}
        >
          30-Day Outlook
        </button>
        <button
          type="button"
          className={`interactive-tab-btn ${activeTab === "simulator" ? "active" : ""}`}
          onClick={() => setActiveTab("simulator")}
        >
          <SlidersHorizontal size={15} /> Live Rate Sensitivity
        </button>
      </div>

      {activeTab === "simulator" && (
        <section className="interactive-slider-box" style={{ marginBottom: '20px', background: '#f8fafc', border: '1.5px solid #38bdf8' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '14px' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <Sparkles size={18} color="#0284c7" />
              <strong style={{ fontSize: '0.95rem', color: '#0f172a' }}>Live Market Sensitivity Simulator</strong>
            </div>
            <button
              type="button"
              className="interactive-action-btn"
              onClick={() => { setBdiDelta(0); setOilDelta(0); }}
              style={{ padding: '4px 10px', fontSize: '0.75rem' }}
            >
              <RefreshCw size={13} /> Reset Sliders
            </button>
          </div>

          <p style={{ fontSize: '0.82rem', color: '#64748b', marginBottom: '16px' }}>
            Adjust market conditions below to simulate real-time freight rate variance against the ML baseline:
          </p>

          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))', gap: '16px' }}>
            <div>
              <div className="interactive-slider-header">
                <span className="interactive-slider-label">BDI Shift (%)</span>
                <span className="interactive-slider-val">{bdiDelta >= 0 ? `+${bdiDelta}%` : `${bdiDelta}%`}</span>
              </div>
              <input
                type="range"
                min="-25"
                max="25"
                value={bdiDelta}
                onChange={(e) => setBdiDelta(Number(e.target.value))}
                className="interactive-range-input"
              />
            </div>

            <div>
              <div className="interactive-slider-header">
                <span className="interactive-slider-label">Crude Oil Shift ($/bbl)</span>
                <span className="interactive-slider-val">{oilDelta >= 0 ? `+$${oilDelta}` : `-$${Math.abs(oilDelta)}`}</span>
              </div>
              <input
                type="range"
                min="-20"
                max="20"
                value={oilDelta}
                onChange={(e) => setOilDelta(Number(e.target.value))}
                className="interactive-range-input"
              />
            </div>

            <div style={{ background: '#ffffff', padding: '10px 16px', borderRadius: '10px', border: '1px solid #cbd5e1', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
              <div>
                <span style={{ fontSize: '0.72rem', color: '#64748b', fontWeight: 700, display: 'block' }}>SIMULATED FREIGHT</span>
                <strong style={{ fontSize: '1.25rem', color: '#0f766e' }}>${simulatedRate}</strong>
                <span style={{ fontSize: '0.75rem', color: '#64748b' }}> / MT</span>
              </div>
              <div className={`interactive-pill-tag ${Number(simulatedDeltaPct) >= 0 ? "amber" : "green"}`}>
                {Number(simulatedDeltaPct) >= 0 ? `+${simulatedDeltaPct}%` : `${simulatedDeltaPct}%`} vs base
              </div>
            </div>
          </div>
        </section>
      )}

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
            {(forecast?.forecast_direction === "down" || forecast?.direction === "down") ? (
              <TrendingDown size={17} color="#dc2626" />
            ) : (
              <TrendingUp size={17} color="#16a34a" />
            )}
            <span>
              {forecast?.forecast_direction
                ? `Market ${forecast.forecast_direction.toLowerCase()}`
                : forecast?.direction
                ? `Market ${forecast.direction.toLowerCase()}`
                : "Market rising"}
            </span>
          </div>
        </div>


        <div className="forecast-main-grid">

          <div className="forecast-primary-rate">
            <span className="card-label">
              CURRENT FREIGHT RATE
            </span>

            <div className="forecast-rate">
              {forecast?.current_rate_usd_mt != null ? `$${Number(forecast.current_rate_usd_mt).toFixed(2)}` : "$24.50"}
            </div>

            <span className="forecast-rate-unit">
              USD / MT
            </span>

            <div className="forecast-change positive">
              {forecast?.forecast_change_percent != null && forecast.forecast_change_percent < 0 ? (
                <ArrowDownRight size={16} />
              ) : (
                <ArrowUpRight size={16} />
              )}
              <span>
                {forecast?.forecast_change_percent != null
                  ? `${forecast.forecast_change_percent >= 0 ? "+" : ""}${Number(forecast.forecast_change_percent).toFixed(1)}% 30d`
                  : forecast?.change_7d_pct != null
                  ? `${forecast.change_7d_pct >= 0 ? "+" : ""}${Number(forecast.change_7d_pct).toFixed(1)}% 7d`
                  : "3.8% this week"}
              </span>
            </div>
          </div>


          <div className="forecast-stat">
            <span className="card-label">
              NEXT WEEK (7D)
            </span>

            <strong>
              {forecast?.forecast_7d_usd_mt != null ? `$${Number(forecast.forecast_7d_usd_mt).toFixed(2)}` : "$25.10"}
            </strong>

            <p>
              Expected market level
            </p>
          </div>


          <div className="forecast-stat">
            <span className="card-label">
              30 DAY OUTLOOK
            </span>

            <strong>
              {forecast?.forecast_30d_usd_mt != null ? `$${Number(forecast.forecast_30d_usd_mt).toFixed(2)}` : "Moderate"}
            </strong>

            <p>
              {forecast?.forecast_change_percent != null
                ? `${forecast.forecast_change_percent >= 0 ? "+" : ""}${Number(forecast.forecast_change_percent).toFixed(1)}% projected`
                : "Upward pressure expected"}
            </p>
          </div>

        </div>

      </section>


      {/* CHART */}

      <section className="forecast-section">

        <div className="forecast-section-heading">

          <div>
            <p className="section-label">
              RATE TREND & DYNAMIC FORECAST
            </p>

            <h2>Freight rate trajectory ($/MT)</h2>

            <p>
              ML-forecasted rate progression plotted across 7d, 15d and 30d horizons with Baltic historical fixtures.
            </p>
          </div>

        </div>


        <div className="forecast-chart-card" style={{ display: 'block', padding: '20px 24px', minHeight: 'auto' }}>
          <FreightRateChart
            forecast={forecast}
            evaluation={evaluation}
            origin={origin}
            destination={destination}
            cargo={cargo}
            deliveryDate={deliveryDate}
          />
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

              <span className={marketSnapshot?.bdi?.direction === "down" ? "signal-warning" : "signal-positive"}>
                {marketSnapshot?.bdi?.direction === "down" ? "Softening" : "Supportive"}
              </span>
            </div>

            <span>DRY BULK DEMAND (BDI)</span>

            <strong>
              {marketSnapshot?.bdi?.current_value != null
                ? `BDI ${Math.round(marketSnapshot.bdi.current_value).toLocaleString()} (${marketSnapshot.bdi.change_percent >= 0 ? "+" : ""}${marketSnapshot.bdi.change_percent.toFixed(1)}%)`
                : "BDI 1,500 (+9.8%)"}
            </strong>

            <p>
              {marketSnapshot?.bdi?.direction === "up"
                ? "Expanding dry bulk activity creates steady upward rate pressure."
                : "Baltic Dry Index indicates balanced market chartering volume."}
            </p>

          </div>


          <div className="forecast-signal-card">

            <div className="forecast-signal-top">
              <div className="forecast-signal-icon">
                <BarChart3 size={19} />
              </div>

              <span className="signal-neutral">
                {economics?.cheapest_feasible_vessel ? "Feasible" : "Balanced"}
              </span>
            </div>

            <span>VESSEL SUPPLY</span>

            <strong>
              {economics?.cheapest_feasible_vessel
                ? `${economics.cheapest_feasible_vessel} suitable`
                : "Tonnage balanced"}
            </strong>

            <p>
              {economics?.comparison
                ? `${economics.comparison.filter((c) => c.feasibility_status === "FEASIBLE").length} vessel classes meet cargo and draft requirements.`
                : "Available fleet capacity is currently keeping market spread moderate."}
            </p>

          </div>


          <div className="forecast-signal-card">

            <div className="forecast-signal-top">
              <div className="forecast-signal-icon">
                <CircleAlert size={19} />
              </div>

              <span className={marketSnapshot?.oil_price?.current_value > 85 ? "signal-warning" : "signal-neutral"}>
                {marketSnapshot?.oil_price?.direction || "Stable"}
              </span>
            </div>

            <span>BUNKER / FUEL (WTI)</span>

            <strong>
              {marketSnapshot?.oil_price?.current_value != null
                ? `$${marketSnapshot.oil_price.current_value.toFixed(2)} / bbl`
                : "$80.04 / bbl"}
            </strong>

            <p>
              Fuel costs represent an essential variable in overall voyage economics and bunker adjustment factors.
            </p>

          </div>


          <div className="forecast-signal-card">

            <div className="forecast-signal-top">
              <div className="forecast-signal-icon">
                <ArrowDownRight size={19} />
              </div>

              <span className={destOps?.congestion_level === "HIGH" ? "signal-warning" : "signal-positive"}>
                {destOps?.congestion_level || "Normal"}
              </span>
            </div>

            <span>PORT CONDITIONS ({destination})</span>

            <strong>
              {destOps?.congestion_level ? `${destOps.congestion_level} Congestion` : "Stable Operations"}
            </strong>

            <p>
              {destOps?.vessels_waiting != null
                ? `${destOps.vessels_waiting} vessels waiting at destination with ~${destOps.average_waiting_days?.toFixed(1) || "1"}d turnaround.`
                : "Current port activity does not indicate significant operational disruption."}
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