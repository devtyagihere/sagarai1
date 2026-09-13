import { useState, useEffect } from "react";
import { ArrowRight, CalendarDays, ChevronDown } from "lucide-react";
import { getShipment } from "../../services/shipmentStorage";

function ScenarioInputs({ onSubmit, onRunScenario }) {
  const currentShipment = getShipment();

  const [form, setForm] = useState({
    origin: currentShipment?.origin || "",
    destination: currentShipment?.destination || "",
    cargoType: currentShipment?.cargo || currentShipment?.cargoType || "Coal",
    quantity: currentShipment?.quantity || "75000",
    deliveryDate: currentShipment?.deliveryDate || new Date(Date.now() + 30 * 86400000).toISOString().split("T")[0],
    contractDuration: currentShipment?.contractDuration || "30",
    urgency: currentShipment?.priority ? currentShipment.priority.toLowerCase() : "medium",
  });

  useEffect(() => {
    if (currentShipment) {
      setForm((prev) => ({
        origin: prev.origin || currentShipment.origin || "",
        destination: prev.destination || currentShipment.destination || "",
        cargoType: prev.cargoType || currentShipment.cargo || currentShipment.cargoType || "Coal",
        quantity: prev.quantity || currentShipment.quantity || "75000",
        deliveryDate: prev.deliveryDate || currentShipment.deliveryDate || "",
        contractDuration: prev.contractDuration || currentShipment.contractDuration || "30",
        urgency: prev.urgency || (currentShipment.priority ? currentShipment.priority.toLowerCase() : "medium"),
      }));
    }
  }, []);

  const handleChange = (event) => {
    const { name, value } = event.target;
    setForm((previousForm) => ({
      ...previousForm,
      [name]: value,
    }));
  };

  const handleSubmit = (event) => {
    event.preventDefault();
    const handler = onRunScenario || onSubmit;
    if (handler) {
      handler(form);
    }
  };

  return (
    <form className="scenario-form" onSubmit={handleSubmit}>
      <div className="form-grid">

        {/* Origin */}
        <div className="input-group">
          <label htmlFor="origin">Origin Port / Country</label>
          <div className="input-wrapper">
            <input
              id="origin"
              name="origin"
              type="text"
              value={form.origin}
              onChange={handleChange}
              placeholder="e.g. Newcastle, Australia"
              required
            />
          </div>
          <span className="form-hint">Where the cargo is procured</span>
        </div>

        {/* Destination */}
        <div className="input-group">
          <label htmlFor="destination">Destination Port</label>
          <div className="input-wrapper">
            <input
              id="destination"
              name="destination"
              type="text"
              value={form.destination}
              onChange={handleChange}
              placeholder="e.g. Rotterdam, Paradip"
              required
            />
          </div>
          <span className="form-hint">Final discharge location</span>
        </div>

        {/* Cargo Type */}
        <div className="input-group">
          <label htmlFor="cargoType">Cargo Type</label>
          <div className="select-wrapper">
            <select
              id="cargoType"
              name="cargoType"
              value={form.cargoType}
              onChange={handleChange}
              required
            >
              <option value="Coal">Coal</option>
              <option value="Iron Ore">Iron Ore</option>
              <option value="Grain">Grain</option>
              <option value="Steel">Steel</option>
              <option value="Other Bulk Cargo">Other Bulk Cargo</option>
            </select>
            <ChevronDown size={16} />
          </div>
          <span className="form-hint">Commodity specification</span>
        </div>

        {/* Cargo Quantity */}
        <div className="input-group">
          <label htmlFor="quantity">Cargo Quantity</label>
          <div className="quantity-wrapper">
            <input
              id="quantity"
              name="quantity"
              type="number"
              value={form.quantity}
              onChange={handleChange}
              placeholder="50,000"
              min="1"
              required
            />
            <span>MT</span>
          </div>
          <span className="form-hint">Total volume in metric tonnes</span>
        </div>

        {/* Required Delivery Date */}
        <div className="input-group">
          <label htmlFor="deliveryDate">Required Delivery Date</label>
          <div className="input-wrapper input-with-icon">
            <CalendarDays size={18} />
            <input
              id="deliveryDate"
              name="deliveryDate"
              type="date"
              min={new Date().toISOString().split("T")[0]}
              value={form.deliveryDate}
              onChange={handleChange}
              required
            />
          </div>
          <span className="form-hint">Laycan window deadline</span>
        </div>

        {/* Contract Duration */}
        <div className="input-group">
          <label htmlFor="contractDuration">Contract Duration</label>
          <div className="quantity-wrapper">
            <input
              id="contractDuration"
              name="contractDuration"
              type="number"
              value={form.contractDuration}
              onChange={handleChange}
              placeholder="30"
              min="1"
              required
            />
            <span>DAYS</span>
          </div>
          <span className="form-hint">Expected voyage charter duration</span>
        </div>

        {/* Procurement Urgency */}
        <div className="input-group full-width" style={{ gridColumn: "1 / -1" }}>
          <label htmlFor="urgency">Procurement Urgency</label>
          <div className="select-wrapper">
            <select
              id="urgency"
              name="urgency"
              value={form.urgency}
              onChange={handleChange}
              required
            >
              <option value="low">Low — Flexible timing, maximize cost savings</option>
              <option value="medium">Medium — Normal procurement timeline</option>
              <option value="high">High — Time sensitive, prompt vessel fixing required</option>
            </select>
            <ChevronDown size={16} />
          </div>
          <span className="form-hint">Prioritization weighting for scenario optimization</span>
        </div>

      </div>

      <div style={{ marginTop: "28px", display: "flex", justifyContent: "flex-end" }}>
        <button className="page-cta-button" type="submit">
          <span>Run Freight Scenario</span>
          <ArrowRight size={18} />
        </button>
      </div>
    </form>
  );
}

export default ScenarioInputs;