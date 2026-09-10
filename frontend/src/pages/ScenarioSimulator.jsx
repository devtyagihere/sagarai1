import { useState } from "react";
import {
  ArrowRight,
  BarChart3,
  Calculator,
  RotateCcw,
  SlidersHorizontal,
} from "lucide-react";
import { useNavigate } from "react-router-dom";

import ScenarioInputs from "../components/simulator/ScenarioInputs";
import ScenarioComparison from "../components/simulator/ScenarioComparison";
import WhatIfComparison from "../components/whatif/WhatIfComparison";
import { getShipment } from "../services/shipmentStorage";

export default function ScenarioSimulator() {
  const navigate = useNavigate();

  const [scenario, setScenario] = useState(null);
  const [scenarioB, setScenarioB] = useState(null);
  const [error, setError] = useState("");

  const shipment = getShipment();

  const runScenario = (scenarioData) => {
    setError("");

    if (!shipment) {
      setError(
        "No shipment has been planned yet. Please enter shipment details first."
      );
      return;
    }

    /*
      Frontend-only stage:
      Keep the user's original shipment together with the
      scenario assumptions.

      The real ML/backend calculation will replace this
      when the backend is connected.
    */
    const preparedScenario = {
      ...shipment,
      ...scenarioData,
      baseShipment: shipment,
    };

    setScenario(preparedScenario);

    setScenarioB({
      ...preparedScenario,
      scenarioName: "Alternative scenario",
    });
  };

  const resetSimulator = () => {
    setScenario(null);
    setScenarioB(null);
    setError("");
  };

  if (!shipment) {
    return (
      <div className="simulator-page">

        <section className="simulator-header">
          <div>
            <p className="section-label">
              SCENARIO SIMULATOR
            </p>

            <h1>
              No shipment selected.
            </h1>

            <p>
              Start by planning a shipment before testing different
              freight and operational assumptions.
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

  return (
    <div className="simulator-page">

      {/* HEADER */}

      <section className="simulator-header">

        <div>
          <p className="section-label">
            SCENARIO SIMULATOR
          </p>

          <h1>
            What changes if your assumptions change?
          </h1>

          <p>
            Test different freight, cargo and operational assumptions
            before making the final shipment decision.
          </p>
        </div>

        <div className="simulator-header-status">
          <SlidersHorizontal size={17} />
          <span>What-if planning workspace</span>
        </div>

      </section>


      {/* SHIPMENT CONTEXT */}

      <section className="simulator-shipment-context">

        <div>
          <span>ROUTE</span>
          <strong>
            {shipment.origin} → {shipment.destination}
          </strong>
        </div>

        <div>
          <span>CARGO</span>
          <strong>{shipment.cargo}</strong>
        </div>

        <div>
          <span>QUANTITY</span>
          <strong>
            {Number(shipment.quantity).toLocaleString()} MT
          </strong>
        </div>

        <div>
          <span>DELIVERY</span>
          <strong>{shipment.deliveryDate}</strong>
        </div>

        <div>
          <span>PRIORITY</span>
          <strong>{shipment.priority}</strong>
        </div>

      </section>


      {/* INTRO */}

      <section className="simulator-intro">

        <div className="simulator-intro-icon">
          <Calculator size={21} />
        </div>

        <div>
          <p className="section-label">
            HOW IT WORKS
          </p>

          <h2>
            Change one assumption at a time.
          </h2>

          <p>
            Compare the resulting freight economics and decision impact
            to understand which assumptions matter most.
          </p>
        </div>

      </section>


      {/* INPUTS */}

      <section className="simulator-section">

        <div className="simulator-section-heading">

          <div>
            <p className="section-label">
              SCENARIO INPUTS
            </p>

            <h2>
              Build your scenario
            </h2>

            <p>
              Enter the assumptions you want to test.
            </p>
          </div>

          {scenario && (
            <button
              className="simulator-reset"
              onClick={resetSimulator}
              type="button"
            >
              <RotateCcw size={15} />
              Reset
            </button>
          )}

        </div>


        <div className="simulator-input-card">

          <ScenarioInputs
            onRunScenario={runScenario}
          />

        </div>


        {error && (
          <div className="simulator-error">
            {error}
          </div>
        )}

      </section>


      {/* RESULTS */}

      {scenario && (
        <>

          <section className="simulator-section">

            <div className="simulator-section-heading">

              <div>
                <p className="section-label">
                  SCENARIO RESULT
                </p>

                <h2>
                  Scenario prepared
                </h2>

                <p>
                  Your selected shipment and scenario assumptions are
                  ready for comparison.
                </p>
              </div>

            </div>


            <div className="simulator-result-card">

              <div className="simulator-result-icon">
                <BarChart3 size={21} />
              </div>

              <div>
                <span>ANALYSIS STATUS</span>

                <strong>
                  Scenario ready
                </strong>

                <p>
                  The scenario has been prepared using your current
                  shipment information.
                </p>
              </div>

            </div>


            <ScenarioComparison
              scenario={scenario}
              scenarioB={scenarioB}
            />

          </section>


          <section className="simulator-section">

            <div className="simulator-section-heading">

              <div>
                <p className="section-label">
                  WHAT-IF COMPARISON
                </p>

                <h2>
                  Compare the decision impact
                </h2>

                <p>
                  See how changing the scenario can influence the
                  resulting decision.
                </p>
              </div>

            </div>


            <WhatIfComparison
              scenario={scenario}
              scenarioB={scenarioB}
            />

          </section>


          {/* NEXT STEP */}

          <section className="simulator-next">

            <div>

              <p className="section-label">
                NEXT STEP
              </p>

              <h2>
                Refine the decision before you commit.
              </h2>

              <p>
                Use different assumptions to understand how the
                shipment decision may change.
              </p>

            </div>

            <button
              className="text-action"
              onClick={() => navigate("/decision")}
              type="button"
            >
              Return to decision engine
              <ArrowRight size={16} />
            </button>

          </section>

        </>
      )}

    </div>
  );
}