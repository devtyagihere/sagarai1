import { useEffect, useState } from "react";

function ScenarioComparison({ scenarioA, scenarioB, onUpdate }) {
  const [form, setForm] = useState(scenarioB);

  useEffect(() => {
    setForm(scenarioB);
  }, [scenarioB]);

  if (!scenarioA || !scenarioB) {
    return null;
  }

  const handleChange = (event) => {
    const { name, value } = event.target;

    const updatedScenario = {
      ...form,
      [name]: value,
    };

    setForm(updatedScenario);
    onUpdate(updatedScenario);
  };

  const formatQuantity = (value) => {
    if (value === "" || value === null || value === undefined) {
      return "—";
    }

    return `${Number(value).toLocaleString()} MT`;
  };

  const formatRoute = (scenario) => {
    return `${scenario.origin} → ${scenario.destination}`;
  };

  return (
    <section className="comparison-section">

      {/* =========================
          SECTION HEADER
          ========================= */}

      <div className="comparison-heading">
        <p className="section-label">WHAT-IF SCENARIO</p>

        <h2>Modify Scenario B</h2>

        <p>
          Change the parameters below to see how the scenario differs
          from your original forecast.
        </p>
      </div>

      {/* =========================
          SCENARIO B FORM
          ========================= */}

      <div className="comparison-form">

        <div className="form-field">
          <label htmlFor="comparison-origin">
            Origin
          </label>

          <input
            id="comparison-origin"
            type="text"
            name="origin"
            value={form.origin || ""}
            onChange={handleChange}
            placeholder="e.g. Australia"
          />
        </div>

        <div className="form-field">
          <label htmlFor="comparison-destination">
            Destination
          </label>

          <input
            id="comparison-destination"
            type="text"
            name="destination"
            value={form.destination || ""}
            onChange={handleChange}
            placeholder="e.g. Paradip"
          />
        </div>

        <div className="form-field">
          <label htmlFor="comparison-cargo">
            Cargo Type
          </label>

          <input
            id="comparison-cargo"
            type="text"
            name="cargoType"
            value={form.cargoType || ""}
            onChange={handleChange}
            placeholder="e.g. Coal"
          />
        </div>

        <div className="form-field">
          <label htmlFor="comparison-quantity">
            Cargo Quantity (MT)
          </label>

          <input
            id="comparison-quantity"
            type="number"
            name="quantity"
            value={form.quantity || ""}
            onChange={handleChange}
            min="1"
            placeholder="e.g. 75000"
          />
        </div>

        <div className="form-field">
          <label htmlFor="comparison-delivery-date">
            Delivery Date
          </label>

          <input
            id="comparison-delivery-date"
            type="date"
            name="deliveryDate"
            value={form.deliveryDate || ""}
            onChange={handleChange}
          />
        </div>

        <div className="form-field">
          <label htmlFor="comparison-duration">
            Contract Duration (Days)
          </label>

          <input
            id="comparison-duration"
            type="number"
            name="contractDuration"
            value={form.contractDuration || ""}
            onChange={handleChange}
            min="1"
            placeholder="e.g. 30"
          />
        </div>

        <div className="form-field full-width">
          <label htmlFor="comparison-urgency">
            Procurement Urgency
          </label>

          <select
            id="comparison-urgency"
            name="urgency"
            value={form.urgency || ""}
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

      {/* =========================
          COMPARISON TABLE
          ========================= */}

      <div className="comparison-table">

        {/* TABLE HEADER */}

        <div className="comparison-row comparison-header">
          <div>Metric</div>
          <div>Scenario A</div>
          <div>Scenario B</div>
        </div>

        {/* ROUTE */}

        <div className="comparison-row">
          <div>Route</div>

          <div>
            {formatRoute(scenarioA)}
          </div>

          <div>
            {formatRoute(form)}
          </div>
        </div>

        {/* CARGO */}

        <div className="comparison-row">
          <div>Cargo</div>

          <div>
            {scenarioA.cargoType || "—"}
          </div>

          <div>
            {form.cargoType || "—"}
          </div>
        </div>

        {/* QUANTITY */}

        <div className="comparison-row">
          <div>Quantity</div>

          <div>
            {formatQuantity(scenarioA.quantity)}
          </div>

          <div>
            {formatQuantity(form.quantity)}
          </div>
        </div>

        {/* URGENCY */}

        <div className="comparison-row">
          <div>Urgency</div>

          <div>
            {scenarioA.urgency || "—"}
          </div>

          <div>
            {form.urgency || "—"}
          </div>
        </div>

        {/* CONTRACT DURATION */}

        <div className="comparison-row">
          <div>Contract Duration</div>

          <div>
            {scenarioA.contractDuration
              ? `${scenarioA.contractDuration} days`
              : "—"}
          </div>

          <div>
            {form.contractDuration
              ? `${form.contractDuration} days`
              : "—"}
          </div>
        </div>

        {/* DELIVERY DATE */}

        <div className="comparison-row">
          <div>Delivery Date</div>

          <div>
            {scenarioA.deliveryDate || "—"}
          </div>

          <div>
            {form.deliveryDate || "—"}
          </div>
        </div>

      </div>

    </section>
  );
}

export default ScenarioComparison;