function ForecastSummary({ scenario, forecast = {} }) {
  if (!scenario) {
    return null;
  }

  const freightRate = Number(forecast.freightRate ?? 24.5);
  const transitDays = Number(forecast.transitDays ?? 18);
  const confidence = Number(forecast.confidence ?? 82);

  const voyageCost =
    freightRate * Number(scenario.quantity || 0);

  return (
    <section className="forecast-section">
      <div className="forecast-heading">
        <div>
          <p className="section-label">FORECAST ANALYSIS</p>

          <h2>Forecast Analysis</h2>

          <p className="forecast-route">
            {scenario.origin} → {scenario.destination} ·{" "}
            {scenario.cargoType} ·{" "}
            {Number(scenario.quantity || 0).toLocaleString()} MT
          </p>
        </div>

        <div className="forecast-status">
          <span className="status-dot"></span>
          LIVE SCENARIO
        </div>
      </div>

      <div className="forecast-summary-grid">
        <div className="forecast-card">
          <p className="forecast-card-label">
            Estimated Freight Rate
          </p>

          <h3>${freightRate.toFixed(2)}</h3>

          <span>USD / MT</span>
        </div>

        <div className="forecast-card">
          <p className="forecast-card-label">
            Estimated Voyage Cost
          </p>

          <h3>
            ${(voyageCost / 1000000).toFixed(2)}M
          </h3>

          <span>Approx. cargo freight</span>
        </div>

        <div className="forecast-card">
          <p className="forecast-card-label">
            Estimated Transit
          </p>

          <h3>{transitDays}</h3>

          <span>Days</span>
        </div>

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