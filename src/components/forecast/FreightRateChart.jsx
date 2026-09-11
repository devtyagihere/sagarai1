import { useState } from "react";

export default function FreightRateChart({ chartData }) {
  const [hoveredIndex, setHoveredIndex] = useState(null);

  const points =
    chartData && chartData.length > 0
      ? chartData
      : [
          { date: "Aug 10", rate: 22.4, isForecast: false },
          { date: "Aug 15", rate: 23.1, isForecast: false },
          { date: "Aug 20", rate: 22.8, isForecast: false },
          { date: "Aug 25", rate: 24.2, isForecast: false },
          { date: "Aug 30", rate: 24.9, isForecast: false },
          { date: "Sep 04", rate: 25.1, isForecast: false },
          { date: "Sep 09", rate: 25.4, isForecast: false },
          { date: "Sep 14", rate: 26.2, isForecast: true },
          { date: "Sep 19", rate: 26.9, isForecast: true },
          { date: "Sep 24", rate: 27.4, isForecast: true },
          { date: "Sep 29", rate: 28.1, isForecast: true },
          { date: "Oct 04", rate: 28.5, isForecast: true },
        ];

  const svgWidth = 840;
  const svgHeight = 240;

  const padding = {
    top: 25,
    right: 35,
    bottom: 35,
    left: 55,
  };

  const innerWidth =
    svgWidth - padding.left - padding.right;

  const innerHeight =
    svgHeight - padding.top - padding.bottom;

  const rates = points.map((point) => Number(point.rate));

  const minRate = Math.min(...rates) * 0.95;
  const maxRate = Math.max(...rates) * 1.05;

  const getX = (index) => {
    if (points.length === 1) {
      return padding.left + innerWidth / 2;
    }

    return (
      padding.left +
      (index / (points.length - 1)) * innerWidth
    );
  };

  const getY = (value) =>
    padding.top +
    innerHeight -
    ((value - minRate) /
      (maxRate - minRate)) *
      innerHeight;

  const linePath = points
    .map(
      (point, index) =>
        `${index === 0 ? "M" : "L"} ${getX(index)} ${getY(
          Number(point.rate)
        )}`
    )
    .join(" ");

  const areaPath = `${linePath}
    L ${getX(points.length - 1)} ${
      padding.top + innerHeight
    }
    L ${getX(0)} ${padding.top + innerHeight}
    Z`;

  const firstForecastIndex = points.findIndex(
    (point) => point.isForecast
  );

  const forecastX =
    firstForecastIndex >= 0
      ? getX(firstForecastIndex)
      : null;

  const yTicks = [0, 0.33, 0.66, 1].map(
    (ratio) =>
      minRate + ratio * (maxRate - minRate)
  );

  const activePoint =
    hoveredIndex !== null
      ? points[hoveredIndex]
      : null;

  return (
    <div className="fi-card">
      <div className="fi-card-header">
        <div className="fi-card-title">
          <span className="fi-card-title-icon">
            📈
          </span>

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

      <div
        className="fi-card-body"
        style={{ padding: "12px 18px" }}
      >
        <div className="fi-chart-container">

          {activePoint && (
            <div className="fi-chart-tooltip tabular-nums">
              <span
                style={{
                  color: "var(--text-secondary)",
                }}
              >
                {activePoint.date}:{" "}
              </span>

              <strong
                style={{
                  color:
                    "var(--accent-cyan-bright)",
                }}
              >
                ${Number(activePoint.rate).toFixed(2)}/MT
              </strong>

              {activePoint.isForecast && (
                <span
                  style={{
                    marginLeft: "6px",
                    color: "#FBBF24",
                    fontSize: "10px",
                  }}
                >
                  (EST)
                </span>
              )}
            </div>
          )}

          <svg
            viewBox={`0 0 ${svgWidth} ${svgHeight}`}
            className="fi-chart-svg"
            onMouseLeave={() =>
              setHoveredIndex(null)
            }
          >
            <defs>
              <linearGradient
                id="chartGradient"
                x1="0"
                y1="0"
                x2="0"
                y2="1"
              >
                <stop
                  offset="0%"
                  stopColor="#0EA5E9"
                  stopOpacity="0.25"
                />

                <stop
                  offset="100%"
                  stopColor="#0EA5E9"
                  stopOpacity="0"
                />
              </linearGradient>
            </defs>

            {/* Y AXIS */}

            {yTicks.map((value, index) => {
              const y = getY(value);

              return (
                <g key={`ytick-${index}`}>
                  <line
                    x1={padding.left}
                    y1={y}
                    x2={svgWidth - padding.right}
                    y2={y}
                    className="fi-chart-grid-line"
                  />

                  <text
                    x={padding.left - 10}
                    y={y + 4}
                    textAnchor="end"
                    className="fi-chart-axis-text"
                  >
                    ${value.toFixed(1)}
                  </text>
                </g>
              );
            })}

            {/* FORECAST DIVIDER */}

            {forecastX !== null && (
              <g>
                <line
                  x1={forecastX}
                  y1={padding.top}
                  x2={forecastX}
                  y2={padding.top + innerHeight}
                  className="fi-chart-divider-line"
                />

                <text
                  x={forecastX + 6}
                  y={padding.top + 14}
                  className="fi-chart-axis-text"
                  fill="var(--accent-cyan-bright)"
                >
                  ▶ Forecast Horizon
                </text>
              </g>
            )}

            {/* AREA */}

            <path
              d={areaPath}
              fill="url(#chartGradient)"
            />

            {/* LINE */}

            <path
              d={linePath}
              className="fi-chart-line"
            />

            {/* POINTS */}

            {points.map((point, index) => {
              const cx = getX(index);
              const cy = getY(
                Number(point.rate)
              );

              const isHovered =
                hoveredIndex === index;

              return (
                <g
                  key={`point-${index}`}
                  onMouseEnter={() =>
                    setHoveredIndex(index)
                  }
                >
                  <circle
                    cx={cx}
                    cy={cy}
                    r={
                      isHovered
                        ? 6
                        : point.isForecast
                        ? 3.5
                        : 2.5
                    }
                    className="fi-chart-point"
                    style={{
                      stroke: point.isForecast
                        ? "var(--accent-cyan-bright)"
                        : "var(--text-secondary)",
                    }}
                  />

                  {index %
                    Math.ceil(points.length / 6) ===
                    0 && (
                    <text
                      x={cx}
                      y={svgHeight - 10}
                      textAnchor="middle"
                      className="fi-chart-axis-text"
                    >
                      {point.date}
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