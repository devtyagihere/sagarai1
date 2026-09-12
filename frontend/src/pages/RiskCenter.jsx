import { useState } from "react";
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
  CheckSquare,
  Square,
  Sparkles,
  SlidersHorizontal,
} from "lucide-react";
import { useNavigate } from "react-router-dom";
import { getShipment, getAnalysisResult } from "../services/shipmentStorage";

export default function RiskCenter() {
  const navigate = useNavigate();
  const shipment = getShipment();
  const analysis = getAnalysisResult();

  const [mitigations, setMitigations] = useState({
    weatherRouting: true,
    demurrageBuffer: false,
    bunkerHedge: false,
  });

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

  const risk = analysis?.risk_assessment;
  const portOps = analysis?.port_operations;
  const forecast = analysis?.market_intelligence?.freight_forecast;
  const economics = analysis?.vessel_economics;

  const weatherScore = risk?.weather_risk?.weather_risk_score ?? 24;
  const marineScore = risk?.marine_risk?.marine_risk_score ?? 18;
  const portScore = portOps?.destination?.congestion_score ?? portOps?.worst_congestion_score ?? 35;
  const marketScore = forecast ? Math.min(80, Math.max(15, Math.round(Math.abs(forecast.forecast_change_percent || 5) * 4))) : 28;
  const vesselScore = economics?.cheapest_feasible_vessel ? 18 : 38;

  const totalRiskSum = Math.max(1, weatherScore + marineScore + portScore + marketScore + vesselScore);
  const portPct = Math.round((portScore / totalRiskSum) * 100);
  const marketPct = Math.round((marketScore / totalRiskSum) * 100);
  const weatherPct = Math.round((weatherScore / totalRiskSum) * 100);
  const marinePct = Math.round((marineScore / totalRiskSum) * 100);
  const vesselPct = Math.max(0, 100 - portPct - marketPct - weatherPct - marinePct);

  const rawOverall = risk?.overall_risk_score ?? risk?.overall_score ?? 35;

  const mitigationDiscount =
    (mitigations.weatherRouting ? 10 : 0) +
    (mitigations.demurrageBuffer ? 8 : 0) +
    (mitigations.bunkerHedge ? 6 : 0);

  const effectiveRiskScore = Math.max(5, Math.round(rawOverall - mitigationDiscount));

  return (
    <div className="risk-page">

      {/* HEADER */}

      <section className="risk-header">
        <div>
          <p className="section-label">RISK CENTER &amp; MITIGATION SIMULATOR</p>

          <h1>See what could disrupt the voyage.</h1>

          <p>
            Review operational, meteorological and market risks, and simulate protective clauses to minimize voyage exposure.
          </p>
        </div>

        <div className="risk-header-status">
          <ShieldCheck size={17} />
          <span>Risk assessment workspace</span>
        </div>
      </section>

      {/* INTERACTIVE MITIGATION STRATEGY BUILDER */}
      <section className="interactive-slider-box" style={{ marginBottom: '20px', background: '#f8fafc', border: '1.5px solid #10b981' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '12px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <Sparkles size={18} color="#059669" />
            <strong style={{ fontSize: '0.95rem', color: '#0f172a' }}>Interactive Risk Mitigation Builder</strong>
          </div>
          <div className="interactive-pill-tag green">
            -{mitigationDiscount} Risk Points Hedged
          </div>
        </div>

        <p style={{ fontSize: '0.82rem', color: '#64748b', marginBottom: '14px' }}>
          Toggle standard maritime risk mitigations to calculate residual post-mitigation risk score:
        </p>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(260px, 1fr))', gap: '10px' }}>
          {[
            { id: 'weatherRouting', label: 'Dynamic Weather Routing Optimization', discount: '-10 pts', desc: 'Avoids heavy sea states & monsoon swells' },
            { id: 'demurrageBuffer', label: 'Port Demurrage 48h Buffer Clause', discount: '-8 pts', desc: 'Hedges against discharge port congestion' },
            { id: 'bunkerHedge', label: 'Bunker Fuel Price Ceiling Lock', discount: '-6 pts', desc: 'Caps VLSFO/MGO price exposure during voyage' },
          ].map((item) => (
            <div
              key={item.id}
              onClick={() => setMitigations(prev => ({ ...prev, [item.id]: !prev[item.id] }))}
              style={{
                background: mitigations[item.id] ? '#f0fdf4' : '#ffffff',
                border: mitigations[item.id] ? '1.5px solid #86efac' : '1px solid #cbd5e1',
                padding: '10px 14px',
                borderRadius: '8px',
                cursor: 'pointer',
                display: 'flex',
                alignItems: 'flex-start',
                gap: '10px',
                transition: 'all 0.2s ease',
              }}
            >
              <div style={{ marginTop: '2px', color: mitigations[item.id] ? '#059669' : '#94a3b8' }}>
                {mitigations[item.id] ? <CheckSquare size={17} /> : <Square size={17} />}
              </div>
              <div style={{ flex: 1 }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.82rem', fontWeight: 700, color: '#0f172a' }}>
                  <span>{item.label}</span>
                  <span style={{ color: '#059669', fontSize: '0.75rem' }}>{item.discount}</span>
                </div>
                <span style={{ fontSize: '0.74rem', color: '#64748b', display: 'block', marginTop: '2px' }}>{item.desc}</span>
              </div>
            </div>
          ))}
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
            <strong>
              {effectiveRiskScore}
            </strong>
            <span>/ 100</span>
          </div>

          <div className="risk-overview-copy">
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <p className="section-label">
                POST-MITIGATION VOYAGE RISK
              </p>
              {mitigationDiscount > 0 && (
                <span className="interactive-pill-tag green" style={{ fontSize: '0.68rem' }}>
                  Base: {Math.round(rawOverall)}/100
                </span>
              )}
            </div>

            <h2>{risk?.risk_level ? `${risk.risk_level} risk` : "Moderate risk"}</h2>

            <p>
              {(risk?.key_hazards && risk.key_hazards.length > 0) || (risk?.hazards_identified && risk.hazards_identified.length > 0)
                ? `Hazards identified along route: ${(risk.key_hazards || risk.hazards_identified).join("; ")}.`
                : "Current conditions do not indicate a major disruption, but operational and weather signals should be monitored."}
            </p>
          </div>

        </div>


        <div className="risk-overview-status">

          <div>
            <span>RISK LEVEL</span>
            <strong>{risk?.risk_level || "Moderate"}</strong>
          </div>

          <div>
            <span>FACTORS REVIEWED</span>
            <strong>5</strong>
          </div>

          <div>
            <span>ATTENTION ITEMS</span>
            <strong>{(risk?.key_hazards || risk?.hazards_identified || []).filter(h => !h.toLowerCase().includes("no significant")).length}</strong>
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

              <span className={weatherScore > 50 ? "risk-medium" : "risk-low"}>
                {weatherScore > 50 ? "Moderate" : "Low"} ({weatherScore.toFixed(0)}/100)
              </span>

            </div>

            <span>WEATHER & SEA STATE</span>

            <h3>{risk?.marine_risk?.sea_state ? `${risk.marine_risk.sea_state} sea conditions` : "Limited weather exposure"}</h3>

            <p>
              {risk?.weather_risk
                ? `Wind Beaufort ${risk.weather_risk.wind_speed_bft?.toFixed(0) || "4"} (${risk.weather_risk.wave_height_m?.toFixed(1) || "2.1"}m waves). Storm probability: ${risk.weather_risk.storm_probability_pct?.toFixed(0) || "5"}%.`
                : "No major weather disruption is currently indicated along the planned voyage."}
            </p>

            <div className="risk-factor-footer">
              <Wind size={15} />
              <span>Cyclone risk: {risk?.marine_risk?.cyclone_risk_pct?.toFixed(0) || "0"}%</span>
            </div>

          </div>


          {/* PORT */}

          <div className="risk-factor-card risk-attention">

            <div className="risk-factor-top">

              <div className="risk-factor-icon">
                <Anchor size={20} />
              </div>

              <span className={portScore > 50 ? "risk-high" : portScore > 25 ? "risk-medium" : "risk-low"}>
                {portOps?.destination?.congestion_level || "Moderate"} ({portScore.toFixed(0)}/100)
              </span>

            </div>

            <span>PORT OPERATIONS</span>

            <h3>{destination} congestion</h3>

            <p>
              {portOps?.destination?.vessels_waiting != null
                ? `${portOps.destination.vessels_waiting} vessels waiting at anchor, ${portOps.destination.vessels_working} working berth.`
                : "Increased activity at the destination may result in additional turnaround time."}
            </p>

            <div className="risk-factor-footer">
              <MapPin size={15} />
              <span>Avg delay: {portOps?.destination?.average_waiting_days?.toFixed(1) || "2.0"} days</span>
            </div>

          </div>


          {/* MARKET */}

          <div className="risk-factor-card">

            <div className="risk-factor-top">

              <div className="risk-factor-icon">
                <TrendingUp size={20} />
              </div>

              <span className={marketScore > 40 ? "risk-medium" : "risk-low"}>
                {forecast?.forecast_direction || "Upward"} ({marketScore.toFixed(0)}/100)
              </span>

            </div>

            <span>FREIGHT MARKET</span>

            <h3>{forecast?.forecast_change_percent != null && forecast.forecast_change_percent < 0 ? "Rates softening" : "Rates trending upward"}</h3>

            <p>
              {forecast?.forecast_change_percent != null
                ? `Predicted 30d rate change is ${forecast.forecast_change_percent >= 0 ? "+" : ""}${forecast.forecast_change_percent.toFixed(1)}%. Current rate: $${forecast.current_rate_usd_mt?.toFixed(2)}/MT.`
                : "Waiting for a later fixing opportunity may increase the effective freight cost."}
            </p>

            <div className="risk-factor-footer">
              <TrendingUp size={15} />
              <span>Horizon 30d: ${forecast?.forecast_30d_usd_mt?.toFixed(2) || "26.50"}/MT</span>
            </div>

          </div>


          {/* VESSEL */}

          <div className="risk-factor-card">

            <div className="risk-factor-top">

              <div className="risk-factor-icon">
                <Ship size={20} />
              </div>

              <span className="risk-low">
                {economics?.cheapest_feasible_vessel ? "Feasible" : "Balanced"} ({vesselScore.toFixed(0)}/100)
              </span>

            </div>

            <span>VESSEL AVAILABILITY</span>

            <h3>{economics?.cheapest_feasible_vessel ? `${economics.cheapest_feasible_vessel} fit` : "Suitable vessel supply"}</h3>

            <p>
              {economics?.comparison
                ? `${economics.comparison.filter(c => c.feasibility_status === 'FEASIBLE').length} vessel class(es) feasible for cargo capacity and port draft.`
                : "Current vessel availability provides reasonable flexibility for the planned cargo."}
            </p>

            <div className="risk-factor-footer">
              <Ship size={15} />
              <span>Voyage: ~{economics?.voyage_days?.toFixed(0) || "15"} days</span>
            </div>

          </div>

        </div>

      </section>


      {/* RISK BREAKDOWN */}

      <section className="risk-section">

        <div className="risk-section-heading">

          <div>
            <p className="section-label">
              RISK BREAKDOWN &amp; WEIGHTED CONTRIBUTION
            </p>

            <h2>Where exposure is coming from</h2>

            <p>
              Shows each standalone risk factor score (0–100) alongside its weighted relative share of total voyage exposure.
            </p>
          </div>

        </div>


        <div className="risk-breakdown-card">

          <div className="risk-breakdown-item">

            <div className="risk-breakdown-label">
              <span>Port congestion &amp; delays</span>
              <strong>Score: {Math.round(portScore)}/100 &nbsp;·&nbsp; Share: {portPct}%</strong>
            </div>

            <div className="risk-progress">
              <div
                className="risk-progress-fill"
                style={{ width: `${portPct}%` }}
              />
            </div>

          </div>


          <div className="risk-breakdown-item">

            <div className="risk-breakdown-label">
              <span>Freight market volatility</span>
              <strong>Score: {Math.round(marketScore)}/100 &nbsp;·&nbsp; Share: {marketPct}%</strong>
            </div>

            <div className="risk-progress">
              <div
                className="risk-progress-fill"
                style={{ width: `${marketPct}%` }}
              />
            </div>

          </div>


          <div className="risk-breakdown-item">

            <div className="risk-breakdown-label">
              <span>Weather exposure</span>
              <strong>Score: {Math.round(weatherScore)}/100 &nbsp;·&nbsp; Share: {weatherPct}%</strong>
            </div>

            <div className="risk-progress">
              <div
                className="risk-progress-fill"
                style={{ width: `${weatherPct}%` }}
              />
            </div>

          </div>


          <div className="risk-breakdown-item">

            <div className="risk-breakdown-label">
              <span>Marine &amp; sea state</span>
              <strong>Score: {Math.round(marineScore)}/100 &nbsp;·&nbsp; Share: {marinePct}%</strong>
            </div>

            <div className="risk-progress">
              <div
                className="risk-progress-fill"
                style={{ width: `${marinePct}%` }}
              />
            </div>

          </div>


          <div className="risk-breakdown-item">

            <div className="risk-breakdown-label">
              <span>Vessel availability &amp; fit</span>
              <strong>Score: {Math.round(vesselScore)}/100 &nbsp;·&nbsp; Share: {vesselPct}%</strong>
            </div>

            <div className="risk-progress">
              <div
                className="risk-progress-fill"
                style={{ width: `${vesselPct}%` }}
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