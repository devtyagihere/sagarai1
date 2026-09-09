import React, { useState } from 'react';

export default function FreightRateChart({ chartData }) {
  const [hoveredIndex, setHoveredIndex] = useState(null);

  const points = chartData && chartData.length > 0 ? chartData : [
    { date: 'Aug 10', rate: 22.40, isForecast: false },
    { date: 'Aug 15', rate: 23.10, isForecast: false },
    { date: 'Aug 20', rate: 22.80, isForecast: false },
    { date: 'Aug 25', rate: 24.20, isForecast: false },
    { date: 'Aug 30', rate: 24.90, isForecast: false },
    { date: 'Sep 04', rate: 25.10, isForecast: false },
    { date: 'Sep 09', rate: 25.40, isForecast: false },
    { date: 'Sep 14', rate: 26.20, isForecast: true },
    { date: 'Sep 19', rate: 26.90, isForecast: true },
    { date: 'Sep 24', rate: 27.40, isForecast: true },
    { date: 'Sep 29', rate: 28.10, isForecast: true },
    { date: 'Oct 04', rate: 28.50, isForecast: true }
  ];

  const svgWidth = 840;
  const svgHeight = 240;
  const padding = { top: 25, right: 35, bottom: 35, left: 55 };

  const innerWidth = svgWidth - padding.left - padding.right;
  const innerHeight = svgHeight - padding.top - padding.bottom;

  const minRate = Math.min(...points.map(p => p.rate)) * 0.95;
  const maxRate = Math.max(...points.map(p => p.rate)) * 1.05;

  const getX = (idx) => padding.left + (idx / (points.length - 1)) * innerWidth;
  const getY = (val) => padding.top + innerHeight - ((val - minRate) / (maxRate - minRate)) * innerHeight;

  const linePath = points.map((p, idx) => `${idx === 0 ? 'M' : 'L'} ${getX(idx)} ${getY(p.rate)}`).join(' ');
  const areaPath = `${linePath} L ${getX(points.length - 1)} ${padding.top + innerHeight} L ${getX(0)} ${padding.top + innerHeight} Z`;

  const firstForecastIndex = points.findIndex(p => p.isForecast);
  const forecastX = firstForecastIndex >= 0 ? getX(firstForecastIndex) : null;
  const yTicks = [0, 0.33, 0.66, 1].map(ratio => minRate + ratio * (maxRate - minRate));
  const activePoint = hoveredIndex !== null ? points[hoveredIndex] : null;

  return (
    <div className="fi-card">
      <div className="fi-card-header">
        <div className="fi-card-title">
          <span className="fi-card-title-icon">📈</span>
          Freight Rate Trajectory ($/MT)
        </div>
        <div className="fi-chart-legend">
          <div className="fi-legend-item">
            <span className="fi-legend-line historical" />
            <span>Baltic Fixtures (Past)</span>
          </div>
          <div className="fi-legend-item">
            <span className="fi-legend-line forecast" />
            <span>Simulated Forecast</span>
          </div>
          <div className="fi-legend-item">
            <span className="fi-legend-line confidence" />
            <span>95% Confidence Band</span>
          </div>
        </div>
      </div>

      <div className="fi-card-body" style={{ padding: '12px 18px' }}>
        <div className="fi-chart-container">
          {activePoint && (
            <div className="fi-chart-tooltip tabular-nums">
              <span style={{ color: 'var(--text-secondary)' }}>{activePoint.date}: </span>
              <strong style={{ color: 'var(--accent-cyan-bright)' }}>${activePoint.rate.toFixed(2)}/MT</strong>
              {activePoint.isForecast && (
                <span style={{ marginLeft: '6px', color: '#FBBF24', fontSize: '10px' }}>(EST)</span>
              )}
            </div>
          )}

          <svg
            viewBox={`0 0 ${svgWidth} ${svgHeight}`}
            className="fi-chart-svg"
            onMouseLeave={() => setHoveredIndex(null)}
          >
            <defs>
              <linearGradient id="chartGradient" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stopColor="#0EA5E9" stopOpacity="0.25" />
                <stop offset="100%" stopColor="#0EA5E9" stopOpacity="0.0" />
              </linearGradient>
            </defs>

            {yTicks.map((val, i) => {
              const y = getY(val);
              return (
                <g key={`ytick-${i}`}>
                  <line x1={padding.left} y1={y} x2={svgWidth - padding.right} y2={y} className="fi-chart-grid-line" />
                  <text x={padding.left - 10} y={y + 4} textAnchor="end" className="fi-chart-axis-text">
                    ${val.toFixed(1)}
                  </text>
                </g>
              );
            })}

            {forecastX && (
              <g>
                <line x1={forecastX} y1={padding.top} x2={forecastX} y2={padding.top + innerHeight} className="fi-chart-divider-line" />
                <text x={forecastX + 6} y={padding.top + 14} className="fi-chart-axis-text" fill="var(--accent-cyan-bright)">
                  ▶ Forecast Horizon
                </text>
              </g>
            )}

            <path d={areaPath} fill="url(#chartGradient)" />
            <path d={linePath} className="fi-chart-line" />

            {points.map((p, idx) => {
              const cx = getX(idx);
              const cy = getY(p.rate);
              const isHovered = hoveredIndex === idx;

              return (
                <g key={`pt-${idx}`} onMouseEnter={() => setHoveredIndex(idx)}>
                  <circle
                    cx={cx}
                    cy={cy}
                    r={isHovered ? 6 : p.isForecast ? 3.5 : 2.5}
                    className="fi-chart-point"
                    style={{ stroke: p.isForecast ? 'var(--accent-cyan-bright)' : 'var(--text-secondary)' }}
                  />
                  {idx % Math.ceil(points.length / 6) === 0 && (
                    <text x={cx} y={svgHeight - 10} textAnchor="middle" className="fi-chart-axis-text">
                      {p.date}
                    </text>
                  )}
                </g>
              );
            })}
          </svg>
        </div>
      </div>
    </div>
  );
}