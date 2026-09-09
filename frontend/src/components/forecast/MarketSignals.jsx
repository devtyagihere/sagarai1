import React from 'react';

export default function MarketSignals({ signals }) {
  const signalList = signals && signals.length > 0 ? signals : [
    {
      type: 'bullish',
      factor: 'FLEET CAPACITY',
      title: 'Capesize Ballast Deficit in Atlantic',
      desc: 'Only 6 prompt uncommitted vessels positioned west of Cape of Good Hope.',
      impact: '+4.2% Rate Premium'
    },
    {
      type: 'bearish',
      factor: 'BUNKER SENSITIVITY',
      title: 'Singapore VLSFO Fuel Cost Softening',
      desc: 'Rotterdam and Fujairah bunker prices contracted -$18/MT over trailing 72 hours.',
      impact: '-$1.15/MT Voyage Exp'
    },
    {
      type: 'neutral',
      factor: 'CANAL QUEUE',
      title: 'Suez Transit Waiting Windows Stable',
      desc: 'Average northbound convoy delay recorded at 18.4 hours, inside margins.',
      impact: '0.0d Laytime Variance'
    }
  ];

  return (
    <div className="fi-card">
      <div className="fi-card-header">
        <div className="fi-card-title">
          <span className="fi-card-title-icon">📡</span>
          Real-Time Market Signals & Volatility Drivers
        </div>
        <span className="badge-mono" style={{ fontSize: '10px', color: 'var(--text-muted)' }}>LIVE FEED</span>
      </div>

      <div className="fi-card-body">
        <div className="fi-signals-grid">
          {signalList.map((sig, idx) => (
            <div key={idx} className={`fi-signal-card ${sig.type}`}>
              <div className="fi-signal-header">
                <span className="fi-signal-factor">{sig.factor}</span>
                <span className={`fi-signal-pill ${sig.type}`}>
                  {sig.type === 'bullish' ? '▲ BULLISH' : sig.type === 'bearish' ? '▼ BEARISH' : '● NEUTRAL'}
                </span>
              </div>
              <div className="fi-signal-text">{sig.title}</div>
              <p style={{ fontSize: '11px', color: 'var(--text-secondary)', lineHeight: 1.35 }}>
                {sig.desc}
              </p>
              <div className="fi-signal-impact">
                Impact: <span style={{ color: sig.type === 'bullish' ? '#34D399' : sig.type === 'bearish' ? '#FB7185' : '#FBBF24' }}>
                  {sig.impact}
                </span>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}