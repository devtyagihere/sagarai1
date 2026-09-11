import { useState } from "react";

function WhatIfComparison({ scenario }) {
  const [whatIf, setWhatIf] = useState({
    quantity: scenario?.quantity || "",
    deliveryDate: scenario?.deliveryDate || "",
    urgency: scenario?.urgency || "medium",
  });

  const handleChange = (event) => {
    const { name, value } = event.target;

    setWhatIf((previous) => ({
      ...previous,
      [name]: value,
    }));
  };

  return (
    <section className="whatif-section">
      <div className="whatif-header">
        <div>
          <p className="section-label">SCENARIO INTELLIGENCE</p>

          <h2>What-If Comparison</h2>

          <p>
            Change the commercial conditions and compare the expected
            freight outcome with your current scenario.
          </p>
        </div>

        <span className="whatif-badge">
          INTERACTIVE
        </span>
      </div>

      <div className="whatif-grid">

        {/* CURRENT SCENARIO */}

        <div className="scenario-box current-box">
          <p className="box-label">CURRENT SCENARIO</p>

          <h3>
            {scenario?.origin || "—"} → {scenario?.destination || "—"}
          </h3>

          <div className="scenario-details">
            <div>
              <span>Cargo</span>
              <strong>{scenario?.cargoType || "—"}</strong>
            </div>

            <div>
              <span>Quantity</span>
              <strong>
                {scenario?.quantity
                  ? Number(scenario.quantity).toLocaleString()
                  : "—"}{" "}
                MT
              </strong>
            </div>

            <div>
              <span>Delivery</span>
              <strong>{scenario?.deliveryDate || "—"}</strong>
            </div>

            <div>
              <span>Urgency</span>
              <strong>{scenario?.urgency || "—"}</strong>
            </div>
          </div>
        </div>

        {/* WHAT-IF SCENARIO */}

        <div className="scenario-box whatif-box">
          <p className="box-label">WHAT-IF SCENARIO</p>

          <h3>Modify Parameters</h3>

          <div className="whatif-fields">

            <div className="whatif-field">
              <label htmlFor="whatif-quantity">
                Cargo Quantity (MT)
              </label>

              <input
                id="whatif-quantity"
                name="quantity"
                type="number"
                min="1"
                value={whatIf.quantity}
                onChange={handleChange}
              />
            </div>

            <div className="whatif-field">
              <label htmlFor="whatif-date">
                Required Delivery Date
              </label>

              <input
                id="whatif-date"
                name="deliveryDate"
                type="date"
                value={whatIf.deliveryDate}
                onChange={handleChange}
              />
            </div>

            <div className="whatif-field">
              <label htmlFor="whatif-urgency">
                Procurement Urgency
              </label>

              <select
                id="whatif-urgency"
                name="urgency"
                value={whatIf.urgency}
                onChange={handleChange}
              >
                <option value="low">
                  Low — Flexible procurement
                </option>

                <option value="medium">
                  Medium — Normal procurement
                </option>

                <option value="high">
                  High — Time sensitive
                </option>
              </select>
            </div>

          </div>
        </div>

      </div>
    </section>
  );
}

export default WhatIfComparison;