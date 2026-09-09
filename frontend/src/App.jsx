import React, { useState, useEffect } from 'react';
import './App.css';
import ScenarioInputs from './components/ScenarioInputs';
import ForecastSummary from './components/ForecastSummary';
import CharterRecommendation from './components/CharterRecommendation';
import FreightRateChart from './components/FreightRateChart';
import MarketSignals from './components/MarketSignals';
import ScenarioComparison from './components/ScenarioComparison';

const getDefaultDate = () => {
  const d = new Date();
  d.setDate(d.getDate() + 14);
  return d.toISOString().split('T')[0];
};

export default function App() {
  const [formData, setFormData] = useState({
    originPort: 'SARST',
    destinationPort: 'CNTAO',
    cargoType: 'crude_oil',
    quantityMt: 280000,
    deliveryDate: getDefaultDate(),
    contractDuration: 'spot',
    urgency: 'standard'
  });

  const [loading, setLoading] = useState(false);
  const [toast, setToast] = useState(null);
  const [forecastData, setForecastData] = useState(null);
  const [baselineScenario, setBaselineScenario] = useState(null);
  const [currentTime, setCurrentTime] = useState('');

  // Live UTC Clock
  useEffect(() => {
    const updateClock = () => {
      const now = new Date();
      setCurrentTime(now.toUTCString().slice(17, 25) + ' UTC');
    };
    updateClock();
    const timer = setInterval(updateClock, 1000);
    return () => clearInterval(timer);
  }, []);

  useEffect(() => {
    handleRunSimulation();
  }, []);

  const showToast = (message, type = 'info') => {
    setToast({ message, type });
    setTimeout(() => {
      setToast(null);
    }, 5000);
  };

  // Fallback simulator engine when backend is offline
  const generateRealisticSimulation = (input) => {
    const qty = Number(input.quantityMt) || 150000;
    const baseRates = {
      crude_oil: 19.80,
      iron_ore: 13.50,
      grain: 28.40,
      coal: 16.20,
      lng: 48.00,
      clean_products: 34.50
    };

    const rateBase = baseRates[input.cargoType] || 22.00;
    const urgencyMultiplier = input.urgency === 'expedited' ? 1.08 : input.urgency === 'flexible' ? 0.96 : 1.0;
    const finalRate = rateBase * urgencyMultiplier;
    const totalCost = finalRate * qty;
    const transitDays = Math.round(18 + (qty / 100000) * 2);

    const chartPoints = [];
    for (let i = -6; i <= 6; i++) {
      const isPast = i <= 0;
      const noise = Math.sin(i * 0.8) * 1.4;
      const drift = (i * 0.35);
      chartPoints.push({
        date: `Sep ${Math.max(1, (20 + i * 3) % 30 || 28)}`,
        rate: Number((finalRate + noise + (isPast ? -1.2 : drift)).toFixed(2)),
        isForecast: !isPast
      });
    }

    return {
      summary: {
        ratePerMt: finalRate,
        rateUnit: '$/MT',
        rateDeltaPct: input.urgency === 'expedited' ? 4.8 : -1.6,
        totalVoyageCost: totalCost,
        bunkerSensitivity: 'VLSFO $612/MT',
        transitDays: transitDays,
        etaDate: input.deliveryDate,
        ciiRating: qty > 200000 ? 'A' : 'B',
        co2EstMt: Math.round(qty * 0.024)
      },
      recommendation: {
        headline: input.urgency === 'expedited'
          ? 'SECURE IMMEDIATE SPOT TONNAGE — ESCALATING BUNKER SPREADS'
          : 'FIX ON SPOT MARKET NOW — FAVORABLE TONNAGE INFLOW',
        subtext: `Simulated for ${input.originPort} → ${input.destinationPort} for ${qty.toLocaleString()} MT ${input.cargoType}.`,
        confidence: 89,
        drivers: [
          {
            title: 'Atlantic Fleet Availability',
            desc: '6 uncommitted VLCC/Capesize ballasters heading toward Arabian Gulf/US Gulf.'
          },
          {
            title: 'FFA Paper Curve Discount',
            desc: 'Forward swap derivatives show -$1.40/MT backwardation over Q4 laycan windows.'
          },
          {
            title: 'Bunker Hedging Opportunity',
            desc: 'Rotterdam VLSFO softening offers $28k bunkering cost optimization.'
          }
        ]
      },
      chartData: chartPoints,
      signals: [
        {
          type: 'bullish',
          factor: 'VESSEL SUPPLY',
          title: `Prompt Availability Tight for ${input.cargoType.replace('_', ' ').toUpperCase()}`,
          desc: 'Ballast voyages to loading ports are restricted by regional maintenance schedules.',
          impact: '+3.4% Rate Pressure'
        },
        {
          type: 'bearish',
          factor: 'FUEL BUNKERS',
          title: 'Singapore VLSFO Pricing Down 2.1%',
          desc: 'Declining crude benchmark futures lowering bunker component in voyage estimates.',
          impact: '-$0.95/MT Voyage Exp'
        },
        {
          type: 'neutral',
          factor: 'PORT TURNAROUND',
          title: `${input.destinationPort} Berth Congestion Normalized`,
          desc: 'Discharge wait times averaging 1.4 days, within standard demurrage thresholds.',
          impact: '0.0d Laytime Variance'
        }
      ]
    };
  };

  const handleRunSimulation = async (e) => {
    if (e) e.preventDefault();
    setLoading(true);

    try {
      if (forecastData && forecastData.summary) {
        setBaselineScenario({
          label: `Prev (${formData.originPort} → ${formData.destinationPort})`,
          ratePerMt: forecastData.summary.ratePerMt,
          totalVoyageCost: forecastData.summary.totalVoyageCost,
          transitDays: forecastData.summary.transitDays,
          bunkerCost: forecastData.summary.totalVoyageCost * 0.42,
          ciiScore: forecastData.summary.ciiRating
        });
      }

      const response = await fetch('http://127.0.0.1:8001/api/scenario', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData)
      });

      if (!response.ok) throw new Error(`Status ${response.status}`);
      const result = await response.json();
      setForecastData(result);
      showToast('Simulation updated with live market feed.', 'info');
    } catch (err) {
      console.warn('Backend offline, using maritime simulator engine.', err);
      const simulatedResult = generateRealisticSimulation(formData);
      setForecastData(simulatedResult);
      showToast('Simulation calculated via terminal model (API offline).', 'info');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fi-app">
      {/* HEADER */}
      <header className="fi-header">
        <div className="fi-header-inner">
          <div className="fi-brand">
            <div className="fi-brand-badge">⚓</div>
            <div className="fi-brand-titles">
              <div className="fi-brand-name">
                Freight <span>Intelligence</span>
              </div>
              <div className="fi-brand-sub">
                Vessel Charter & Cargo Forecasting Simulator — Terminal v2.4
              </div>
            </div>
          </div>

          <div className="fi-header-meta">
            <div className="fi-clock">
              <span>🌐</span> {currentTime}
            </div>
            <div className="fi-status-pill">
              <span className="fi-pulse-dot" />
              <span>System Online</span>
            </div>
          </div>
        </div>
      </header>

      {/* TOAST ALERT */}
      {toast && (
        <div className={`fi-toast ${toast.type}`}>
          <span>{toast.type === 'error' ? '⚠️' : 'ℹ️'}</span>
          <span>{toast.message}</span>
          <button className="fi-toast-close" onClick={() => setToast(null)}>✕</button>
        </div>
      )}

      {/* DASHBOARD GRID */}
      <main className="fi-container">
        <div className="fi-grid-layout">
          {/* SCENARIO FORM */}
          <aside>
            <ScenarioInputs
              formData={formData}
              onChange={setFormData}
              onSubmit={handleRunSimulation}
              loading={loading}
            />
          </aside>

          {/* FORECAST & INTELLIGENCE */}
          <section className="fi-forecast-workspace">
            {loading ? (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
                <div className="fi-skeleton fi-skeleton-kpi" />
                <div className="fi-skeleton fi-skeleton-chart" />
                <div className="fi-skeleton fi-skeleton-kpi" />
              </div>
            ) : forecastData ? (
              <>
                <ForecastSummary summary={forecastData.summary} />
                <CharterRecommendation recommendation={forecastData.recommendation} />
                <FreightRateChart chartData={forecastData.chartData} />
                <MarketSignals signals={forecastData.signals} />
                <ScenarioComparison
                  baselineScenario={baselineScenario}
                  currentScenario={forecastData.summary}
                />
              </>
            ) : null}
          </section>
        </div>
      </main>
    </div>
  );
}