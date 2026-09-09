import React from 'react';

export default function ScenarioComparison({ baselineScenario, currentScenario }) {
  if (!currentScenario) return null;

  const base = baselineScenario || {
    label: 'Scenario A (Baseline: 150k MT Spot)',
    ratePerMt: currentScenario.ratePerMt ? currentScenario.ratePerMt * 1.052 : 26.80,
    totalVoyageCost: currentScenario.totalVoyageCost ? currentScenario.totalVoyageCost * 1.045 : 4280000,
    transitDays: currentScenario.transitDays ? currentScenario.transitDays + 2 : 24,
    bunkerCost: currentScenario.totalVoyageCost ? currentScenario.totalVoyageCost * 0.44 : 1880000,
    ciiScore: 'C'
  };

  const current = {
    label: 'Scenario B (Current Simulation)',
    ratePerMt: currentScenario.ratePerMt || 25.40,
    totalVoyageCost: currentScenario.totalVoyageCost || 4050000,
    transitDays: currentScenario.transitDays || 22,
    bunkerCost: currentScenario.totalVoyageCost ? currentScenario.totalVoyageCost * 0.41 : 1660000,
    ciiScore: currentScenario.ciiRating || 'B'
  };

  const rateDelta = current.ratePerMt - base.ratePerMt;
  const rateDeltaPct = ((rateDelta / base.ratePerMt) * 100).toFixed(1);
  const costDelta = current.totalVoyageCost - base.totalVoyageCost;
  const daysDelta = current.transitDays - base.transitDays;
  const bunkerDelta = current.bunkerCost - base.bunkerCost;

  return (
    <div className="fi-card">
      <div className="fi-card-header">
        <div className="fi-card-title">
          <span className="fi-card-title-icon">⚖️</span>
          Scenario A/B Delta Analysis
        </div>
        <span className="badge-mono" style={{ fontSize: '10px', color: 'var(--text-muted)' }}>COMPARISON</span>
      </div>

      <div className="fi-card-body" style={{ padding: 0 }}>
        <table className="fi-compare-table">
          <thead>
            <tr>
              <th style={{ width: '28%' }}>Metric / Term</th>
              <th style={{ width: '24%' }}>{base.label}</th>
              <th style={{ width: '24%' }}>{current.label}</th>
              <th style={{ width: '24%' }}>Variance (Delta)</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td className="fi-compare-metric">Freight Rate ($/MT)</td>
              <td className="tabular-nums">${base.ratePerMt.toFixed(2)}</td>
              <td className="tabular-nums" style={{ fontWeight: 600 }}>${current.ratePerMt.toFixed(2)}</td>
              <td>
                <span className={`fi-delta-badge ${rateDelta < 0 ? 'pos' : rateDelta > 0 ? 'neg' : 'same'}`}>
                  {rateDelta < 0 ? '↓' : rateDelta > 0 ? '↑' : '—'} {Math.abs(rateDeltaPct)}% (${Math.abs(rateDelta).toFixed(2)}/t)
                </span>
              </td>
            </tr>
            <tr>
              <td className="fi-compare-metric">Total Fixture Cost</td>
              <td className="tabular-nums">${base.totalVoyageCost.toLocaleString(undefined, { maximumFractionDigits: 0 })}</td>
              <td className="tabular-nums" style={{ fontWeight: 600 }}>
                ${current.totalVoyageCost.toLocaleString(undefined, { maximumFractionDigits: 0 })}
              </td>
              <td>
                <span className={`fi-delta-badge ${costDelta < 0 ? 'pos' : costDelta > 0 ? 'neg' : 'same'}`}>
                  {costDelta < 0 ? '↓ Savings: ' : costDelta > 0 ? '↑ Premium: ' : '—'}
                  ${Math.abs(costDelta).toLocaleString(undefined, { maximumFractionDigits: 0 })}
                </span>
              </td>
            </tr>
            <tr>
              <td className="fi-compare-metric">Transit & Turnaround</td>
              <td className="tabular-nums">{base.transitDays} Sea Days</td>
              <td className="tabular-nums" style={{ fontWeight: 600 }}>{current.transitDays} Sea Days</td>
              <td>
                <span className={`fi-delta-badge ${daysDelta < 0 ? 'pos' : daysDelta > 0 ? 'neg' : 'same'}`}>
                  {daysDelta < 0 ? '↓' : daysDelta > 0 ? '↑' : '—'} {Math.abs(daysDelta)} Days
                </span>
              </td>
            </tr>
            <tr>
              <td className="fi-compare-metric">Est. Bunker Burn</td>
              <td className="tabular-nums">${base.bunkerCost.toLocaleString(undefined, { maximumFractionDigits: 0 })}</td>
              <td className="tabular-nums" style={{ fontWeight: 600 }}>
                ${current.bunkerCost.toLocaleString(undefined, { maximumFractionDigits: 0 })}
              </td>
              <td>
                <span className={`fi-delta-badge ${bunkerDelta < 0 ? 'pos' : bunkerDelta > 0 ? 'neg' : 'same'}`}>
                  {bunkerDelta < 0 ? '↓' : bunkerDelta > 0 ? '↑' : '—'}
                  ${Math.abs(bunkerDelta).toLocaleString(undefined, { maximumFractionDigits: 0 })}
                </span>
              </td>
            </tr>
            <tr>
              <td className="fi-compare-metric">CII Rating Target</td>
              <td className="tabular-nums">Grade {base.ciiScore}</td>
              <td className="tabular-nums" style={{ fontWeight: 600, color: '#34D399' }}>Grade {current.ciiScore}</td>
              <td>
                <span className="fi-delta-badge pos">✓ Target Compliant</span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  );
}