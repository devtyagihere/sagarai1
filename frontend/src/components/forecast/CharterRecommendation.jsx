import React from 'react';

export default function CharterRecommendation({ recommendation }) {
  if (!recommendation) return null;

  const {
    headline = 'FIX ON SPOT MARKET NOW',
    subtext = 'Spot fixture recommended before expected Atlantic fleet repositioning.',
    confidence = 88,
    drivers = [
      {
        title: 'Tonnage Supply Surplus',
        desc: '14 ballasting vessels arriving in loading region within 10-day laycan window.'
      },
      {
        title: 'Bunker Price Softening',
        desc: 'Singapore & Rotterdam VLSFO spreads down 2.8% on crude inventory builds.'
      },
      {
        title: 'Forward FFA Discount',
        desc: 'Paper swaps trading at a -$1.20/MT backwardation into Q4 deliveries.'
      }
    ]
  } = recommendation;

  return (
    <div className="fi-verdict-card">
      <div className="fi-verdict-head">
        <div>
          <div className="fi-verdict-tag">
            <span>🛡️</span> Strategic Charter Verdict
          </div>
          <h2 className="fi-verdict-title">{headline}</h2>
          <p style={{ fontSize: '12px', color: 'var(--text-secondary)', marginTop: '4px' }}>
            {subtext}
          </p>
        </div>

        <div className="fi-confidence-box">
          <div className="fi-confidence-score tabular-nums">{confidence}%</div>
          <div className="fi-confidence-label">Model Confidence</div>
        </div>
      </div>

      <div className="fi-verdict-rationale">
        {drivers.map((d, index) => (
          <div key={index} className="fi-driver-item">
            <div className="fi-driver-title">
              <span style={{ color: 'var(--accent-cyan-bright)' }}>▪</span>
              {d.title}
            </div>
            <div className="fi-driver-desc">{d.desc}</div>
          </div>
        ))}
      </div>
    </div>
  );
}