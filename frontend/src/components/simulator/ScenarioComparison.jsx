import { useState } from "react";
import { ChevronDown } from "lucide-react";

function ScenarioComparison({ scenarioA, scenarioB, onUpdate }) {
  const [editedScenario, setEditedScenario] = useState(null);

  if (!scenarioA || !scenarioB) {
    return null;
  }

  const form = editedScenario || scenarioB;

  const handleChange = (event) => {
    const { name, value } = event.target;

    const updatedScenario = {
      ...form,
      [name]: value,
    };

    setEditedScenario(updatedScenario);
    onUpdate(updatedScenario);
  };

  const formatQuantity = (value) => {
    if (value === "" || value === null || value === undefined) {
      return "—";
    }

    return `${Number(value).toLocaleString()} MT`;
  };

  const formatRoute = (scenario) => {
    return `${scenario.origin || "—"} → ${scenario.destination || "—"}`;
  };

  return (
    <section className="comparison-section">
      <div className="comparison-heading">
        <p className="section-label">WHAT-IF SCENARIO</p>

        <h2>Modify Scenario B</h2>

        <p>
          Change the parameters below to see how the scenario differs
          from your original forecast.
        </p>
      </div>

      <div className="comparison-form">
        <div className="form-grid">
          <div className="input-group">
            <label htmlFor="comparison-origin">Origin</label>
            <div className="input-wrapper">
              <input
                id="comparison-origin"
                type="text"
                name="origin"
                value={form.origin || ""}
                onChange={handleChange}
                placeholder="e.g. Australia"
              />
            </div>
          </div>

          <div className="input-group">
            <label htmlFor="comparison-destination">Destination</label>
            <div className="input-wrapper">
              <input
                id="comparison-destination"
                type="text"
                name="destination"
                value={form.destination || ""}
                onChange={handleChange}
                placeholder="e.g. Paradip"
              />
            </div>
          </div>

          <div className="input-group">
            <label htmlFor="comparison-cargo">Cargo Type</label>
            <div className="input-wrapper">
              <input
                id="comparison-cargo"
                type="text"
                name="cargoType"
                value={form.cargoType || ""}
                onChange={handleChange}
                placeholder="e.g. Coal"
              />
            </div>
          </div>

          <div className="input-group">
            <label htmlFor="comparison-quantity">Cargo Quantity (MT)</label>
            <div className="quantity-wrapper">
              <input
                id="comparison-quantity"
                type="number"
                name="quantity"
                value={form.quantity || ""}
                onChange={handleChange}
                min="1"
                placeholder="e.g. 75000"
              />
              <span>MT</span>
            </div>
          </div>

          <div className="input-group">
            <label htmlFor="comparison-delivery-date">Delivery Date</label>
            <div className="input-wrapper">
              <input
                id="comparison-delivery-date"
                type="date"
                name="deliveryDate"
                value={form.deliveryDate || ""}
                onChange={handleChange}
              />
            </div>
          </div>

          <div className="input-group">
            <label htmlFor="comparison-duration">Contract Duration (Days)</label>
            <div className="quantity-wrapper">
              <input
                id="comparison-duration"
                type="number"
                name="contractDuration"
                value={form.contractDuration || ""}
                onChange={handleChange}
                min="1"
                placeholder="e.g. 30"
              />
              <span>DAYS</span>
            </div>
          </div>

          <div className="input-group full-width" style={{ gridColumn: "1 / -1" }}>
            <label htmlFor="comparison-urgency">Procurement Urgency</label>
            <div className="select-wrapper">
              <select
                id="comparison-urgency"
                name="urgency"
                value={form.urgency || "medium"}
                onChange={handleChange}
              >
                <option value="low">Low — Flexible procurement</option>
                <option value="medium">Medium — Normal procurement</option>
                <option value="high">High — Time sensitive</option>
              </select>
              <ChevronDown size={16} />
            </div>
          </div>
        </div>
      </div>

      <div className="comparison-table-wrap" style={{ marginTop: "24px" }}>
        <table className="comparison-table">
          <thead>
            <tr>
              <th>Parameter</th>
              <th>Scenario A (Base)</th>
              <th>Scenario B (Simulated)</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td>Route</td>
              <td>{formatRoute(scenarioA)}</td>
              <td>{formatRoute(form)}</td>
            </tr>
            <tr>
              <td>Cargo</td>
              <td>{scenarioA.cargoType || "—"}</td>
              <td>{form.cargoType || "—"}</td>
            </tr>
            <tr>
              <td>Quantity</td>
              <td>{formatQuantity(scenarioA.quantity)}</td>
              <td>{formatQuantity(form.quantity)}</td>
            </tr>
            <tr>
              <td>Delivery Date</td>
              <td>{scenarioA.deliveryDate || "—"}</td>
              <td>{form.deliveryDate || "—"}</td>
            </tr>
            <tr>
              <td>Contract Duration</td>
              <td>
                {scenarioA.contractDuration
                  ? `${scenarioA.contractDuration} days`
                  : "—"}
              </td>
              <td>
                {form.contractDuration
                  ? `${form.contractDuration} days`
                  : "—"}
              </td>
            </tr>
            <tr>
              <td>Urgency</td>
              <td>{scenarioA.urgency || "medium"}</td>
              <td>{form.urgency || "medium"}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </section>
  );
}

export default ScenarioComparison;