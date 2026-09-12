import { useState } from "react";
import {
  ArrowRight,
  ArrowUpRight,
  CalendarDays,
  CircleAlert,
  Fuel,
  MapPin,
  Ship,
  TrendingUp,
  Copy,
  Check,
  ExternalLink,
  Sparkles,
  ChevronDown,
  ChevronUp,
  FileText,
  SlidersHorizontal,
} from "lucide-react";
import { useNavigate } from "react-router-dom";
import { getShipment, getAnalysisResult } from "../services/shipmentStorage";

export default function Overview() {
  const navigate = useNavigate();
  const shipment = getShipment();
  const analysis = getAnalysisResult();

  const [copied, setCopied] = useState(false);
  const [metricMode, setMetricMode] = useState("rate");
  const [expandedSection, setExpandedSection] = useState(null);

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

  const forecast = analysis?.market_intelligence?.freight_forecast;
  const marketSnapshot = analysis?.market_intelligence?.market_snapshot;
  const recommendation = analysis?.recommendation;
  const portOps = analysis?.port_operations;
  const routeEst = analysis?.route_estimate;
  const decision = analysis?.decision;
  const risk = analysis?.risk_assessment;
  const economics = analysis?.vessel_economics;
  const cheapestV = economics?.comparison?.find(v => v.vessel_class === economics?.cheapest_feasible_vessel) || economics?.comparison?.[0];
  const cheapestCost = cheapestV?.cost_per_mt_usd ?? economics?.cheapest_cost_per_mt;

  const handleCopySummary = () => {
    const text = `SagarAI Voyage Briefing:
Route: ${origin} -> ${destination}
Cargo: ${cargo} (${Number(quantity).toLocaleString()} MT)
Recommended Action: ${decision?.action || "EVALUATE"}
Forecast Rate: $${forecast?.current_rate_usd_mt ? forecast.current_rate_usd_mt.toFixed(2) : "24.50"}/MT (30d: ${forecast?.forecast_change_percent ? (forecast.forecast_change_percent >= 0 ? "+" : "") + Number(forecast.forecast_change_percent).toFixed(1) + "%" : "Stable"})
Best Feasible Vessel: ${economics?.cheapest_feasible_vessel || recommendation?.recommended_vessel || "Panamax"}
Route Risk Score: ${Math.round(risk?.overall_risk_score ?? risk?.overall_score ?? 35)}/100 (${risk?.risk_level || "MODERATE"})`;
    navigator.clipboard.writeText(text);
    setCopied(true);
    setTimeout(() => setCopied(false), 2500);
  };

  return (
    <div className="overview-page">

      {copied && (
        <div className="interactive-toast">
          <Check size={18} color="#10b981" />
          <span>Executive Voyage Summary copied to clipboard!</span>
        </div>
      )}

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

        <div style={{ display: 'flex', gap: '10px', alignItems: 'center' }}>
          <button
            type="button"
            className="interactive-action-btn"
            onClick={handleCopySummary}
            title="Copy Voyage Brief"
          >
            {copied ? <Check size={16} color="#10b981" /> : <Copy size={16} />}
            <span>{copied ? "Copied" : "Copy Brief"}</span>
          </button>

          <div className="overview-date">
            <CalendarDays size={16} />
            <span>Planning workspace</span>
          </div>
        </div>
      </section>

      {/* INTERACTIVE WORKSPACE QUICK NAV RIBBON */}
      <div className="interactive-action-ribbon">
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <Sparkles size={16} color="#0f766e" />
          <span style={{ fontSize: '0.82rem', fontWeight: 700, color: '#0f172a' }}>
            Quick Drill-Down:
          </span>
        </div>
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
          <button type="button" className="interactive-chip" onClick={() => navigate("/forecast")}>
            <TrendingUp size={14} /> Freight Forecast
          </button>
          <button type="button" className="interactive-chip" onClick={() => navigate("/vessels")}>
            <Ship size={14} /> Vessel Economics
          </button>
          <button type="button" className="interactive-chip" onClick={() => navigate("/ports")}>
            <MapPin size={14} /> Port Intelligence
          </button>
          <button type="button" className="interactive-chip" onClick={() => navigate("/risk")}>
            <CircleAlert size={14} /> Risk Center
          </button>
          <button type="button" className="interactive-chip active" onClick={() => navigate("/decision")}>
            <Sparkles size={14} /> Decision Engine
          </button>
        </div>
      </div>

      {/* SHIPMENT CARD */}

      <section className="overview-shipment interactive-hover-card" onClick={() => navigate("/plan")}>

        <div className="overview-section-heading">
          <div>
            <p className="section-label">CURRENT SHIPMENT (CLICK TO EDIT)</p>
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
              {forecast?.current_rate_usd_mt ? `$${forecast.current_rate_usd_mt.toFixed(2)}` : "$24.50"}
            </div>

            <div className="rate-unit">
              USD / MT
            </div>

            <div className="rate-change positive">
              <ArrowUpRight size={16} />
              {forecast?.forecast_change_percent != null
                ? `${forecast.forecast_change_percent >= 0 ? "+" : ""}${Number(forecast.forecast_change_percent).toFixed(1)}% projected`
                : "3.8% this week"}
            </div>

          </div>


          <div className="overview-rate-card">

            <div className="card-label">
              NEXT WEEK (7D)
            </div>

            <div className="rate-value">
              {forecast?.forecast_7d_usd_mt != null ? `$${Number(forecast.forecast_7d_usd_mt).toFixed(2)}` : "$25.10"}
            </div>

            <div className="rate-unit">
              Forecast
            </div>

            <div className="rate-change warning">
              <ArrowUpRight size={16} />
              {forecast?.forecast_direction ? `Trend: ${forecast.forecast_direction}` : (forecast?.direction ? `Trend: ${forecast.direction}` : "Expected increase")}
            </div>

          </div>


          <div className="forecast-direction-card">

            <div className="card-label">
              MARKET DIRECTION
            </div>

            <div className="direction-icon">
              <TrendingUp size={24} />
            </div>

            <strong>
              {forecast?.forecast_direction
                ? `Market ${forecast.forecast_direction.toLowerCase()}`
                : (forecast?.direction ? `Market ${forecast.direction.toLowerCase()}` : "Moderately rising")}
            </strong>

            <p>
              {decision?.action ? `Decision recommendation: ${decision.action}.` : "Freight conditions currently favour watching the market before fixing."}
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

              <strong>
                {marketSnapshot?.bdi?.current_value != null
                  ? Math.round(marketSnapshot.bdi.current_value).toLocaleString()
                  : (typeof marketSnapshot?.bdi === "number" ? Math.round(marketSnapshot.bdi).toLocaleString() : "1,500")}
              </strong>

              <p className="positive">
                {(marketSnapshot?.bdi?.change_percent ?? marketSnapshot?.bdi_change_pct) != null
                  ? `${(marketSnapshot?.bdi?.change_percent ?? marketSnapshot?.bdi_change_pct) >= 0 ? "+" : ""}${(marketSnapshot?.bdi?.change_percent ?? marketSnapshot?.bdi_change_pct).toFixed(1)}% change`
                  : "+9.8% this week"}
              </p>
            </div>

          </div>


          <div className="signal-card">

            <div className="signal-icon">
              <Fuel size={19} />
            </div>

            <div>
              <span>FUEL (WTI)</span>

              <strong>
                {marketSnapshot?.oil_price?.current_value != null
                  ? `$${marketSnapshot.oil_price.current_value.toFixed(2)}`
                  : (marketSnapshot?.wti_oil_usd_bbl ? `$${marketSnapshot.wti_oil_usd_bbl.toFixed(2)}` : "$80.04")}
              </strong>

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
              <span>VESSEL MATCH</span>

              <strong>{recommendation?.recommended_vessel || "Balanced"}</strong>

              <p>
                {recommendation?.recommended_vessel ? "Recommended class" : "Current market"}
              </p>
            </div>

          </div>


          <div className="signal-card">

            <div className="signal-icon">
              <MapPin size={19} />
            </div>

            <div>
              <span>PORT ACTIVITY</span>

              <strong>{portOps?.worst_congestion_level || "Moderate"}</strong>

              <p>
                {portOps?.worst_congestion_score ? `Congestion: ${portOps.worst_congestion_score.toFixed(0)}/100` : "Across monitored ports"}
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
              {forecast
                ? `Trend: ${forecast.forecast_direction || forecast.direction || "Stable"}${forecast.forecast_change_percent != null ? ` (${forecast.forecast_change_percent >= 0 ? "+" : ""}${Number(forecast.forecast_change_percent).toFixed(1)}% 30d)` : ""}`
                : "Market data available"}
            </p>

            <span className="status-ready">
              {forecast ? "Evaluated" : "Ready"}
            </span>

          </div>


          <div className="decision-status">

            <div className="decision-status-top">
              <span>02</span>
              <Ship size={18} />
            </div>

            <strong>Vessel economics</strong>

            <p>
              {economics?.cheapest_feasible_vessel
                ? `${economics.cheapest_feasible_vessel}${cheapestCost != null ? ` ($${Number(cheapestCost).toFixed(2)}/MT)` : ""}`
                : (recommendation?.recommended_vessel ? `Best: ${recommendation.recommended_vessel}` : "Vessel comparison required")}
            </p>

            <span className="status-ready">
              {economics ? "Optimized" : "Ready"}
            </span>

          </div>


          <div className={(risk?.overall_risk_score ?? risk?.overall_score) > 50 ? "decision-status status-attention" : "decision-status"}>

            <div className="decision-status-top">
              <span>03</span>
              <CircleAlert size={18} />
            </div>

            <strong>Operational risk</strong>

            <p>
              {risk?.risk_level
                ? `Score: ${Math.round(risk?.overall_risk_score ?? risk?.overall_score ?? 35)}/100 (${risk.risk_level})`
                : "Review port and weather signals"}
            </p>

            <span className={(risk?.overall_risk_score ?? risk?.overall_score) > 50 ? "status-review" : "status-ready"}>
              {risk?.risk_level || "Ready"}
            </span>

          </div>

        </div>

      </section>

    </div>
  );
}