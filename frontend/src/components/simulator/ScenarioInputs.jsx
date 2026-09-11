import { useState } from "react";

function ScenarioInputs({ onSubmit }) {
  const [form, setForm] = useState({
    origin: "",
    destination: "",
    cargoType: "",
    quantity: "",
    deliveryDate: "",
    contractDuration: "",
    urgency: "",
  });

  const handleChange = (event) => {
    const { name, value } = event.target;

    setForm((previousForm) => ({
      ...previousForm,
      [name]: value,
    }));
  };

  const handleSubmit = (event) => {
    event.preventDefault();
    onSubmit(form);
  };

  return (
    <form className="scenario-form" onSubmit={handleSubmit}>
      <div className="form-grid">

        <div className="form-field">
          <label htmlFor="origin">Origin Port / Country</label>

          <input
            id="origin"
            name="origin"
            type="text"
            value={form.origin}
            onChange={handleChange}
            placeholder="e.g. Australia"
            required
          />

          <span className="form-hint">
            Where the cargo is procured
          </span>
        </div>

        <div className="form-field">
          <label htmlFor="destination">Destination Port</label>

          <input
            id="destination"
            name="destination"
            type="text"
            value={form.destination}
            onChange={handleChange}
            placeholder="e.g. Paradip"
            required
          />

          <span className="form-hint">
            Final discharge location
          </span>
        </div>

        <div className="form-field">
          <label htmlFor="cargoType">Cargo Type</label>

          <input
            id="cargoType"
            name="cargoType"
            type="text"
            value={form.cargoType}
            onChange={handleChange}
            placeholder="e.g. Coal"
            required
          />
        </div>

        <div className="form-field">
          <label htmlFor="quantity">Cargo Quantity (MT)</label>

          <input
            id="quantity"
            name="quantity"
            type="number"
            value={form.quantity}
            onChange={handleChange}
            placeholder="e.g. 75000"
            min="1"
            required
          />
        </div>

        <div className="form-field">
          <label htmlFor="deliveryDate">Required Delivery Date</label>

          <input
            id="deliveryDate"
            name="deliveryDate"
            type="date"
            value={form.deliveryDate}
            onChange={handleChange}
            required
          />
        </div>

        <div className="form-field">
          <label htmlFor="contractDuration">
            Contract Duration (Days)
          </label>

          <input
            id="contractDuration"
            name="contractDuration"
            type="number"
            value={form.contractDuration}
            onChange={handleChange}
            placeholder="e.g. 30"
            min="1"
            required
          />
        </div>

        <div className="form-field full-width">
          <label htmlFor="urgency">Procurement Urgency</label>

          <select
            id="urgency"
            name="urgency"
            value={form.urgency}
            onChange={handleChange}
            required
          >
            <option value="">Select urgency</option>
            <option value="low">Low — Flexible procurement</option>
            <option value="medium">Medium — Normal procurement</option>
            <option value="high">High — Time sensitive</option>
          </select>
        </div>

      </div>

      <div className="submit-area">
        <button className="submit-button" type="submit">
          Run Freight Scenario →
        </button>
      </div>
    </form>
  );
}

export default ScenarioInputs;