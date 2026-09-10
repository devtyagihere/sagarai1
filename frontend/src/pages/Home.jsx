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
  return (
    <div className="home-page">
      {/* HERO */}
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

      {/* MAIN INPUT CARD */}
      <section className="shipment-card">
        <div className="shipment-card-header">
          <div>
            <p className="section-label">SHIPMENT DETAILS</p>

            <h2>Tell us about your voyage</h2>

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
              <label>Origin port</label>

              <div className="input-wrapper">
                <input
                  type="text"
                  placeholder="e.g. Newcastle"
                />
              </div>
            </div>

            <div className="route-arrow">
              <ArrowRight size={20} />
            </div>

            <div className="input-group">
              <label>Destination port</label>

              <div className="input-wrapper">
                <input
                  type="text"
                  placeholder="e.g. Paradip"
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
              <label>Cargo type</label>

              <div className="select-wrapper">
                <select defaultValue="">
                  <option value="" disabled>
                    Select cargo
                  </option>

                  <option>Coal</option>
                  <option>Iron Ore</option>
                  <option>Grain</option>
                  <option>Steel</option>
                  <option>Other Bulk Cargo</option>
                </select>

                <ChevronDown size={16} />
              </div>
            </div>

            <div className="input-group">
              <label>Cargo quantity</label>

              <div className="quantity-wrapper">
                <input
                  type="number"
                  placeholder="50,000"
                />

                <span>MT</span>
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
              <label>Required delivery</label>

              <div className="input-wrapper input-with-icon">
                <CalendarDays size={17} />

                <input
                  type="date"
                />
              </div>
            </div>

            <div className="input-group">
              <label>Contract duration</label>

              <div className="quantity-wrapper">
                <input
                  type="number"
                  placeholder="30"
                />

                <span>days</span>
              </div>
            </div>
          </div>
        </div>

        {/* PRIORITY */}
        <div className="form-section">
          <div className="field-heading">
            <Sparkles size={16} />
            <span>PROCUREMENT PRIORITY</span>
          </div>

          <div className="priority-options">
            <button type="button">
              <strong>Flexible</strong>
              <span>Timing can move</span>
            </button>

            <button
              type="button"
              className="priority-selected"
            >
              <strong>Normal</strong>
              <span>Standard planning</span>
            </button>

            <button type="button">
              <strong>Time-sensitive</strong>
              <span>Need to act soon</span>
            </button>
          </div>
        </div>

        {/* ACTION */}
        <div className="form-action">
          <div className="action-note">
            <span className="action-dot" />

            <span>
              Your inputs stay editable until analysis begins.
            </span>
          </div>

          <button className="analyse-button">
            Analyse Shipment

            <ArrowRight size={18} />
          </button>
        </div>
      </section>

      {/* MARKET SNAPSHOT */}
      <section className="market-section">
        <div className="market-header">
          <div>
            <p className="section-label">MARKET SNAPSHOT</p>

            <h2>A quick look at today's market</h2>
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

            <strong>1,842</strong>

            <p className="positive">
              +5.2% this week
            </p>
          </div>

          <div className="market-card">
            <div className="market-card-top">
              <span>CRUDE OIL</span>
            </div>

            <strong>$78.20</strong>

            <p>USD / barrel</p>
          </div>

          <div className="market-card">
            <div className="market-card-top">
              <span>COAL</span>
            </div>

            <strong>$118.50</strong>

            <p>USD / MT</p>
          </div>

          <div className="market-card">
            <div className="market-card-top">
              <span>PORT ACTIVITY</span>
            </div>

            <strong className="market-status">
              Moderate
            </strong>

            <p>Across monitored ports</p>
          </div>
        </div>
      </section>

      {/* PRODUCT INFO */}
      <section className="home-info">
        <div className="info-intro">
          <p className="section-label">WHAT WE LOOK AT</p>

          <h2>
            One shipment.
            <br />
            Multiple signals.
          </h2>
        </div>

        <div className="info-items">
          <div className="info-item">
            <span>01</span>

            <div>
              <strong>Freight market</strong>

              <p>
                Historical rates and forecast trends
                help identify where freight may be heading.
              </p>
            </div>
          </div>

          <div className="info-item">
            <span>02</span>

            <div>
              <strong>Vessel economics</strong>

              <p>
                Compare vessel classes and understand
                the economics behind each option.
              </p>
            </div>
          </div>

          <div className="info-item">
            <span>03</span>

            <div>
              <strong>Operational risk</strong>

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