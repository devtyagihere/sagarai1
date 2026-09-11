import { useState } from "react";
import { useNavigate } from "react-router-dom";

import { saveShipment } from "../services/shipmentStorage";

import {
  ArrowRight,
  CalendarDays,
  ChevronDown,
  MapPin,
  Ship,
  Sparkles,
  TrendingUp,
} from "lucide-react";

export default function Home() {
  const navigate = useNavigate();

  const [formData, setFormData] = useState({
    origin: "",
    destination: "",
    cargo: "",
    quantity: "",
    deliveryDate: "",
    contractDuration: "",
    priority: "Normal",
  });

  const [analysing, setAnalysing] = useState(false);
  const [analysisError, setAnalysisError] = useState("");

  const updateField = (field, value) => {
    setFormData((previous) => ({
      ...previous,
      [field]: value,
    }));
  };

  const handleAnalyse = () => {
    setAnalysisError("");

    // Basic frontend validation
    if (
      !formData.origin.trim() ||
      !formData.destination.trim() ||
      !formData.cargo ||
      !formData.quantity ||
      !formData.deliveryDate ||
      !formData.contractDuration
    ) {
      setAnalysisError(
        "Please complete all shipment details before continuing."
      );
      return;
    }

    setAnalysing(true);

    // Save the user's actual shipment for the rest of the frontend.
    saveShipment(formData);

    // Move into the decision-support flow.
    navigate("/overview");

    setAnalysing(false);
  };

  return (
    <div className="home-page">

      {/* =========================================
          HERO
      ========================================= */}

      <section className="home-hero">

        <div className="hero-copy">

          <div className="hero-kicker">
            <span className="kicker-line" />
            MARITIME FREIGHT INTELLIGENCE
          </div>

          <h1>
            Plan your next
            <span> shipment.</span>
          </h1>

          <p>
            Understand the market, compare vessel economics,
            and make a smarter chartering decision before you commit.
          </p>

        </div>


        <div className="hero-status">
          <span className="status-pulse" />
          Decision engine ready
        </div>

      </section>


      {/* =========================================
          SHIPMENT INPUT CARD
      ========================================= */}

      <section className="shipment-card">

        <div className="shipment-card-header">

          <div>
            <p className="section-label">
              SHIPMENT DETAILS
            </p>

            <h2>
              Tell us about your voyage
            </h2>

            <p className="section-description">
              Enter the basic details of the shipment you are planning.
            </p>
          </div>

          <div className="shipment-icon">
            <Ship size={22} strokeWidth={1.7} />
          </div>

        </div>


        {/* ROUTE */}

        <div className="route-section">

          <div className="field-heading">
            <MapPin size={16} />
            <span>ROUTE</span>
          </div>


          <div className="route-fields">

            <div className="input-group">

              <label>
                Origin port
              </label>

              <div className="input-wrapper">

                <input
                  type="text"
                  placeholder="e.g. Newcastle"
                  value={formData.origin}
                  onChange={(event) =>
                    updateField("origin", event.target.value)
                  }
                />

              </div>

            </div>


            <div className="route-arrow">
              <ArrowRight size={20} />
            </div>


            <div className="input-group">

              <label>
                Destination port
              </label>

              <div className="input-wrapper">

                <input
                  type="text"
                  placeholder="e.g. Paradip"
                  value={formData.destination}
                  onChange={(event) =>
                    updateField("destination", event.target.value)
                  }
                />

              </div>

            </div>

          </div>

        </div>


        {/* CARGO */}

        <div className="form-section">

          <div className="field-heading">
            <Ship size={16} />
            <span>CARGO</span>
          </div>


          <div className="form-grid">

            <div className="input-group">

              <label>
                Cargo type
              </label>

              <div className="select-wrapper">

                <select
                  value={formData.cargo}
                  onChange={(event) =>
                    updateField("cargo", event.target.value)
                  }
                >
                  <option value="" disabled>
                    Select cargo
                  </option>

                  <option value="Coal">
                    Coal
                  </option>

                  <option value="Iron Ore">
                    Iron Ore
                  </option>

                  <option value="Grain">
                    Grain
                  </option>

                  <option value="Steel">
                    Steel
                  </option>

                  <option value="Other Bulk Cargo">
                    Other Bulk Cargo
                  </option>

                </select>

                <ChevronDown size={16} />

              </div>

            </div>


            <div className="input-group">

              <label>
                Cargo quantity
              </label>

              <div className="quantity-wrapper">

                <input
                  type="number"
                  placeholder="50,000"
                  min="1"
                  value={formData.quantity}
                  onChange={(event) =>
                    updateField("quantity", event.target.value)
                  }
                />

                <span>
                  MT
                </span>

              </div>

            </div>

          </div>

        </div>


        {/* TIMING */}

        <div className="form-section">

          <div className="field-heading">
            <CalendarDays size={16} />
            <span>TIMING</span>
          </div>


          <div className="form-grid">

            <div className="input-group">

              <label>
                Required delivery
              </label>

              <div className="input-wrapper input-with-icon">

                <CalendarDays size={17} />

                <input
                  type="date"
                  value={formData.deliveryDate}
                  onChange={(event) =>
                    updateField(
                      "deliveryDate",
                      event.target.value
                    )
                  }
                />

              </div>

            </div>


            <div className="input-group">

              <label>
                Contract duration
              </label>

              <div className="quantity-wrapper">

                <input
                  type="number"
                  placeholder="30"
                  min="1"
                  value={formData.contractDuration}
                  onChange={(event) =>
                    updateField(
                      "contractDuration",
                      event.target.value
                    )
                  }
                />

                <span>
                  days
                </span>

              </div>

            </div>

          </div>

        </div>


        {/* PROCUREMENT PRIORITY */}

        <div className="form-section">

          <div className="field-heading">
            <Sparkles size={16} />
            <span>PROCUREMENT PRIORITY</span>
          </div>


          <div className="priority-options">

            <button
              type="button"
              className={
                formData.priority === "Flexible"
                  ? "priority-selected"
                  : ""
              }
              onClick={() =>
                updateField("priority", "Flexible")
              }
            >
              <strong>
                Flexible
              </strong>

              <span>
                Timing can move
              </span>
            </button>


            <button
              type="button"
              className={
                formData.priority === "Normal"
                  ? "priority-selected"
                  : ""
              }
              onClick={() =>
                updateField("priority", "Normal")
              }
            >
              <strong>
                Normal
              </strong>

              <span>
                Standard planning
              </span>
            </button>


            <button
              type="button"
              className={
                formData.priority === "Time-sensitive"
                  ? "priority-selected"
                  : ""
              }
              onClick={() =>
                updateField("priority", "Time-sensitive")
              }
            >
              <strong>
                Time-sensitive
              </strong>

              <span>
                Need to act soon
              </span>
            </button>

          </div>

        </div>


        {/* ACTION */}

        <div className="form-action">

          <div className="action-note">

            <span className="action-dot" />

            <span>
              Your shipment details will be used throughout the planning workspace.
            </span>

          </div>


          {analysisError && (
            <div className="analysis-error">
              {analysisError}
            </div>
          )}


          <button
            type="button"
            className="analyse-button"
            disabled={analysing}
            onClick={handleAnalyse}
          >
            {analysing
              ? "Opening workspace..."
              : "Analyse Shipment"}

            <ArrowRight size={18} />
          </button>

        </div>

      </section>


      {/* =========================================
          MARKET SNAPSHOT
      ========================================= */}

      <section className="market-section">

        <div className="market-header">

          <div>

            <p className="section-label">
              MARKET SNAPSHOT
            </p>

            <h2>
              A quick look at today's market
            </h2>

          </div>


          <div className="market-live">
            <span />
            Market data
          </div>

        </div>


        <div className="market-grid">

          <div className="market-card">

            <div className="market-card-top">
              <span>BDI</span>
              <TrendingUp size={17} />
            </div>

            <strong>
              1,842
            </strong>

            <p className="positive">
              +5.2% this week
            </p>

          </div>


          <div className="market-card">

            <div className="market-card-top">
              <span>CRUDE OIL</span>
            </div>

            <strong>
              $78.20
            </strong>

            <p>
              USD / barrel
            </p>

          </div>


          <div className="market-card">

            <div className="market-card-top">
              <span>COAL</span>
            </div>

            <strong>
              $118.50
            </strong>

            <p>
              USD / MT
            </p>

          </div>


          <div className="market-card">

            <div className="market-card-top">
              <span>PORT ACTIVITY</span>
            </div>

            <strong className="market-status">
              Moderate
            </strong>

            <p>
              Across monitored ports
            </p>

          </div>

        </div>

      </section>


      {/* =========================================
          PRODUCT INFORMATION
      ========================================= */}

      <section className="home-info">

        <div className="info-intro">

          <p className="section-label">
            WHAT WE LOOK AT
          </p>

          <h2>
            One shipment.
            <br />
            Multiple signals.
          </h2>

        </div>


        <div className="info-items">

          <div className="info-item">

            <span>
              01
            </span>

            <div>

              <strong>
                Freight market
              </strong>

              <p>
                Historical rates and forecast trends
                help identify where freight may be heading.
              </p>

            </div>

          </div>


          <div className="info-item">

            <span>
              02
            </span>

            <div>

              <strong>
                Vessel economics
              </strong>

              <p>
                Compare vessel classes and understand
                the economics behind each option.
              </p>

            </div>

          </div>


          <div className="info-item">

            <span>
              03
            </span>

            <div>

              <strong>
                Operational risk
              </strong>

              <p>
                Port conditions, weather and marine
                signals are considered before a decision.
              </p>

            </div>

          </div>

        </div>

      </section>

    </div>
  );
}