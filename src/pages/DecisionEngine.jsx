import {
  AlertTriangle,
  ArrowRight,
  CheckCircle2,
  Clock3,
  DollarSign,
  ShieldCheck,
  Ship,
  TrendingUp,
} from "lucide-react";
import { useNavigate } from "react-router-dom";
import { getShipment } from "../services/shipmentStorage";

export default function DecisionEngine() {
  const navigate = useNavigate();
  const shipment = getShipment();

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

  return (
    <div className="decision-page">

      {/* HEADER */}

      <section className="decision-header">
        <div>
          <p className="section-label">DECISION ENGINE</p>

          <h1>Turn the signals into a decision.</h1>

          <p>
            Combine freight outlook, vessel economics, port conditions
            and operational risk to understand what action makes the
            most sense for this shipment.
          </p>
        </div>

        <div className="decision-header-status">
          <ShieldCheck size={17} />
          <span>Decision workspace</span>
        </div>
      </section>


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

            <h2>Wait briefly before fixing.</h2>

            <p>
              Current market conditions suggest monitoring the freight
              market before committing to a charter.
            </p>
          </div>

          <div className="recommendation-confidence">
            <span>CONFIDENCE</span>
            <strong>Moderate</strong>
          </div>

        </div>


        <div className="recommendation-action">

          <div>
            <span>Suggested action</span>

            <strong>
              Monitor the market and review fixing opportunities.
            </strong>
          </div>

          <div className="recommendation-timing">
            <Clock3 size={17} />
            <span>Review again before fixing</span>
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
              Each part of the recommendation can be traced back to a
              measurable operational or market factor.
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

              <span className="factor-positive">
                Upward
              </span>

            </div>

            <span>FREIGHT MARKET</span>

            <strong>Rates are rising</strong>

            <p>
              A rising market creates pressure to avoid waiting too long.
            </p>

            <div className="factor-value">
              <span>Market impact</span>
              <strong>High</strong>
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

            <strong>Panamax is a strong fit</strong>

            <p>
              Cargo capacity and indicative voyage cost align well with
              the shipment.
            </p>

            <div className="factor-value">
              <span>Economic impact</span>
              <strong>Positive</strong>
            </div>

          </div>


          {/* PORT */}

          <div className="decision-factor-card">

            <div className="decision-factor-top">

              <div className="decision-factor-icon">
                <AlertTriangle size={19} />
              </div>

              <span className="factor-warning">
                Watch
              </span>

            </div>

            <span>PORT CONDITIONS</span>

            <strong>Destination congestion</strong>

            <p>
              Waiting time at {destination} could increase the effective
              voyage cost.
            </p>

            <div className="factor-value">
              <span>Operational impact</span>
              <strong>Moderate</strong>
            </div>

          </div>


          {/* RISK */}

          <div className="decision-factor-card">

            <div className="decision-factor-top">

              <div className="decision-factor-icon">
                <ShieldCheck size={19} />
              </div>

              <span className="factor-neutral">
                Moderate
              </span>

            </div>

            <span>OVERALL RISK</span>

            <strong>Manageable exposure</strong>

            <p>
              No major disruption is currently indicated along the
              planned voyage.
            </p>

            <div className="factor-value">
              <span>Risk impact</span>
              <strong>42 / 100</strong>
            </div>

          </div>

        </div>

      </section>


      {/* OPTIONS */}

      <section className="decision-section">

        <div className="decision-section-heading">

          <div>
            <p className="section-label">
              AVAILABLE ACTIONS
            </p>

            <h2>Compare your fixing choices</h2>

            <p>
              The decision engine evaluates the trade-off between fixing
              now, waiting, and taking a more conservative approach.
            </p>
          </div>

        </div>


        <div className="decision-options">

          {/* FIX NOW */}

          <div className="decision-option">

            <div className="decision-option-number">
              01
            </div>

            <div className="decision-option-main">

              <div className="decision-option-title">
                <h3>Fix now</h3>

                <span className="option-risk">
                  Lower uncertainty
                </span>
              </div>

              <p>
                Lock in the current freight level and reduce exposure to
                further market movement.
              </p>

              <div className="option-metrics">

                <div>
                  <span>PRICE</span>
                  <strong>$24.50 / MT</strong>
                </div>

                <div>
                  <span>MARKET EXPOSURE</span>
                  <strong>Low</strong>
                </div>

                <div>
                  <span>PORT EXPOSURE</span>
                  <strong>Moderate</strong>
                </div>

              </div>

            </div>

          </div>


          {/* WAIT */}

          <div className="decision-option decision-option-recommended">

            <div className="decision-option-number">
              02
            </div>

            <div className="decision-option-main">

              <div className="decision-option-title">
                <h3>Wait briefly</h3>

                <span className="option-recommended">
                  Recommended
                </span>
              </div>

              <p>
                Continue monitoring the market while retaining the
                flexibility to fix when conditions become more favourable.
              </p>

              <div className="option-metrics">

                <div>
                  <span>EXPECTED RANGE</span>
                  <strong>$24–26 / MT</strong>
                </div>

                <div>
                  <span>MARKET EXPOSURE</span>
                  <strong>Moderate</strong>
                </div>

                <div>
                  <span>UPSIDE</span>
                  <strong>Moderate</strong>
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
                <h3>Delay fixing</h3>

                <span className="option-risk">
                  Higher exposure
                </span>
              </div>

              <p>
                Hold the decision for longer in expectation of a better
                freight opportunity.
              </p>

              <div className="option-metrics">

                <div>
                  <span>MARKET EXPOSURE</span>
                  <strong>High</strong>
                </div>

                <div>
                  <span>PORT EXPOSURE</span>
                  <strong>Moderate</strong>
                </div>

                <div>
                  <span>DOWNSIDE</span>
                  <strong>Higher</strong>
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

      <section className="decision-next">

        <div>
          <p className="section-label">
            NEXT STEP
          </p>

          <h2>
            Test the decision before you commit.
          </h2>

          <p>
            Use the scenario simulator to compare different freight,
            timing and operational assumptions.
          </p>
        </div>

        <button
          className="text-action"
          onClick={() => navigate("/simulator")}
          type="button"
        >
          Open scenario simulator
          <ArrowRight size={16} />
        </button>

      </section>

    </div>
  );
}