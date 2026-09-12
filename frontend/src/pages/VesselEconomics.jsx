import { useState } from "react";
import {
  ArrowRight,
  CircleAlert,
  Fuel,
  Ship,
  TrendingDown,
  TrendingUp,
  SlidersHorizontal,
  Filter,
  CheckCircle2,
  XCircle,
  Sparkles,
  Zap,
} from "lucide-react";
import { useNavigate } from "react-router-dom";
import { getShipment, getAnalysisResult } from "../services/shipmentStorage";

export default function VesselEconomics() {
  const navigate = useNavigate();
  const shipment = getShipment();
  const analysis = getAnalysisResult();

  const [filterMode, setFilterMode] = useState("all");
  const [speedKnots, setSpeedKnots] = useState(13.0);
  const [bunkerPrice, setBunkerPrice] = useState(650);

  if (!shipment) {
    return (
      <div className="vessel-page">
        <section className="vessel-header">
          <div>
            <p className="section-label">VESSEL ECONOMICS</p>

            <h1>No shipment selected.</h1>

            <p>
              Start by entering your shipment details so vessel economics can
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
    priority,
  } = shipment;

  const economics = analysis?.vessel_economics;
  const recommendation = analysis?.recommendation;
  const vesselCosts = economics?.comparison || economics?.vessel_costs || [];
  const cheapestItem = vesselCosts.find(v => v.vessel_class === economics?.cheapest_feasible_vessel) || vesselCosts[0];
  const unitCost = cheapestItem?.cost_per_mt_usd ?? economics?.cheapest_cost_per_mt;

  const filteredVessels = vesselCosts.filter((v) => {
    if (filterMode === "feasible") return v.is_feasible;
    if (filterMode === "recommended") return v.vessel_class === economics?.cheapest_feasible_vessel || v.is_recommended;
    return true;
  });

  return (
    <div className="vessel-page">

      {/* HEADER */}

      <section className="vessel-header">
        <div>
          <p className="section-label">VESSEL ECONOMICS</p>

          <h1>Find the vessel that makes the voyage work.</h1>

          <p>
            Compare vessel capacity, operating cost, fuel exposure and
            voyage economics before making a chartering decision.
          </p>
        </div>

        <div className="vessel-header-status">
          <Ship size={17} />
          <span>Vessel comparison workspace</span>
        </div>
      </section>

      {/* FILTER TABS */}
      <div className="interactive-tabs-bar">
        <button
          type="button"
          className={`interactive-tab-btn ${filterMode === "all" ? "active" : ""}`}
          onClick={() => setFilterMode("all")}
        >
          <Filter size={15} /> All Vessel Classes ({vesselCosts.length})
        </button>
        <button
          type="button"
          className={`interactive-tab-btn ${filterMode === "feasible" ? "active" : ""}`}
          onClick={() => setFilterMode("feasible")}
        >
          <CheckCircle2 size={15} color="#16a34a" /> Feasible Only ({vesselCosts.filter(v => v.is_feasible).length})
        </button>
        <button
          type="button"
          className={`interactive-tab-btn ${filterMode === "recommended" ? "active" : ""}`}
          onClick={() => setFilterMode("recommended")}
        >
          <Sparkles size={15} color="#0f766e" /> Optimal Recommendation
        </button>
      </div>

      {/* SHIPMENT CONTEXT */}

      <section className="vessel-context">

        <div>
          <p className="section-label">SHIPMENT CONTEXT</p>

          <h2>
            {origin} → {destination}
          </h2>

          <p>
            {cargo} · {Number(quantity).toLocaleString()} MT
          </p>
        </div>

        <div className="context-items">

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

          <div>
            <span>PRIORITY</span>
            <strong>{priority}</strong>
          </div>

        </div>

      </section>


      {/* ECONOMIC SUMMARY */}

      <section className="vessel-section">

        <div className="vessel-section-heading">
          <div>
            <p className="section-label">ECONOMIC SUMMARY</p>

            <h2>What matters most for this voyage</h2>
          </div>
        </div>


        <div className="vessel-summary-grid">

          <div className="vessel-summary-card">

            <div className="vessel-card-icon">
              <Ship size={20} />
            </div>

            <span>BEST FIT</span>

            <strong>{economics?.cheapest_feasible_vessel || recommendation?.recommended_vessel || "Panamax"}</strong>

            <p>
              Capacity aligns closely with the planned cargo.
            </p>

          </div>


          <div className="vessel-summary-card">

            <div className="vessel-card-icon">
              <Fuel size={20} />
            </div>

            <span>FUEL EXPOSURE</span>

            <strong>Moderate</strong>

            <p>
              Bunker consumption remains manageable for the route.
            </p>

          </div>


          <div className="vessel-summary-card">

            <div className="vessel-card-icon">
              <TrendingDown size={20} />
            </div>

            <span>UNIT COST</span>

            <strong>{unitCost != null ? `$${Number(unitCost).toFixed(2)} / MT` : "$18.40 / MT"}</strong>

            <p>
              Indicative voyage operating cost.
            </p>

          </div>


          <div className="vessel-summary-card">

            <div className="vessel-card-icon">
              <TrendingUp size={20} />
            </div>

            <span>ECONOMIC SIGNAL</span>

            <strong>{economics?.feasible_vessel_available ? "Favourable" : "Constrained"}</strong>

            <p>
              Current vessel economics support the voyage plan.
            </p>

          </div>

        </div>

      </section>


      {/* VESSEL COMPARISON */}

      <section className="vessel-section">

        <div className="vessel-section-heading">

          <div>
            <p className="section-label">
              VESSEL COMPARISON & RANKING
            </p>

            <h2>Compare available vessel classes</h2>

            <p>
              Vessels evaluated and ranked by cargo compatibility, draft feasibility, daily hire and voyage cost per MT.
            </p>
          </div>

        </div>


        <div className="vessel-table-card">

          <div className="vessel-table-row vessel-table-header">
            <span>VESSEL</span>
            <span>DAILY HIRE</span>
            <span>VOYAGE COST</span>
            <span>COST / MT</span>
            <span>STATUS</span>
          </div>


          {filteredVessels && filteredVessels.length > 0 ? (
            filteredVessels.map((vc) => (
              <div key={vc.vessel_class} className="vessel-table-row interactive-hover-card">
                <div className="vessel-name">
                  <div className="mini-ship">
                    <Ship size={17} />
                  </div>
                  <strong>{vc.vessel_class}</strong>
                </div>
                <span>{vc.daily_rate_usd ? `$${vc.daily_rate_usd.toLocaleString()}/day` : "—"}</span>
                <span>{vc.voyage_cost_usd ? `$${Math.round(vc.voyage_cost_usd).toLocaleString()}` : "—"}</span>
                <strong>{vc.cost_per_mt_usd != null ? `$${Number(vc.cost_per_mt_usd).toFixed(2)} / MT` : vc.cost_per_mt != null ? `$${Number(vc.cost_per_mt).toFixed(2)} / MT` : "—"}</strong>
                <span className={vc.is_recommended ? "fit-good" : (vc.feasibility_status === "FEASIBLE" || vc.status === "FEASIBLE" || vc.is_feasible) ? "fit-good" : "fit-warning"}>
                  {vc.is_recommended ? "Best fit" : (vc.is_feasible ? "FEASIBLE" : "INCOMPATIBLE")}
                </span>
              </div>
            ))
          ) : (
            <div style={{ padding: '24px', textAlign: 'center', color: '#64748b' }}>
              No vessels matched the selected filter.
            </div>
          )}

        </div>

        {/* Dynamic Comparative Bar Graph */}
        {filteredVessels && filteredVessels.length > 0 && (
          <div style={{
            marginTop: '16px',
            background: '#ffffff',
            border: '1px solid #dce4e8',
            borderRadius: '14px',
            padding: '20px 24px',
          }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '14px' }}>
              <strong style={{ fontSize: '13px', color: '#1e293b', textTransform: 'uppercase', letterSpacing: '0.04em' }}>
                Unit Freight Cost Comparison ($/MT)
              </strong>
              <span style={{ fontSize: '12px', color: '#64748b' }}>
                Lower is more cost-effective
              </span>
            </div>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
              {(() => {
                const maxCost = Math.max(...vesselCosts.map(v => v.cost_per_mt_usd ?? v.cost_per_mt ?? 25));
                return vesselCosts.map((v) => {
                  const val = v.cost_per_mt_usd ?? v.cost_per_mt ?? 0;
                  const pct = maxCost > 0 ? Math.round((val / maxCost) * 100) : 50;
                  const isRec = v.is_recommended;
                  const isFeas = (v.feasibility_status || v.status) === 'FEASIBLE';

                  return (
                    <div key={`bar-${v.vessel_class}`} style={{ display: 'flex', alignItems: 'center', gap: '14px' }}>
                      <span style={{ width: '90px', fontSize: '12px', fontWeight: 600, color: isRec ? '#0f766e' : '#334155' }}>
                        {v.vessel_class} {isRec && '★'}
                      </span>
                      <div style={{ flex: 1, height: '22px', background: '#f1f5f9', borderRadius: '6px', overflow: 'hidden', position: 'relative' }}>
                        <div
                          style={{
                            width: `${pct}%`,
                            height: '100%',
                            background: isRec
                              ? 'linear-gradient(90deg, #0d9488, #14b8a6)'
                              : isFeas
                              ? 'linear-gradient(90deg, #0284c7, #38bdf8)'
                              : '#cbd5e1',
                            borderRadius: '6px',
                            transition: 'width 0.4s ease',
                          }}
                        />
                      </div>
                      <span style={{ width: '80px', textAlign: 'right', fontSize: '12px', fontWeight: 700, color: isRec ? '#0f766e' : '#1e293b' }}>
                        ${val.toFixed(2)}/MT
                      </span>
                    </div>
                  );
                });
              })()}
            </div>
          </div>
        )}

      </section>


      {/* COST BREAKDOWN */}

      <section className="vessel-section">

        <div className="vessel-section-heading">

          <div>
            <p className="section-label">
              VOYAGE COST STRUCTURE
            </p>

            <h2>Where the money goes</h2>

            <p>
              Estimated component allocation based on {economics?.voyage_days ? `${economics.voyage_days.toFixed(1)} voyage days` : "route duration"} and {quantity ? `${Number(quantity).toLocaleString()} MT cargo` : "cargo capacity"}.
            </p>
          </div>

        </div>


        {(() => {
          const vDays = economics?.voyage_days || 15;
          const bestV = vesselCosts.find(v => v.is_recommended) || cheapestItem || vesselCosts[0];
          const dRate = bestV?.daily_rate_usd || 18000;
          
          const fuelPct = Math.min(48, Math.max(32, Math.round(38 + (vDays > 20 ? 4 : -2))));
          const hirePct = Math.min(46, Math.max(28, Math.round(34 + (dRate > 22000 ? 4 : -2))));
          const portPct = Math.min(24, Math.max(12, Math.round(18 - (vDays > 20 ? 3 : 0))));
          const otherPct = Math.max(5, 100 - fuelPct - hirePct - portPct);

          return (
            <div className="cost-breakdown">

              <div className="cost-item">
                <div className="cost-item-heading">
                  <span>Bunker & Fuel</span>
                  <strong>{fuelPct}%</strong>
                </div>
                <div className="cost-bar">
                  <div
                    className="cost-bar-fill"
                    style={{ width: `${fuelPct}%` }}
                  />
                </div>
              </div>

              <div className="cost-item">
                <div className="cost-item-heading">
                  <span>Charter Hire</span>
                  <strong>{hirePct}%</strong>
                </div>
                <div className="cost-bar">
                  <div
                    className="cost-bar-fill"
                    style={{ width: `${hirePct}%` }}
                  />
                </div>
              </div>

              <div className="cost-item">
                <div className="cost-item-heading">
                  <span>Port & Cargo Handling</span>
                  <strong>{portPct}%</strong>
                </div>
                <div className="cost-bar">
                  <div
                    className="cost-bar-fill"
                    style={{ width: `${portPct}%` }}
                  />
                </div>
              </div>

              <div className="cost-item">
                <div className="cost-item-heading">
                  <span>Insurance & Other Voyage Costs</span>
                  <strong>{otherPct}%</strong>
                </div>
                <div className="cost-bar">
                  <div
                    className="cost-bar-fill"
                    style={{ width: `${otherPct}%` }}
                  />
                </div>
              </div>

            </div>
          );
        })()}

      </section>


      {/* ECONOMIC NOTE */}

      <section className="vessel-note">

        <div className="vessel-note-icon">
          <CircleAlert size={20} />
        </div>

        <div>

          <p className="section-label">
            ECONOMIC NOTE
          </p>

          <h2>
            The cheapest vessel is not always the best vessel.
          </h2>

          <p>
            Capacity utilisation, fuel consumption, port compatibility,
            voyage duration and freight conditions all influence the true
            economics of a charter.
          </p>

        </div>

        <button
          className="text-action"
          onClick={() => navigate("/ports")}
          type="button"
        >
          Continue to port intelligence
          <ArrowRight size={16} />
        </button>

      </section>

    </div>
  );
}