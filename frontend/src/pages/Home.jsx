import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";

import { saveShipment } from "../services/shipmentStorage";
import { analyzeShipment, fetchMarketSnapshot, fetchPorts } from "../services/api";

import {
  ArrowRight,
  CalendarDays,
  CheckCircle2,
  ChevronDown,
  CircleAlert,
  MapPin,
  Ship,
  Sparkles,
  TrendingUp,
} from "lucide-react";

const FALLBACK_VERIFIED_PORTS = [
  { port_name: "Paradip", country: "India", max_draft_m: 17.1 },
  { port_name: "Visakhapatnam", country: "India", max_draft_m: 18.1 },
  { port_name: "Gangavaram", country: "India", max_draft_m: 21.0 },
  { port_name: "Gopalpur", country: "India", max_draft_m: 14.5 },
  { port_name: "Dhamra", country: "India", max_draft_m: 18.0 },
  { port_name: "Haldia", country: "India", max_draft_m: 8.5 },
  { port_name: "Sagar-Sandheads", country: "India", max_draft_m: 11.0 },
  { port_name: "Rotterdam", country: "Netherlands", max_draft_m: 24.0 },
  { port_name: "Port Hedland", country: "Australia", max_draft_m: 19.5 },
  { port_name: "Hay Point", country: "Australia", max_draft_m: 19.0 },
  { port_name: "Newcastle", country: "Australia", max_draft_m: 15.2 },
  { port_name: "Richards Bay", country: "South Africa", max_draft_m: 17.5 },
  { port_name: "Maputo", country: "Mozambique", max_draft_m: 14.2 },
  { port_name: "Tanjung Bara", country: "Indonesia", max_draft_m: 16.0 },
  { port_name: "Samarinda", country: "Indonesia", max_draft_m: 11.5 },
  { port_name: "Ust-Luga", country: "Russia", max_draft_m: 16.5 },
  { port_name: "Vostochny", country: "Russia", max_draft_m: 17.5 },
  { port_name: "Baltimore", country: "United States", max_draft_m: 15.2 },
  { port_name: "Norfolk", country: "United States", max_draft_m: 16.8 },
  { port_name: "Singapore", country: "Singapore", max_draft_m: 20.0 },
  { port_name: "Shanghai", country: "China", max_draft_m: 15.5 },
  { port_name: "Qingdao", country: "China", max_draft_m: 21.0 },
];

const PRESET_ROUTES = [
  {
    orig: "Newcastle",
    dest: "Rotterdam",
    cargo: "Coal",
    qty: "75000",
    days: "35",
    tagColor: "blue",
  },
  {
    orig: "Port Hedland",
    dest: "Qingdao",
    cargo: "Iron Ore",
    qty: "120000",
    days: "25",
    tagColor: "amber",
  },
  {
    orig: "Paradip",
    dest: "Singapore",
    cargo: "Iron Ore",
    qty: "65000",
    days: "20",
    tagColor: "teal",
  },
  {
    orig: "Baltimore",
    dest: "Rotterdam",
    cargo: "Grain",
    qty: "55000",
    days: "20",
    tagColor: "green",
  },
  {
    orig: "Samarinda",
    dest: "Gangavaram",
    cargo: "Coal",
    qty: "60000",
    days: "18",
    tagColor: "purple",
  },
  {
    orig: "Richards Bay",
    dest: "Visakhapatnam",
    cargo: "Coal",
    qty: "80000",
    days: "22",
    tagColor: "indigo",
  },
];

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
  const [marketData, setMarketData] = useState(null);
  const [availablePorts, setAvailablePorts] = useState(FALLBACK_VERIFIED_PORTS);

  useEffect(() => {
    fetchMarketSnapshot("coal").then((data) => {
      if (data) setMarketData(data);
    });
    fetchPorts().then((ports) => {
      if (ports && ports.length > 0) {
        const verified = ports.filter(p => p.data_status === "verified" || !p.port_name.startsWith("Port_"));
        setAvailablePorts(verified.length > 0 ? verified : ports);
      }
    });
  }, []);

  const updateField = (field, value) => {
    setFormData((previous) => ({
      ...previous,
      [field]: value,
    }));
  };

  const findPortInfo = (portName) => {
    if (!portName || !portName.trim()) return null;
    const clean = portName.trim().toLowerCase();
    return availablePorts.find(p => p.port_name.toLowerCase() === clean) || null;
  };

  const originInfo = findPortInfo(formData.origin);
  const destInfo = findPortInfo(formData.destination);

  const handleAnalyse = async () => {
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

    // Strict verified port validation
    if (!originInfo) {
      setAnalysisError(
        `Origin port '${formData.origin}' is unavailable. It is not in the verified maritime ports database. Please select a registered port (e.g. Newcastle, Paradip, Rotterdam, Singapore).`
      );
      return;
    }

    if (!destInfo) {
      setAnalysisError(
        `Destination port '${formData.destination}' is unavailable. It is not in the verified maritime ports database. Please select a registered port (e.g. Paradip, Rotterdam, Qingdao, Singapore).`
      );
      return;
    }

    if (formData.origin.trim().toLowerCase() === formData.destination.trim().toLowerCase()) {
      setAnalysisError("Origin and Destination ports must be different.");
      return;
    }

    setAnalysing(true);

    try {
      await analyzeShipment(formData);
      navigate("/overview");
    } catch (err) {
      setAnalysisError(err.message || "Failed to analyze shipment. Please verify port names and inputs.");
    } finally {
      setAnalysing(false);
    }
  };

  const applyPreset = (presetOrigin, presetDest, presetCargo, presetQty, presetDuration) => {
    const days = Number(presetDuration) || 30;
    const targetDate = new Date(Date.now() + days * 86400000);
    const targetDateStr = targetDate.toISOString().split("T")[0];

    setFormData((prev) => ({
      ...prev,
      origin: presetOrigin,
      destination: presetDest,
      cargo: presetCargo || prev.cargo || "Coal",
      quantity: presetQty || prev.quantity || "75000",
      contractDuration: presetDuration || prev.contractDuration || "30",
      deliveryDate: prev.deliveryDate || targetDateStr,
    }));
    setAnalysisError("");
  };

  return (
    <div className="home-page">

      {/* Datalist for port suggestions */}
      <datalist id="verified-ports-list">
        {availablePorts.map((p) => (
          <option key={p.port_name} value={p.port_name}>
            {p.country} (Max Draft: {p.max_draft_m ? `${p.max_draft_m}m` : "Standard"})
          </option>
        ))}
      </datalist>

      {/* =========================================
          HERO
      ========================================= */}

      <section className="home-hero">

        <div className="hero-copy">

          <div className="hero-kicker">
            <span className="kicker-line" />
            SAGARAI FREIGHT INTELLIGENCE
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
              Select verified loading and discharge ports from the maritime database.
            </p>
          </div>

          <div className="shipment-icon">
            <Ship size={22} strokeWidth={1.7} />
          </div>

        </div>

        {/* Quick Port Presets Section */}
        <div className="route-presets-container">
          <div className="route-presets-header">
            <div className="route-presets-title">
              <Sparkles size={15} className="route-presets-icon" />
              <span>Popular Verified Trade Routes</span>
            </div>
            <span className="route-presets-badge">1-Click Auto-Fill</span>
          </div>

          <div className="route-presets-grid">
            {PRESET_ROUTES.map((preset, idx) => {
              const isSelected =
                formData.origin.toLowerCase() === preset.orig.toLowerCase() &&
                formData.destination.toLowerCase() === preset.dest.toLowerCase();

              return (
                <button
                  key={idx}
                  type="button"
                  className={`route-preset-card ${isSelected ? "selected" : ""}`}
                  onClick={() =>
                    applyPreset(
                      preset.orig,
                      preset.dest,
                      preset.cargo,
                      preset.qty,
                      preset.days
                    )
                  }
                >
                  <div className="route-preset-main">
                    <div className="route-preset-ports">
                      <span className="preset-port origin">{preset.orig}</span>
                      <ArrowRight size={13} className="preset-arrow" />
                      <span className="preset-port dest">{preset.dest}</span>
                    </div>
                    {isSelected && (
                      <CheckCircle2 size={15} className="preset-selected-check" />
                    )}
                  </div>

                  <div className="route-preset-details">
                    <span className={`preset-cargo-badge ${preset.tagColor}`}>
                      {preset.cargo}
                    </span>
                    <span className="preset-meta">
                      {Number(preset.qty).toLocaleString()} MT • ~{preset.days}d
                    </span>
                  </div>
                </button>
              );
            })}
          </div>
        </div>

        {/* ROUTE */}

        <div className="route-section">

          <div className="field-heading">
            <MapPin size={16} />
            <span>ROUTE (VERIFIED MARITIME PORTS ONLY)</span>
          </div>


          <div className="route-fields">

            <div className="input-group">

              <label>
                Origin port (Loading terminal)
              </label>

              <div className="input-wrapper">

                <input
                  type="text"
                  list="verified-ports-list"
                  placeholder="e.g. Newcastle, Paradip, Rotterdam"
                  value={formData.origin}
                  onChange={(event) =>
                    updateField("origin", event.target.value)
                  }
                  style={{
                    borderColor: formData.origin && !originInfo ? '#ef4444' : undefined,
                  }}
                />

              </div>

              {/* Live Port Validation Status */}
              {formData.origin.trim() && (
                <div style={{ marginTop: '7px', fontSize: '13px', display: 'flex', alignItems: 'center', gap: '6px' }}>
                  {originInfo ? (
                    <span style={{ color: '#15803d', display: 'flex', alignItems: 'center', gap: '5px', fontWeight: 600 }}>
                      <CheckCircle2 size={15} />
                      Verified: {originInfo.port_name} ({originInfo.country}) — Max Draft {originInfo.max_draft_m}m
                    </span>
                  ) : (
                    <span style={{ color: '#b91c1c', display: 'flex', alignItems: 'center', gap: '5px', fontWeight: 600 }}>
                      <CircleAlert size={15} />
                      Unavailable: &apos;{formData.origin}&apos; is not a registered port. Please pick from database.
                    </span>
                  )}
                </div>
              )}

            </div>


            <div className="route-arrow">
              <ArrowRight size={20} />
            </div>


            <div className="input-group">

              <label>
                Destination port (Discharge terminal)
              </label>

              <div className="input-wrapper">

                <input
                  type="text"
                  list="verified-ports-list"
                  placeholder="e.g. Rotterdam, Qingdao, Singapore"
                  value={formData.destination}
                  onChange={(event) =>
                    updateField("destination", event.target.value)
                  }
                  style={{
                    borderColor: formData.destination && !destInfo ? '#ef4444' : undefined,
                  }}
                />

              </div>

              {/* Live Port Validation Status */}
              {formData.destination.trim() && (
                <div style={{ marginTop: '7px', fontSize: '13px', display: 'flex', alignItems: 'center', gap: '6px' }}>
                  {destInfo ? (
                    <span style={{ color: '#15803d', display: 'flex', alignItems: 'center', gap: '5px', fontWeight: 600 }}>
                      <CheckCircle2 size={15} />
                      Verified: {destInfo.port_name} ({destInfo.country}) — Max Draft {destInfo.max_draft_m}m
                    </span>
                  ) : (
                    <span style={{ color: '#b91c1c', display: 'flex', alignItems: 'center', gap: '5px', fontWeight: 600 }}>
                      <CircleAlert size={15} />
                      Unavailable: &apos;{formData.destination}&apos; is not a registered port. Please pick from database.
                    </span>
                  )}
                </div>
              )}

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
                  min={new Date().toISOString().split("T")[0]}
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
              {marketData?.bdi ? Number(marketData.bdi).toLocaleString() : "1,500"}
            </strong>

            <p className="positive">
              {marketData?.data_source ? `Source: ${marketData.data_source}` : "+5.2% this week"}
            </p>

          </div>


          <div className="market-card">

            <div className="market-card-top">
              <span>CRUDE OIL</span>
            </div>

            <strong>
              {marketData?.wti_oil_usd_bbl ? `$${marketData.wti_oil_usd_bbl.toFixed(2)}` : "$80.00"}
            </strong>

            <p>
              USD / barrel
            </p>

          </div>


          <div className="market-card">

            <div className="market-card-top">
              <span>COAL SPOT</span>
            </div>

            <strong>
              {marketData?.commodity_price_usd_t ? `$${marketData.commodity_price_usd_t.toFixed(2)}` : "$118.50"}
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