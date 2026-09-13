import { useState } from "react";
import {
  Anchor,
  ArrowRight,
  CircleAlert,
  Clock3,
  CloudRain,
  MapPin,
  Ship,
  TrendingUp,
  SlidersHorizontal,
  Sparkles,
  DollarSign,
} from "lucide-react";
import { useNavigate } from "react-router-dom";
import { getShipment, getAnalysisResult } from "../services/shipmentStorage";

export default function PortIntelligence() {
  const navigate = useNavigate();
  const shipment = getShipment();
  const analysis = getAnalysisResult();

  if (!shipment) {
    return (
      <div className="port-page">
        <section className="port-header">
          <div>
            <p className="section-label">PORT INTELLIGENCE</p>

            <h1>No shipment selected.</h1>

            <p>
              Start by entering your shipment details so port conditions can
              be evaluated for your voyage.
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
  } = shipment;

  const portOps = analysis?.port_operations;
  const originOps = portOps?.origin || portOps?.origin_port;
  const destOps = portOps?.destination || portOps?.destination_port;

  return (
    <div className="port-page">

      {/* HEADER */}

      <section className="port-header">
        <div>
          <p className="section-label">PORT INTELLIGENCE</p>

          <h1>Know what is happening at the ports.</h1>

          <p>
            Review real-time port activity, congestion queues, and turnaround conditions.
          </p>
        </div>

        <div className="port-header-status">
          <Anchor size={17} />
          <span>Port operations workspace</span>
        </div>
      </section>


      {/* ROUTE */}

      <section className="port-route-card">

        <div className="port-route-heading">
          <div>
            <p className="section-label">VOYAGE PORTS</p>

            <h2>
              {origin} → {destination}
            </h2>

            <p>
              Origin and destination operational overview
            </p>
          </div>

          <div className="route-status">
            <span className="route-status-dot" />
            Monitoring
          </div>
        </div>


        <div className="port-route">

          <div className="port-location">

            <div className="port-location-icon">
              <MapPin size={20} />
            </div>

            <div>
              <span>ORIGIN</span>
              <strong>{origin}</strong>
              <small>Loading port</small>
            </div>

          </div>


          <div className="port-route-line">
            <div />
            <Ship size={20} />
            <div />
          </div>


          <div className="port-location destination">

            <div className="port-location-icon">
              <MapPin size={20} />
            </div>

            <div>
              <span>DESTINATION</span>
              <strong>{destination}</strong>
              <small>Discharge port</small>
            </div>

          </div>

        </div>


        <div className="port-shipment-context">

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

        </div>

      </section>


      {/* PORT STATUS */}

      <section className="port-section">

        <div className="port-section-heading">

          <div>
            <p className="section-label">
              OPERATIONAL STATUS
            </p>

            <h2>How the ports are performing</h2>

            <p>
              Current operational indicators that may influence voyage
              timing and cost.
            </p>
          </div>

        </div>


        <div className="port-status-grid">

          {/* ORIGIN */}

          <div className="port-status-card">

            <div className="port-status-top">

              <div className="port-card-icon">
                <Anchor size={19} />
              </div>

              <span className={originOps?.congestion_level === "LOW" ? "status-good" : "status-warning"}>
                {originOps?.congestion_level || "Normal"}
              </span>

            </div>

            <span>{origin.toUpperCase()}</span>

            <h3>{originOps?.congestion_level === "LOW" ? "Operationally stable" : `${originOps?.congestion_level || "Normal"} congestion`}</h3>

            <p>
              {originOps?.vessels_waiting != null ? `${originOps.vessels_waiting} vessels waiting, ${originOps.vessels_working} working.` : "Current activity does not indicate significant loading disruption."}
            </p>

            <div className="port-mini-metrics">

              <div>
                <span>WAIT TIME</span>
                <strong>{originOps?.average_waiting_days != null ? `${originOps.average_waiting_days.toFixed(1)} days` : "1.8 hrs"}</strong>
              </div>

              <div>
                <span>CONGESTION</span>
                <strong>{originOps?.congestion_score != null ? `${originOps.congestion_score.toFixed(0)}/100` : "Moderate"}</strong>
              </div>

            </div>

          </div>


          {/* DESTINATION */}

          <div className="port-status-card">

            <div className="port-status-top">

              <div className="port-card-icon">
                <Anchor size={19} />
              </div>

              <span className={destOps?.congestion_level === "LOW" ? "status-good" : "status-warning"}>
                {destOps?.congestion_level || "Watch"}
              </span>

            </div>

            <span>{destination.toUpperCase()}</span>

            <h3>{destOps?.congestion_level === "LOW" ? "Operationally stable" : `${destOps?.congestion_level || "Moderate"} congestion`}</h3>

            <p>
              {destOps?.vessels_waiting != null ? `${destOps.vessels_waiting} vessels waiting, ${destOps.vessels_working} working.` : "Increased vessel activity may result in longer turnaround times."}
            </p>

            <div className="port-mini-metrics">

              <div>
                <span>WAIT TIME</span>
                <strong>{destOps?.average_waiting_days != null ? `${destOps.average_waiting_days.toFixed(1)} days` : "5.2 hrs"}</strong>
              </div>

              <div>
                <span>CONGESTION</span>
                <strong>{destOps?.congestion_score != null ? `${destOps.congestion_score.toFixed(0)}/100` : "High"}</strong>
              </div>

            </div>

          </div>

        </div>

        {/* Dynamic Port Congestion Forecast Graph */}
        {(originOps || destOps) && (
          <div style={{
            marginTop: '20px',
            background: '#ffffff',
            border: '1px solid #dce4e8',
            borderRadius: '14px',
            padding: '20px 24px',
          }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
              <div>
                <strong style={{ fontSize: '13px', color: '#1e293b', textTransform: 'uppercase', letterSpacing: '0.04em' }}>
                  Port Congestion Progression (0–100 Index)
                </strong>
                <p style={{ margin: '4px 0 0', fontSize: '12px', color: '#64748b' }}>
                  Projected waiting conditions across 7d, 15d and 30d operational horizons
                </p>
              </div>
              <div style={{ display: 'flex', gap: '14px', fontSize: '11px', fontWeight: 600 }}>
                <span style={{ display: 'flex', alignItems: 'center', gap: '6px', color: '#0f766e' }}>
                  <span style={{ width: '10px', height: '10px', borderRadius: '50%', background: '#0f766e' }} />
                  {origin} (Origin)
                </span>
                <span style={{ display: 'flex', alignItems: 'center', gap: '6px', color: '#0284c7' }}>
                  <span style={{ width: '10px', height: '10px', borderRadius: '50%', background: '#0284c7' }} />
                  {destination} (Destination)
                </span>
              </div>
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '12px' }}>
              {[
                {
                  period: 'Current / Now',
                  origVal: originOps?.congestion_score ?? 30,
                  destVal: destOps?.congestion_score ?? 55,
                },
                {
                  period: '+7d Projection',
                  origVal: originOps?.congestion_forecast_7d ?? ((originOps?.congestion_score ?? 30) * 1.02),
                  destVal: destOps?.congestion_forecast_7d ?? ((destOps?.congestion_score ?? 55) * 1.04),
                },
                {
                  period: '+15d Projection',
                  origVal: originOps?.congestion_forecast_15d ?? ((originOps?.congestion_score ?? 30) * 1.04),
                  destVal: destOps?.congestion_forecast_15d ?? ((destOps?.congestion_score ?? 55) * 1.07),
                },
                {
                  period: '+30d Projection',
                  origVal: originOps?.congestion_forecast_30d ?? ((originOps?.congestion_score ?? 30) * 1.05),
                  destVal: destOps?.congestion_forecast_30d ?? ((destOps?.congestion_score ?? 55) * 1.09),
                },
              ].map((slot, idx) => (
                <div key={idx} style={{ background: '#f8fafc', padding: '12px 14px', borderRadius: '8px', border: '1px solid #e2e8f0' }}>
                  <span style={{ fontSize: '11px', color: '#64748b', fontWeight: 600, display: 'block', marginBottom: '8px' }}>
                    {slot.period}
                  </span>

                  <div style={{ marginBottom: '8px' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '11px', marginBottom: '3px' }}>
                      <span style={{ color: '#0f766e', fontWeight: 600 }}>{origin.slice(0, 8)}</span>
                      <span style={{ fontWeight: 700 }}>{Math.round(slot.origVal)}/100</span>
                    </div>
                    <div style={{ height: '6px', background: '#e2e8f0', borderRadius: '3px', overflow: 'hidden' }}>
                      <div style={{ width: `${Math.min(100, slot.origVal)}%`, height: '100%', background: '#0f766e' }} />
                    </div>
                  </div>

                  <div>
                    <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '11px', marginBottom: '3px' }}>
                      <span style={{ color: '#0284c7', fontWeight: 600 }}>{destination.slice(0, 8)}</span>
                      <span style={{ fontWeight: 700 }}>{Math.round(slot.destVal)}/100</span>
                    </div>
                    <div style={{ height: '6px', background: '#e2e8f0', borderRadius: '3px', overflow: 'hidden' }}>
                      <div style={{ width: `${Math.min(100, slot.destVal)}%`, height: '100%', background: '#0284c7' }} />
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

      </section>


      {/* OPERATIONAL INDICATORS */}

      <section className="port-section">

        <div className="port-section-heading">

          <div>
            <p className="section-label">
              PORT INDICATORS
            </p>

            <h2>Signals worth watching</h2>

            <p>
              Operational conditions can change the effective economics
              of a voyage even when freight rates remain unchanged.
            </p>
          </div>

        </div>


        {(() => {
          const avgWaitDays = (((originOps?.average_waiting_days ?? 1.5) + (destOps?.average_waiting_days ?? 2.5)) / 2).toFixed(1);
          const totalWaitVessels = (originOps?.vessels_waiting ?? 0) + (destOps?.vessels_waiting ?? 0);
          const weatherRisk = analysis?.risk_assessment?.weather_risk?.weather_risk_score;

          return (
            <div className="port-indicator-grid">

              <div className="port-indicator">

                <div className="port-indicator-icon">
                  <Clock3 size={19} />
                </div>

                <div>
                  <span>AVERAGE WAIT</span>
                  <strong>{avgWaitDays} days</strong>
                  <p>Across loading & discharge</p>
                </div>

              </div>


              <div className="port-indicator">

                <div className="port-indicator-icon">
                  <Ship size={19} />
                </div>

                <div>
                  <span>VESSEL ACTIVITY</span>
                  <strong>{totalWaitVessels > 10 ? "Elevated" : "Normal"}</strong>
                  <p>{totalWaitVessels} vessels currently waiting</p>
                </div>

              </div>


              <div className="port-indicator">

                <div className="port-indicator-icon">
                  <CloudRain size={19} />
                </div>

                <div>
                  <span>WEATHER IMPACT</span>
                  <strong>{weatherRisk != null ? (weatherRisk > 50 ? "Moderate" : "Low") : "Low"}</strong>
                  <p>Storm risk along corridor</p>
                </div>

              </div>


              <div className="port-indicator">

                <div className="port-indicator-icon">
                  <TrendingUp size={19} />
                </div>

                <div>
                  <span>PORT DELAY RISK</span>
                  <strong>{destOps?.congestion_level || "Moderate"}</strong>
                  <p>{destination} congestion status</p>
                </div>

              </div>

            </div>
          );
        })()}

      </section>


      {/* PORT IMPACT */}
      <section className="page-next-banner">
        <div className="banner-icon">
          <Anchor size={22} />
        </div>

        <div className="banner-content">
          <p className="section-label">
            VOYAGE IMPACT
          </p>

          <h2>
            {destination} deserves closer attention.
          </h2>

          <p>
            Current destination conditions could increase turnaround time.
            The final voyage economics should account for potential waiting
            costs before fixing the vessel.
          </p>
        </div>

        <button
          className="page-cta-button"
          onClick={() => navigate("/risk")}
          type="button"
        >
          <span>Continue to risk center</span>
          <ArrowRight size={18} />
        </button>
      </section>

    </div>
  );
}