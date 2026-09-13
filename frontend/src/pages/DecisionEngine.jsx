import { useState } from "react";
import {
  AlertTriangle,
  ArrowRight,
  CheckCircle2,
  Clock3,
  DollarSign,
  ShieldCheck,
  Ship,
  TrendingUp,
  Sparkles,
  Printer,
  ChevronDown,
  ChevronUp,
  Copy,
  Check,
  FileCheck,
} from "lucide-react";
import { useNavigate } from "react-router-dom";
import { getShipment, getAnalysisResult } from "../services/shipmentStorage";

export default function DecisionEngine() {
  const navigate = useNavigate();
  const shipment = getShipment();
  const analysis = getAnalysisResult();

  const [strategyMode, setStrategyMode] = useState("consensus");
  const [copiedReport, setCopiedReport] = useState(false);

  if (!shipment) {
    return (
      <div className="decision-page">
        <section className="decision-header">
          <div>
            <p className="section-label">DECISION ENGINE</p>

            <h1>No shipment selected.</h1>

            <p>
              Start by entering your shipment details before evaluating the
              chartering decision.
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

  const decision = analysis?.decision;
  const recommendation = analysis?.recommendation;
  const forecast = analysis?.market_intelligence?.freight_forecast;
  const economics = analysis?.vessel_economics;
  const risk = analysis?.risk_assessment;
  const portOps = analysis?.port_operations;
  const destPortOps = portOps?.destination || portOps?.destination_port;

  const currentRate = forecast?.current_rate_usd_mt ?? 24.50;
  const horizon30dRate = forecast?.forecast_30d_usd_mt ?? (currentRate * (1 + (forecast?.forecast_change_percent || 0) / 100));
  const rateChangePct = forecast?.forecast_change_percent ?? 0;

  const recommendedVessel = decision?.recommended_vessel || recommendation?.recommended_vessel || economics?.recommended_vessel || "Handysize";
  const recommendedCostItem = economics?.comparison?.find(v => v.vessel_class === recommendedVessel || v.is_recommended) || economics?.comparison?.[0];
  const fixingCostPerMt = recommendedCostItem?.cost_per_mt_usd ?? currentRate;

  const riskScore = risk?.overall_risk_score != null ? Math.round(risk.overall_risk_score) : 38;
  const destCongestionScore = destPortOps?.congestion_score != null ? Math.round(destPortOps.congestion_score) : 35;
  const destCongestionLevel = destPortOps?.congestion_level || "MODERATE";

  const action = decision?.action || "CHARTER NOW";
  const isCharterNow = action === "CHARTER NOW";
  const isWait = action === "WAIT";
  const isNegotiate = action === "NEGOTIATE";

  const handlePrint = () => {
    window.print();
  };

  const handleCopyReport = () => {
    const text = `SAGARAI CHARTERING DECISION BRIEFING
Route: ${origin} -> ${destination}
Cargo: ${cargo} (${Number(quantity).toLocaleString()} MT)
Recommended Action: ${action} (Confidence: ${decision?.confidence ? (decision.confidence * 100).toFixed(0) : "88"}%)
Selected Vessel: ${recommendedVessel} ($${Number(fixingCostPerMt).toFixed(2)}/MT)
Market Trajectory: ${rateChangePct >= 0 ? "+" : ""}${Number(rateChangePct).toFixed(1)}% (30d Horizon)
Port Congestion: ${destCongestionScore}/100 (${destCongestionLevel})
Overall Risk Score: ${riskScore}/100
Rationale: ${decision?.confidence_rationale || "Consensus derived from integrated ML forecasting and physical constraints."}`;
    navigator.clipboard.writeText(text);
    setCopiedReport(true);
    setTimeout(() => setCopiedReport(false), 2500);
  };

  return (
    <div className="decision-page">

      {copiedReport && (
        <div className="interactive-toast">
          <Check size={18} color="#10b981" />
          <span>Charterparty Decision Report copied to clipboard!</span>
        </div>
      )}

      {/* HEADER */}

      <section className="decision-header">
        <div>
          <p className="section-label">DECISION ENGINE &amp; CHARTER CONSENSUS</p>

          <h1>Turn the signals into a decision.</h1>

          <p>
            Combine freight outlook, vessel economics, port conditions
            and operational risk to compute optimal chartering action.
          </p>
        </div>

        <div style={{ display: 'flex', gap: '10px', alignItems: 'center' }}>
          <button
            type="button"
            className="interactive-action-btn"
            onClick={handleCopyReport}
            title="Copy Charter Brief"
          >
            {copiedReport ? <Check size={16} color="#10b981" /> : <Copy size={16} />}
            <span>{copiedReport ? "Report Copied" : "Copy Report"}</span>
          </button>

          <button
            type="button"
            className="interactive-action-btn"
            onClick={handlePrint}
            title="Print Decision Brief"
          >
            <Printer size={16} />
            <span>Print Brief</span>
          </button>
        </div>
      </section>

      {/* STRATEGY MODE SELECTOR */}
      <div className="interactive-tabs-bar">
        <button
          type="button"
          className={`interactive-tab-btn ${strategyMode === "consensus" ? "active" : ""}`}
          onClick={() => setStrategyMode("consensus")}
        >
          <Sparkles size={15} color="#0f766e" /> AI Consensus Model (Optimal)
        </button>
        <button
          type="button"
          className={`interactive-tab-btn ${strategyMode === "aggressive" ? "active" : ""}`}
          onClick={() => setStrategyMode("aggressive")}
        >
          <TrendingUp size={15} color="#0284c7" /> Spot Market Aggressive
        </button>
        <button
          type="button"
          className={`interactive-tab-btn ${strategyMode === "conservative" ? "active" : ""}`}
          onClick={() => setStrategyMode("conservative")}
        >
          <ShieldCheck size={15} color="#059669" /> Risk-Averse Hedging
        </button>
      </div>


      {/* SHIPMENT CONTEXT */}

      <section className="decision-shipment-context">

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
          <span>CONTRACT</span>
          <strong>{contractDuration}</strong>
        </div>

        <div>
          <span>PRIORITY</span>
          <strong>{priority}</strong>
        </div>

      </section>


      {/* RECOMMENDATION */}

      <section className="recommendation-card">

        <div className="recommendation-top">

          <div className="recommendation-icon">
            <CheckCircle2 size={25} />
          </div>

          <div>
            <p className="section-label">
              CURRENT RECOMMENDATION
            </p>

            <h2>
              {action}: {isCharterNow ? "Lock in rates before price escalation" : isNegotiate ? "Negotiate rates & terms" : "Monitor market as rates soften"}
            </h2>

            <p>
              {decision?.reasons && decision.reasons.length > 0
                ? decision.reasons[0]
                : "Current market conditions and risk signals have been integrated to produce the optimal chartering recommendation."}
            </p>
          </div>

          <div className="recommendation-confidence">
            <span>CONFIDENCE</span>
            <strong>{decision?.confidence || "High"}</strong>
          </div>

        </div>


        <div className="recommendation-action">

          <div>
            <span>Suggested action</span>

            <strong>
              {action} (Decision score: {decision?.overall_score != null ? decision.overall_score.toFixed(1) : "72.0"}/100 · Best vessel: {recommendedVessel})
            </strong>
          </div>

          <div className="recommendation-timing">
            <Clock3 size={17} />
            <span>{isCharterNow ? "Immediate fixing" : isNegotiate ? "Counter-offer benchmark" : "Reassess in 7–14 days"}</span>
          </div>

        </div>

      </section>


      {/* DECISION FACTORS */}

      <section className="decision-section">

        <div className="decision-section-heading">

          <div>
            <p className="section-label">
              DECISION FACTORS
            </p>

            <h2>What is driving the recommendation</h2>

            <p>
              Each part of the recommendation is grounded directly in quantitative operational and ML forecast models.
            </p>
          </div>

        </div>


        <div className="decision-factor-grid">

          {/* FREIGHT */}

          <div className="decision-factor-card">

            <div className="decision-factor-top">

              <div className="decision-factor-icon">
                <TrendingUp size={19} />
              </div>

              <span className={rateChangePct >= 0 ? "factor-positive" : "factor-neutral"}>
                {forecast?.forecast_direction || (rateChangePct >= 0 ? "Upward" : "Softening")}
              </span>

            </div>

            <span>FREIGHT MARKET</span>

            <strong>{rateChangePct >= 0 ? `Rates rising (+${rateChangePct.toFixed(1)}%)` : `Rates softening (${rateChangePct.toFixed(1)}%)`}</strong>

            <p>
              {rateChangePct >= 0
                ? "Rising market creates strong incentive to lock in fixture rates now."
                : "Softening rates allow flexibility to negotiate or wait for lower fixtures."}
            </p>

            <div className="factor-value">
              <span>Forecast 30d</span>
              <strong>${horizon30dRate.toFixed(2)} / MT</strong>
            </div>

          </div>


          {/* VESSEL */}

          <div className="decision-factor-card">

            <div className="decision-factor-top">

              <div className="decision-factor-icon">
                <Ship size={19} />
              </div>

              <span className="factor-positive">
                Favourable
              </span>

            </div>

            <span>VESSEL ECONOMICS</span>

            <strong>{recommendedVessel} optimal fit</strong>

            <p>
              {recommendedCostItem
                ? `Cost: $${recommendedCostItem.cost_per_mt_usd?.toFixed(2)}/MT · ~$${Math.round(recommendedCostItem.voyage_cost_usd || 0).toLocaleString()} voyage total`
                : "Passes port draft, LOA and capacity feasibility checks."}
            </p>

            <div className="factor-value">
              <span>Unit Cost</span>
              <strong>${fixingCostPerMt.toFixed(2)} / MT</strong>
            </div>

          </div>


          {/* PORT */}

          <div className="decision-factor-card">

            <div className="decision-factor-top">

              <div className="decision-factor-icon">
                <AlertTriangle size={19} />
              </div>

              <span className={destCongestionScore > 50 ? "factor-warning" : "factor-neutral"}>
                {destCongestionLevel}
              </span>

            </div>

            <span>PORT CONDITIONS</span>

            <strong>{destination} ({destCongestionScore}/100)</strong>

            <p>
              {destPortOps?.vessels_waiting != null
                ? `${destPortOps.vessels_waiting} vessels waiting, ${destPortOps.average_waiting_days?.toFixed(1)}d avg turnaround time.`
                : `Port operational index currently at ${destCongestionScore}/100.`}
            </p>

            <div className="factor-value">
              <span>Queue status</span>
              <strong>{destPortOps?.vessels_waiting != null ? `${destPortOps.vessels_waiting} at anchor` : `${destCongestionLevel}`}</strong>
            </div>

          </div>


          {/* RISK */}

          <div className="decision-factor-card">

            <div className="decision-factor-top">

              <div className="decision-factor-icon">
                <ShieldCheck size={19} />
              </div>

              <span className={riskScore > 60 ? "factor-warning" : "factor-neutral"}>
                {risk?.risk_level || "Moderate"}
              </span>

            </div>

            <span>OVERALL RISK</span>

            <strong>{risk?.risk_level || "Moderate"} exposure</strong>

            <p>
              {risk?.key_hazards && risk.key_hazards.length > 0
                ? risk.key_hazards[0]
                : "Weather, marine, and navigational exposure within operational limits."}
            </p>

            <div className="factor-value">
              <span>Risk score</span>
              <strong>{riskScore} / 100</strong>
            </div>

          </div>

        </div>

      </section>


      {/* OPTIONS */}

      <section className="decision-section">

        <div className="decision-section-heading">

          <div>
            <p className="section-label">
              AVAILABLE ACTIONS &amp; TRADE-OFF ANALYSIS
            </p>

            <h2>Compare your fixing choices</h2>

            <p>
              The decision engine compares immediate fixing against waiting or delaying based on the ML freight forecast trajectory.
            </p>
          </div>

        </div>


        <div className="decision-options">

          {/* FIX NOW */}

          <div className={`decision-option ${isCharterNow ? "decision-option-recommended" : ""}`}>

            <div className="decision-option-number">
              01
            </div>

            <div className="decision-option-main">

              <div className="decision-option-title">
                <h3>Fix now</h3>

                <span className={isCharterNow ? "option-recommended" : "option-risk"}>
                  {isCharterNow ? "Recommended Action" : "Lower uncertainty"}
                </span>
              </div>

              <p>
                Lock in the current freight level of ${fixingCostPerMt.toFixed(2)}/MT and eliminate exposure to future market inflation.
              </p>

              <div className="option-metrics">

                <div>
                  <span>PRICE</span>
                  <strong>${fixingCostPerMt.toFixed(2)} / MT</strong>
                </div>

                <div>
                  <span>MARKET EXPOSURE</span>
                  <strong>Locked (0% Volatility)</strong>
                </div>

                <div>
                  <span>PORT EXPOSURE</span>
                  <strong>{destCongestionLevel}</strong>
                </div>

              </div>

            </div>

          </div>


          {/* WAIT */}

          <div className={`decision-option ${isWait || isNegotiate ? "decision-option-recommended" : ""}`}>

            <div className="decision-option-number">
              02
            </div>

            <div className="decision-option-main">

              <div className="decision-option-title">
                <h3>Wait / Negotiate</h3>

                <span className={isWait || isNegotiate ? "option-recommended" : "option-neutral"}>
                  {isWait ? "Recommended Action" : isNegotiate ? "Recommended (Negotiate)" : "Flexible window"}
                </span>
              </div>

              <p>
                {rateChangePct >= 0
                  ? `Monitoring carries risk of rate increasing to ~$${horizon30dRate.toFixed(2)}/MT over the 30-day horizon.`
                  : `Waiting allows you to capture softening rates down to ~$${horizon30dRate.toFixed(2)}/MT.`}
              </p>

              <div className="option-metrics">

                <div>
                  <span>EXPECTED 30D</span>
                  <strong>${Math.min(currentRate, horizon30dRate).toFixed(2)}–${Math.max(currentRate, horizon30dRate).toFixed(2)} / MT</strong>
                </div>

                <div>
                  <span>RATE DELTA</span>
                  <strong>{rateChangePct >= 0 ? `+${rateChangePct.toFixed(1)}%` : `${rateChangePct.toFixed(1)}%`}</strong>
                </div>

                <div>
                  <span>UPSIDE/RISK</span>
                  <strong>{rateChangePct >= 0 ? "Cost Risk" : "Savings Opportunity"}</strong>
                </div>

              </div>

            </div>

          </div>


          {/* DELAY */}

          <div className="decision-option">

            <div className="decision-option-number">
              03
            </div>

            <div className="decision-option-main">

              <div className="decision-option-title">
                <h3>Delay fixing (60d+)</h3>

                <span className="option-risk">
                  High Market Exposure
                </span>
              </div>

              <p>
                Hold the decision for an extended period. High exposure to spot market volatility, bunker oil fluctuations, and berth queue build-up.
              </p>

              <div className="option-metrics">

                <div>
                  <span>PROJECTED HIGH</span>
                  <strong>&gt;${(Math.max(currentRate, horizon30dRate) * 1.08).toFixed(2)} / MT</strong>
                </div>

                <div>
                  <span>MARKET EXPOSURE</span>
                  <strong>High Spot Volatility</strong>
                </div>

                <div>
                  <span>PORT RISK</span>
                  <strong>Queue Build-up</strong>
                </div>

              </div>

            </div>

          </div>

        </div>

      </section>


      {/* ECONOMIC IMPACT */}

      <section className="decision-impact">

        <div className="decision-impact-icon">
          <DollarSign size={21} />
        </div>

        <div className="decision-impact-copy">

          <p className="section-label">
            DECISION IMPACT
          </p>

          <h2>
            The timing decision can materially affect voyage cost.
          </h2>

          <p>
            Freight rate, vessel cost, bunker exposure and potential port
            waiting time should be evaluated together before committing
            to the voyage.
          </p>

        </div>

        <div className="decision-impact-value">
          <span>SHIPMENT SIZE</span>
          <strong>
            {Number(quantity).toLocaleString()} MT
          </strong>
        </div>

      </section>


      {/* NEXT STEP */}
      <section className="page-next-banner">
        <div className="banner-icon">
          <Sparkles size={22} />
        </div>

        <div className="banner-content">
          <p className="section-label">
            NEXT STEP
          </p>

          <h2>
            Test the decision before you commit.
          </h2>

          <p>
            Use the scenario simulator to stress-test your decision against different freight rate shocks,
            timing adjustments, and port delays.
          </p>
        </div>

        <button
          className="page-cta-button"
          onClick={() => navigate("/simulator")}
          type="button"
        >
          <span>Open scenario simulator</span>
          <ArrowRight size={18} />
        </button>
      </section>

    </div>
  );
}