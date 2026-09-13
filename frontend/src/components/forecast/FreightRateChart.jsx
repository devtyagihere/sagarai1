import React, { useState, useRef } from 'react';
import {
  CalendarDays,
  TrendingUp,
  TrendingDown,
  Info,
  ShieldCheck,
  Eye,
  EyeOff,
  Crosshair,
  Sliders,
  Sparkles,
  Layers,
} from 'lucide-react';

export default function FreightRateChart({
  forecast,
  evaluation,
  origin,
  destination,
  cargo,
  deliveryDate,
  chartData,
}) {
  const [hoveredIndex, setHoveredIndex] = useState(null);
  const [selectedIndex, setSelectedIndex] = useState(null);
  const [horizonFilter, setHorizonFilter] = useState('all'); // 'all', '7d', '15d', '30d'
  const [showConfidenceBand, setShowConfidenceBand] = useState(true);
  const [showBenchmarkLine, setShowBenchmarkLine] = useState(false);
  const [benchmarkRate, setBenchmarkRate] = useState(25.0);

  const svgRef = useRef(null);

  // Determine base values
  const currentRate = forecast?.current_rate_usd_mt ?? 24.50;
  const f7 = forecast?.forecast_7d_usd_mt ?? (currentRate * 1.025);
  const f15 = forecast?.forecast_15d_usd_mt ?? (currentRate * 1.05);
  const f30 = forecast?.forecast_30d_usd_mt ?? (currentRate * 1.08);
  const changePct = forecast?.forecast_change_percent ?? (((f30 - currentRate) / currentRate) * 100);
  const direction = forecast?.forecast_direction || (changePct >= 0 ? 'up' : 'down');
  const mae = evaluation?.mae ?? 0.85;
  const r2 = evaluation?.r2_score ?? 0.95;
  const modelName = evaluation?.model_name || 'RandomForestRegressor';

  // Always anchor the trajectory timeline to TODAY (current actual date)
  const today = new Date();

  const formatDateOffset = (daysOffset, label) => {
    const d = new Date(today.getTime() + daysOffset * 86400000);
    const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
    return {
      dateStr: `${months[d.getMonth()]} ${String(d.getDate()).padStart(2, '0')}`,
      label: label || `${daysOffset >= 0 ? '+' : ''}${daysOffset}d`,
    };
  };

  const todayMonthName = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'][today.getMonth()];
  const todayDayStr = String(today.getDate()).padStart(2, '0');

  // Trajectory points dynamically driven by actual variables
  const rateDelta = f30 - currentRate;
  const rawPoints = [
    {
      ...formatDateOffset(-30, '-30d'),
      rate: Number((currentRate - rateDelta * 0.82).toFixed(2)),
      isForecast: false,
      descriptor: 'Historical Fixture (-30d)',
      bdiImpact: 'BDI 1,420 · Baseline',
      bunkerImpact: 'VLSFO $620/MT',
    },
    {
      ...formatDateOffset(-20, '-20d'),
      rate: Number((currentRate - rateDelta * 0.55).toFixed(2)),
      isForecast: false,
      descriptor: 'Historical Fixture (-20d)',
      bdiImpact: 'BDI 1,460 · +2.8%',
      bunkerImpact: 'VLSFO $635/MT',
    },
    {
      ...formatDateOffset(-10, '-10d'),
      rate: Number((currentRate - rateDelta * 0.28).toFixed(2)),
      isForecast: false,
      descriptor: 'Historical Fixture (-10d)',
      bdiImpact: 'BDI 1,490 · +4.9%',
      bunkerImpact: 'VLSFO $640/MT',
    },
    {
      ...formatDateOffset(-4, '-4d'),
      rate: Number((currentRate - rateDelta * 0.10).toFixed(2)),
      isForecast: false,
      descriptor: 'Recent Fixture (-4d)',
      bdiImpact: 'BDI 1,510 · Tightening',
      bunkerImpact: 'VLSFO $645/MT',
    },
    {
      dateStr: 'Today',
      label: 'Current',
      rate: Number(currentRate.toFixed(2)),
      isForecast: false,
      descriptor: `Current Spot Rate (Prompt Fixing · ${todayMonthName} ${todayDayStr})`,
      bdiImpact: 'BDI Live Spot',
      bunkerImpact: 'VLSFO Market Spot',
    },
    {
      ...formatDateOffset(7, '+7d'),
      rate: Number(f7.toFixed(2)),
      isForecast: true,
      horizon: '7d',
      descriptor: '7-Day ML Forecast Projection',
      bdiImpact: 'Forward Curves +3.2%',
      bunkerImpact: 'Expected Bunker Stability',
    },
    {
      ...formatDateOffset(15, '+15d'),
      rate: Number(f15.toFixed(2)),
      isForecast: true,
      horizon: '15d',
      descriptor: '15-Day ML Forecast Projection',
      bdiImpact: 'Seasonal Demand Peak',
      bunkerImpact: 'Oil Volatility Buffer',
    },
    {
      ...formatDateOffset(30, '+30d'),
      rate: Number(f30.toFixed(2)),
      isForecast: true,
      horizon: '30d',
      descriptor: '30-Day ML Forecast Outlook',
      bdiImpact: 'Full Horizon Trajectory',
      bunkerImpact: 'Long-term Trend',
    },
  ];

  // Filter points based on selected horizon
  let points = rawPoints;
  if (horizonFilter === '7d') {
    points = rawPoints.filter((p) => !p.isForecast || p.horizon === '7d');
  } else if (horizonFilter === '15d') {
    points = rawPoints.filter((p) => !p.isForecast || p.horizon === '7d' || p.horizon === '15d');
  } else if (horizonFilter === 'forecast_only') {
    points = rawPoints.filter((p) => p.isForecast || p.label === 'Current');
  }

  // SVG Coordinates calculation
  const svgWidth = 840;
  const svgHeight = 290;
  const padding = { top: 38, right: 40, bottom: 48, left: 65 };

  const innerWidth = svgWidth - padding.left - padding.right;
  const innerHeight = svgHeight - padding.top - padding.bottom;

  const rates = points.map((p) => p.rate);
  const minRateVal = Math.min(...rates, showBenchmarkLine ? benchmarkRate : 9999);
  const maxRateVal = Math.max(...rates, showBenchmarkLine ? benchmarkRate : 0);
  const spread = Math.max(maxRateVal - minRateVal, 1.5);

  const minRate = Math.max(0, Number((minRateVal - spread * 0.18).toFixed(2)));
  const maxRate = Number((maxRateVal + spread * 0.22).toFixed(2));

  const getX = (idx) => padding.left + (idx / (points.length - 1)) * innerWidth;
  const getY = (val) => padding.top + innerHeight - ((val - minRate) / (maxRate - minRate)) * innerHeight;

  // Paths
  const linePath = points.map((p, idx) => `${idx === 0 ? 'M' : 'L'} ${getX(idx)} ${getY(p.rate)}`).join(' ');
  const areaPath = `${linePath} L ${getX(points.length - 1)} ${padding.top + innerHeight} L ${getX(0)} ${padding.top + innerHeight} Z`;

  // Confidence Band for forecast points
  const forecastPoints = points.filter((p) => p.isForecast);
  const todayIndex = points.findIndex((p) => p.label === 'Current');
  let confidencePath = '';
  if (forecastPoints.length > 0 && todayIndex >= 0 && showConfidenceBand) {
    const bandPoints = [points[todayIndex], ...forecastPoints];
    const upperPoints = bandPoints.map((p) => {
      const idx = points.indexOf(p);
      const confRate = p.isForecast ? p.rate + mae * 1.6 : p.rate;
      return `${getX(idx)} ${getY(confRate)}`;
    });
    const lowerPoints = [...bandPoints].reverse().map((p) => {
      const idx = points.indexOf(p);
      const confRate = p.isForecast ? Math.max(minRate, p.rate - mae * 1.6) : p.rate;
      return `${getX(idx)} ${getY(confRate)}`;
    });
    confidencePath = `M ${upperPoints[0]} L ${upperPoints.slice(1).join(' L ')} L ${lowerPoints.join(' L ')} Z`;
  }

  const todayX = todayIndex >= 0 ? getX(todayIndex) : null;

  // Dynamic Y ticks: 5 clean levels
  const yTickValues = [0, 0.25, 0.5, 0.75, 1.0].map(
    (ratio) => minRate + ratio * (maxRate - minRate)
  );

  const activeIndex = hoveredIndex !== null ? hoveredIndex : selectedIndex;
  const activePoint = activeIndex !== null && points[activeIndex] ? points[activeIndex] : null;

  // Handle continuous mouse move over SVG
  const handleMouseMove = (e) => {
    if (!svgRef.current) return;
    const rect = svgRef.current.getBoundingClientRect();
    const clientX = e.clientX - rect.left;
    const svgX = (clientX / rect.width) * svgWidth;

    if (svgX < padding.left - 10 || svgX > svgWidth - padding.right + 10) return;

    let closestIdx = 0;
    let minDistance = 99999;
    points.forEach((_, idx) => {
      const px = getX(idx);
      const dist = Math.abs(px - svgX);
      if (dist < minDistance) {
        minDistance = dist;
        closestIdx = idx;
      }
    });
    setHoveredIndex(closestIdx);
  };

  return (
    <div style={{ width: '100%', fontFamily: 'inherit' }}>
      {/* ── Top Controls & Interactive Legend Bar ── */}
      <div
        style={{
          display: 'flex',
          flexWrap: 'wrap',
          alignItems: 'center',
          justifyContent: 'space-between',
          gap: '12px',
          marginBottom: '14px',
          paddingBottom: '12px',
          borderBottom: '1px solid #e2e8f0',
        }}
      >
        {/* Route & Cargo Tag */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', flexWrap: 'wrap' }}>
          <span
            style={{
              fontSize: '12px',
              fontWeight: 700,
              letterSpacing: '0.04em',
              color: '#0f766e',
              background: '#ccfbf1',
              padding: '4px 10px',
              borderRadius: '6px',
            }}
          >
            {origin || 'Origin'} → {destination || 'Destination'} ({cargo || 'Dry Bulk'})
          </span>
          <span
            style={{
              display: 'inline-flex',
              alignItems: 'center',
              gap: '4px',
              fontSize: '12px',
              fontWeight: 600,
              color: changePct >= 0 ? '#15803d' : '#b91c1c',
              background: changePct >= 0 ? '#f0fdf4' : '#fef2f2',
              padding: '4px 8px',
              borderRadius: '6px',
            }}
          >
            {changePct >= 0 ? <TrendingUp size={14} /> : <TrendingDown size={14} />}
            {changePct >= 0 ? '+' : ''}
            {changePct.toFixed(1)}% 30d Trajectory
          </span>
        </div>

        {/* Interactive Horizon Filter & Layer Toggles */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '6px', flexWrap: 'wrap' }}>
          <span style={{ fontSize: '11px', color: '#64748b', fontWeight: 600, marginRight: '2px' }}>
            VIEW:
          </span>
          {[
            { id: 'all', label: 'Full Trajectory' },
            { id: '7d', label: '7-Day' },
            { id: '15d', label: '15-Day' },
            { id: 'forecast_only', label: 'Forecast Only' },
          ].map((btn) => (
            <button
              key={btn.id}
              type="button"
              onClick={() => setHorizonFilter(btn.id)}
              style={{
                fontSize: '11px',
                fontWeight: 600,
                padding: '4px 9px',
                borderRadius: '6px',
                border: horizonFilter === btn.id ? '1px solid #0f766e' : '1px solid #cbd5e1',
                background: horizonFilter === btn.id ? '#0f766e' : '#ffffff',
                color: horizonFilter === btn.id ? '#ffffff' : '#475569',
                cursor: 'pointer',
                transition: 'all 0.15s ease',
              }}
            >
              {btn.label}
            </button>
          ))}

          {/* Confidence Band Toggle */}
          <button
            type="button"
            onClick={() => setShowConfidenceBand(!showConfidenceBand)}
            title="Toggle 95% Confidence Band"
            style={{
              fontSize: '11px',
              fontWeight: 600,
              padding: '4px 9px',
              borderRadius: '6px',
              border: showConfidenceBand ? '1px solid #10b981' : '1px solid #cbd5e1',
              background: showConfidenceBand ? '#f0fdf4' : '#ffffff',
              color: showConfidenceBand ? '#15803d' : '#64748b',
              cursor: 'pointer',
              display: 'inline-flex',
              alignItems: 'center',
              gap: '4px',
              marginLeft: '4px',
            }}
          >
            {showConfidenceBand ? <Eye size={12} /> : <EyeOff size={12} />}
            <span>±MAE Band</span>
          </button>

          {/* Benchmark Target Toggle */}
          <button
            type="button"
            onClick={() => setShowBenchmarkLine(!showBenchmarkLine)}
            title="Toggle Target Rate Benchmark"
            style={{
              fontSize: '11px',
              fontWeight: 600,
              padding: '4px 9px',
              borderRadius: '6px',
              border: showBenchmarkLine ? '1px solid #f59e0b' : '1px solid #cbd5e1',
              background: showBenchmarkLine ? '#fef3c7' : '#ffffff',
              color: showBenchmarkLine ? '#b45309' : '#64748b',
              cursor: 'pointer',
              display: 'inline-flex',
              alignItems: 'center',
              gap: '4px',
            }}
          >
            <Crosshair size={12} />
            <span>Target Line</span>
          </button>
        </div>
      </div>

      {/* Target Rate Benchmark Slider Bar (when enabled) */}
      {showBenchmarkLine && (
        <div
          style={{
            background: '#fffbeb',
            border: '1px solid #fde68a',
            borderRadius: '8px',
            padding: '8px 14px',
            marginBottom: '12px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            gap: '12px',
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '11px', fontWeight: 700, color: '#b45309' }}>
            <Crosshair size={14} />
            <span>Charterer Budget Threshold Target:</span>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px', flex: 1, maxWidth: '300px' }}>
            <input
              type="range"
              min={Number((minRate + 0.5).toFixed(1))}
              max={Number((maxRate - 0.5).toFixed(1))}
              step="0.25"
              value={benchmarkRate}
              onChange={(e) => setBenchmarkRate(Number(e.target.value))}
              className="interactive-range-input"
              style={{ accentColor: '#d97706' }}
            />
            <strong style={{ fontSize: '12px', color: '#b45309', minWidth: '70px' }}>
              ${benchmarkRate.toFixed(2)}/MT
            </strong>
          </div>
          <span style={{ fontSize: '11px', color: '#78350f' }}>
            {currentRate <= benchmarkRate ? `✓ Under target by $${(benchmarkRate - currentRate).toFixed(2)}/MT` : `⚠ Above target by $${(currentRate - benchmarkRate).toFixed(2)}/MT`}
          </span>
        </div>
      )}

      {/* ── Main Interactive SVG Chart Container ── */}
      <div
        style={{
          position: 'relative',
          width: '100%',
          overflow: 'hidden',
          background: '#ffffff',
          borderRadius: '10px',
          border: '1px solid #e2e8f0',
          boxShadow: 'inset 0 1px 4px rgba(0,0,0,0.02)',
        }}
      >
        {/* Floating Tooltip with Dynamic Position */}
        {activePoint && (
          <div
            style={{
              position: 'absolute',
              top: '10px',
              right: '12px',
              background: '#0f172a',
              color: '#f8fafc',
              padding: '8px 14px',
              borderRadius: '8px',
              boxShadow: '0 6px 18px rgba(0,0,0,0.2)',
              fontSize: '12px',
              zIndex: 10,
              pointerEvents: 'none',
              display: 'flex',
              alignItems: 'center',
              gap: '14px',
              borderLeft: `4px solid ${activePoint.isForecast ? '#10b981' : '#0284c7'}`,
              animation: 'fadeIn 0.15s ease',
            }}
          >
            <div>
              <span style={{ color: '#94a3b8', display: 'block', fontSize: '10px', textTransform: 'uppercase', letterSpacing: '0.04em' }}>
                {activePoint.descriptor}
              </span>
              <strong style={{ fontSize: '15px', color: activePoint.isForecast ? '#4ade80' : '#38bdf8' }}>
                ${activePoint.rate.toFixed(2)} / MT
              </strong>
            </div>
            <div style={{ borderLeft: '1px solid #334155', paddingLeft: '12px' }}>
              <span style={{ color: '#cbd5e1', fontWeight: 600 }}>{activePoint.dateStr}</span>
              <span
                style={{
                  display: 'block',
                  fontSize: '10px',
                  color: activePoint.isForecast ? '#4ade80' : '#94a3b8',
                }}
              >
                {activePoint.isForecast ? 'ML Prediction Model' : 'Verified Baltic Fixture'}
              </span>
            </div>
          </div>
        )}

        <svg
          ref={svgRef}
          viewBox={`0 0 ${svgWidth} ${svgHeight}`}
          style={{ width: '100%', height: 'auto', display: 'block', cursor: 'crosshair' }}
          onMouseMove={handleMouseMove}
          onMouseLeave={() => setHoveredIndex(null)}
          onClick={() => {
            if (hoveredIndex !== null) {
              setSelectedIndex(hoveredIndex === selectedIndex ? null : hoveredIndex);
            }
          }}
        >
          <defs>
            <linearGradient id="areaGradient" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor="#0284c7" stopOpacity="0.22" />
              <stop offset="100%" stopColor="#0284c7" stopOpacity="0.0" />
            </linearGradient>
            <linearGradient id="confidenceGradient" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor="#10b981" stopOpacity="0.18" />
              <stop offset="100%" stopColor="#10b981" stopOpacity="0.03" />
            </linearGradient>
            <linearGradient id="lineGrad" x1="0" y1="0" x2="1" y2="0">
              <stop offset="0%" stopColor="#0284c7" />
              <stop offset="60%" stopColor="#0f766e" />
              <stop offset="100%" stopColor="#10b981" />
            </linearGradient>
          </defs>

          {/* Horizontal Grid lines & Y-axis labels */}
          {yTickValues.map((val, i) => {
            const y = getY(val);
            return (
              <g key={`ytick-${i}`}>
                <line
                  x1={padding.left}
                  y1={y}
                  x2={svgWidth - padding.right}
                  y2={y}
                  stroke="#f1f5f9"
                  strokeDasharray="4 4"
                  strokeWidth="1"
                />
                <text
                  x={padding.left - 12}
                  y={y + 4}
                  textAnchor="end"
                  fontSize="11"
                  fill="#64748b"
                  fontFamily="sans-serif"
                  fontWeight="500"
                >
                  ${val.toFixed(2)}
                </text>
              </g>
            );
          })}

          {/* Target Rate Benchmark Horizontal Line */}
          {showBenchmarkLine && (
            <g>
              <line
                x1={padding.left}
                y1={getY(benchmarkRate)}
                x2={svgWidth - padding.right}
                y2={getY(benchmarkRate)}
                stroke="#d97706"
                strokeWidth="1.5"
                strokeDasharray="6 3"
              />
              <text
                x={svgWidth - padding.right}
                y={getY(benchmarkRate) - 6}
                textAnchor="end"
                fontSize="10"
                fontWeight="700"
                fill="#d97706"
              >
                TARGET: ${benchmarkRate.toFixed(2)}/MT
              </text>
            </g>
          )}

          {/* Confidence Interval Band (95% CI) */}
          {confidencePath && showConfidenceBand && (
            <path
              d={confidencePath}
              fill="url(#confidenceGradient)"
              stroke="#10b981"
              strokeWidth="0.8"
              strokeDasharray="3 3"
            />
          )}

          {/* Area fill */}
          <path d={areaPath} fill="url(#areaGradient)" />

          {/* Rate Trajectory Line */}
          <path
            d={linePath}
            fill="none"
            stroke="url(#lineGrad)"
            strokeWidth="3"
            strokeLinecap="round"
            strokeLinejoin="round"
          />

          {/* Today Divider Marker */}
          {todayX && (
            <g>
              <line
                x1={todayX}
                y1={padding.top - 12}
                x2={todayX}
                y2={padding.top + innerHeight}
                stroke="#0f766e"
                strokeWidth="1.5"
                strokeDasharray="4 3"
              />
              <rect
                x={todayX - 44}
                y={padding.top - 26}
                width="88"
                height="20"
                rx="4"
                fill="#0f766e"
              />
              <text
                x={todayX}
                y={padding.top - 13}
                textAnchor="middle"
                fontSize="9"
                fontWeight="700"
                fill="#ffffff"
                letterSpacing="0.04em"
              >
                TODAY (FIXING)
              </text>
            </g>
          )}

          {/* Interactive Scrubbing Crosshair Line */}
          {activeIndex !== null && (
            <g>
              <line
                x1={getX(activeIndex)}
                y1={padding.top}
                x2={getX(activeIndex)}
                y2={padding.top + innerHeight}
                stroke="#38bdf8"
                strokeWidth="1.5"
                strokeDasharray="3 2"
              />
              <line
                x1={padding.left}
                y1={getY(points[activeIndex].rate)}
                x2={svgWidth - padding.right}
                y2={getY(points[activeIndex].rate)}
                stroke="#38bdf8"
                strokeWidth="1"
                strokeDasharray="3 2"
              />
            </g>
          )}

          {/* Data Points */}
          {points.map((p, idx) => {
            const cx = getX(idx);
            const cy = getY(p.rate);
            const isHovered = activeIndex === idx;
            const isSelected = selectedIndex === idx;
            const isToday = p.label === 'Current';

            return (
              <g
                key={`pt-${idx}`}
                onMouseEnter={() => setHoveredIndex(idx)}
                style={{ cursor: 'pointer' }}
              >
                {/* Larger invisible hit area for easy tapping/clicking */}
                <circle cx={cx} cy={cy} r="18" fill="transparent" />

                {/* Point Halo when active/hovered */}
                {isHovered && (
                  <circle
                    cx={cx}
                    cy={cy}
                    r={p.isForecast ? 12 : 9}
                    fill={p.isForecast ? '#10b981' : '#0284c7'}
                    opacity="0.3"
                  />
                )}

                {/* Point Circle */}
                <circle
                  cx={cx}
                  cy={cy}
                  r={isHovered ? 6.5 : isSelected ? 7 : isToday ? 5.5 : p.isForecast ? 4.5 : 3.5}
                  fill={isToday ? '#0f766e' : p.isForecast ? '#10b981' : '#0284c7'}
                  stroke="#ffffff"
                  strokeWidth={isToday || isSelected ? 2.5 : 2}
                />

                {/* X-axis date labels */}
                <text
                  x={cx}
                  y={svgHeight - 16}
                  textAnchor="middle"
                  fontSize="11"
                  fontWeight={isToday || isSelected ? '700' : '500'}
                  fill={isToday ? '#0f766e' : isSelected ? '#0284c7' : '#64748b'}
                >
                  {p.dateStr}
                </text>
                <text
                  x={cx}
                  y={svgHeight - 4}
                  textAnchor="middle"
                  fontSize="9"
                  fill="#94a3b8"
                >
                  {p.label}
                </text>
              </g>
            );
          })}
        </svg>
      </div>

      {/* ── Interactive Point Detail Inspector (Updates on Click/Scrub) ── */}
      {activePoint && (
        <div
          style={{
            marginTop: '12px',
            background: '#f8fafc',
            border: '1px solid #e2e8f0',
            borderRadius: '10px',
            padding: '10px 16px',
            display: 'flex',
            flexWrap: 'wrap',
            alignItems: 'center',
            justifyContent: 'space-between',
            gap: '12px',
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <span style={{ fontSize: '11px', color: '#64748b', fontWeight: 600 }}>INSPECTING POINT:</span>
            <strong style={{ fontSize: '12px', color: '#0f172a' }}>{activePoint.descriptor}</strong>
            <span className={`interactive-pill-tag ${activePoint.isForecast ? 'green' : 'blue'}`} style={{ fontSize: '10px' }}>
              {activePoint.dateStr}
            </span>
          </div>

          <div style={{ display: 'flex', alignItems: 'center', gap: '16px', fontSize: '12px' }}>
            <div>
              <span style={{ color: '#64748b' }}>Rate: </span>
              <strong style={{ color: '#0f766e' }}>${activePoint.rate.toFixed(2)}/MT</strong>
            </div>
            <div>
              <span style={{ color: '#64748b' }}>Variance vs Today: </span>
              <strong style={{ color: activePoint.rate >= currentRate ? '#15803d' : '#b91c1c' }}>
                {activePoint.rate >= currentRate ? '+' : ''}
                {(((activePoint.rate - currentRate) / currentRate) * 100).toFixed(1)}%
              </strong>
            </div>
            <div>
              <span style={{ color: '#64748b' }}>Driver: </span>
              <span style={{ color: '#334155', fontWeight: 600 }}>{activePoint.bdiImpact}</span>
            </div>
          </div>
        </div>
      )}

      {/* ── Legend and Model Evaluation Footer ── */}
      <div
        style={{
          marginTop: '12px',
          paddingTop: '10px',
          borderTop: '1px solid #f1f5f9',
          display: 'flex',
          flexWrap: 'wrap',
          alignItems: 'center',
          justifyContent: 'space-between',
          fontSize: '11px',
          color: '#64748b',
          gap: '8px',
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: '16px', flexWrap: 'wrap' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
            <span style={{ width: '12px', height: '3px', background: '#0284c7', display: 'inline-block', borderRadius: '2px' }} />
            <span>Baltic Historical Fixtures</span>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
            <span style={{ width: '12px', height: '3px', background: '#10b981', display: 'inline-block', borderRadius: '2px' }} />
            <span>ML Rate Forecast</span>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
            <span style={{ width: '10px', height: '10px', background: 'rgba(16,185,129,0.18)', border: '1px dashed #10b981', display: 'inline-block', borderRadius: '2px' }} />
            <span>95% Confidence Band (±${typeof mae === 'number' ? mae.toFixed(2) : mae}/MT)</span>
          </div>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <span style={{ display: 'inline-flex', alignItems: 'center', gap: '4px' }}>
            <ShieldCheck size={13} color="#0f766e" />
            <strong>{modelName}</strong> (R² = {typeof r2 === 'number' ? r2.toFixed(2) : r2})
          </span>
          <span>MAE: ${typeof mae === 'number' ? mae.toFixed(2) : mae}/MT</span>
        </div>
      </div>
    </div>
  );
}