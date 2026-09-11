function ForecastSummary({ scenario }) {
  if (!scenario) {
    return null;
  }

  // Temporary frontend values.
  // These will later come from the ML/backend API.
  const freightRate = 24.5;
  const voyageCost = freightRate * Number(scenario.quantity || 0);
  const transitDays = 18;
  const confidence = 82;

  return (
    <section className="forecast-section">

      {/* Section Header */}
      <div className="forecast-heading">
        <div>
          <p className="section-label">FORECAST ANALYSIS</p>

          <h2>Forecast Analysis</h2>

          <p className="forecast-route">
            {scenario.origin} → {scenario.destination} ·{" "}
            {scenario.cargoType} ·{" "}
            {Number(scenario.quantity).toLocaleString()} MT
          </p>
        </div>

        <div className="forecast-status">
          <span className="status-dot"></span>
          LIVE SCENARIO
        </div>
      </div>

      {/* Summary Cards */}
      <div className="forecast-summary-grid">

        {/* Freight Rate */}
        <div className="forecast-card">
          <p className="forecast-card-label">
            Estimated Freight Rate
          </p>

          <h3>
            ${freightRate.toFixed(2)}
          </h3>

          <span>USD / MT</span>
        </div>

        {/* Voyage Cost */}
        <div className="forecast-card">
          <p className="forecast-card-label">
            Estimated Voyage Cost
          </p>

          <h3>
            ${(voyageCost / 1000000).toFixed(2)}M
          </h3>

          <span>Approx. cargo freight</span>
        </div>

        {/* Transit */}
        <div className="forecast-card">
          <p className="forecast-card-label">
            Estimated Transit
          </p>

          <h3>{transitDays}</h3>

          <span>Days</span>
        </div>

        {/* Confidence */}
        <div className="forecast-card">
          <p className="forecast-card-label">
            Forecast Confidence
          </p>

          <h3>{confidence}%</h3>

          <span>Model confidence</span>
        </div>

      </div>

    </section>
  );
}

export default ForecastSummary;