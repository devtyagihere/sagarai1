"""
Tests for FreightForecastingService — ML model training, evaluation, and forecasting.
All tests use SYNTHETIC data. Metrics and predictions reflect synthetic patterns only.
"""

import pytest

from app.services.market_service import MarketDataService
from app.services.freight_forecasting import FreightForecastingService
from app.models.market import FreightForecast, ModelEvaluation


# ── Fixtures ──────────────────────────────────────────────────────────────────

@pytest.fixture(scope="module")
def market_service():
    svc = MarketDataService()
    svc.load_all()
    return svc


@pytest.fixture(scope="module")
def trained_service(market_service):
    """Return a FreightForecastingService that has been trained once."""
    svc = FreightForecastingService(market_service)
    svc.train()
    return svc


# ── Model Training Tests ──────────────────────────────────────────────────────

class TestModelTraining:
    def test_train_returns_model_evaluation(self, market_service):
        svc = FreightForecastingService(market_service)
        ev: ModelEvaluation = svc.train()
        assert isinstance(ev, ModelEvaluation)

    def test_train_populates_sample_counts(self, trained_service):
        ev = trained_service.get_evaluation()
        assert ev.train_samples > 0
        assert ev.test_samples > 0

    def test_train_uses_correct_features(self, trained_service):
        ev = trained_service.get_evaluation()
        expected_features = {"bdi", "oil_price", "commodity_price", "distance_nm",
                             "vessel_type_enc", "cargo_type_enc"}
        assert expected_features == set(ev.features_used)

    def test_train_is_idempotent(self, market_service):
        """Calling train() twice should return the same metrics."""
        svc = FreightForecastingService(market_service)
        ev1 = svc.train()
        ev2 = svc.train()  # Should use cache, not retrain
        assert ev1.mae == ev2.mae
        assert ev1.r2 == ev2.r2

    def test_force_retrain_works(self, market_service):
        """force_retrain=True should produce consistent metrics."""
        svc = FreightForecastingService(market_service)
        ev1 = svc.train()
        ev2 = svc.train(force_retrain=True)
        # Same data, same seed → same metrics
        assert ev1.mae == ev2.mae

    def test_training_data_source_labeled_synthetic(self, trained_service):
        ev = trained_service.get_evaluation()
        assert ev.training_data_source == "SYNTHETIC"


# ── Evaluation Metrics Tests ──────────────────────────────────────────────────

class TestEvaluationMetrics:
    def test_mae_is_positive_float(self, trained_service):
        """MAE must be a non-negative number."""
        ev = trained_service.get_evaluation()
        assert ev.mae is not None
        assert ev.mae >= 0.0

    def test_rmse_is_positive_float(self, trained_service):
        ev = trained_service.get_evaluation()
        assert ev.rmse is not None
        assert ev.rmse >= 0.0

    def test_r2_is_plausible(self, trained_service):
        """R² should be > 0 on well-correlated synthetic data (not faked, just realistic)."""
        ev = trained_service.get_evaluation()
        assert ev.r2 is not None
        # R² CAN be negative in pathological cases, but for this correlated data it should be > 0.5
        assert ev.r2 > 0.50, f"R² too low: {ev.r2} — model may have data issue"

    def test_rmse_gte_mae(self, trained_service):
        """RMSE is always >= MAE (mathematical property)."""
        ev = trained_service.get_evaluation()
        assert ev.rmse >= ev.mae, f"RMSE={ev.rmse} < MAE={ev.mae} — impossible"

    def test_evaluation_note_present(self, trained_service):
        """Evaluation note must contain honest commentary."""
        ev = trained_service.get_evaluation()
        assert len(ev.note) > 20
        assert "SYNTHETIC" in ev.note


# ── Forecast Generation Tests ─────────────────────────────────────────────────

class TestForecastGeneration:
    def test_forecast_known_route_returns_result(self, trained_service):
        """Forecasting a known route should return a FreightForecast."""
        fc = trained_service.forecast(
            origin="Paradip", destination="Rotterdam",
            cargo_type="iron_ore", vessel_type="Panamax", distance_nm=4800.0
        )
        assert fc is not None
        assert isinstance(fc, FreightForecast)

    def test_forecast_has_all_horizon_values(self, trained_service):
        """Forecast must include 7d, 15d, 30d rate predictions."""
        fc = trained_service.forecast("Paradip", "Rotterdam", "iron_ore", "Panamax", 4800.0)
        assert fc.forecast_7d_usd_mt > 0
        assert fc.forecast_15d_usd_mt > 0
        assert fc.forecast_30d_usd_mt > 0

    def test_forecast_rate_is_positive(self, trained_service):
        """All forecast rates must be positive (floor applied)."""
        fc = trained_service.forecast("Paradip", "Rotterdam", "iron_ore", "Panamax", 4800.0)
        assert fc.current_rate_usd_mt > 0
        assert fc.forecast_30d_usd_mt >= 2.0  # floor is 2.0 USD/mt

    def test_forecast_direction_is_valid(self, trained_service):
        """Direction must be one of: up, down, stable."""
        fc = trained_service.forecast("Samarinda", "Shanghai", "coal", "Supramax", 2600.0)
        assert fc.forecast_direction in ("up", "down", "stable")

    def test_forecast_change_percent_matches_direction(self, trained_service):
        """change_percent and direction must be consistent."""
        fc = trained_service.forecast("Paradip", "Rotterdam", "iron_ore", "Panamax", 4800.0)
        if fc.forecast_direction == "up":
            assert fc.forecast_change_percent > 2.0
        elif fc.forecast_direction == "down":
            assert fc.forecast_change_percent < -2.0
        else:  # stable
            assert -2.0 <= fc.forecast_change_percent <= 2.0

    def test_forecast_data_source_is_synthetic(self, trained_service):
        """Forecast must declare SYNTHETIC data source — NEVER claim live."""
        fc = trained_service.forecast("Paradip", "Rotterdam", "iron_ore", "Panamax", 4800.0)
        assert fc.data_source == "SYNTHETIC"

    def test_forecast_disclaimer_present(self, trained_service):
        """Forecast must include a disclaimer."""
        fc = trained_service.forecast("Paradip", "Rotterdam", "iron_ore", "Panamax", 4800.0)
        assert len(fc.disclaimer) > 30

    def test_forecast_unknown_route_uses_model_fallback(self, trained_service):
        """Unknown route should still return a forecast using market-based prediction."""
        fc = trained_service.forecast(
            origin="Atlantis", destination="Timbuktu",
            cargo_type="iron_ore", vessel_type="Panamax", distance_nm=9999.0
        )
        assert fc is not None
        assert fc.current_rate_usd_mt > 0

    def test_forecast_unknown_vessel_type_does_not_crash(self, trained_service):
        """Unknown vessel type should not raise — use encoded fallback (0)."""
        fc = trained_service.forecast(
            "Paradip", "Rotterdam", "iron_ore", "GhostVessel", 4800.0
        )
        assert fc is not None

    def test_forecast_model_name_is_random_forest(self, trained_service):
        fc = trained_service.forecast("Paradip", "Rotterdam", "iron_ore", "Panamax", 4800.0)
        assert fc.model_name == "RandomForestRegressor"

    @pytest.mark.parametrize("cargo_type", ["iron_ore", "coal", "grain"])
    def test_forecast_multiple_cargo_types(self, trained_service, cargo_type):
        """Forecast should work for all major cargo types."""
        fc = trained_service.forecast(
            "Paradip", "Rotterdam", cargo_type, "Panamax", 4800.0
        )
        assert fc is not None
        assert fc.current_rate_usd_mt > 0


# ── Integration: End-to-End Pipeline ─────────────────────────────────────────

class TestEndToEndPipeline:
    def test_full_analysis_includes_market_intelligence(self):
        """analyze_shipping_request should now include market_intelligence field."""
        from app.main import analyze_shipping_request
        result = analyze_shipping_request("iron_ore", 75000, "Paradip", "Rotterdam")
        assert "market_intelligence" in result
        mi = result["market_intelligence"]
        assert mi is not None
        assert "market_snapshot" in mi
        assert "freight_forecast" in mi
        assert "model_evaluation" in mi

    def test_market_snapshot_in_response_has_bdi(self):
        """Market snapshot in full response must contain BDI."""
        from app.main import analyze_shipping_request
        result = analyze_shipping_request("coal", 65000, "Samarinda", "Gangavaram")
        bdi = result["market_intelligence"]["market_snapshot"]["bdi"]
        assert bdi["current_value"] > 0
        assert bdi["data_source"] == "SYNTHETIC"

    def test_analysis_still_works_without_market_failure(self):
        """Core analysis fields must be present even if market intelligence fails."""
        from app.main import analyze_shipping_request
        result = analyze_shipping_request("grain", 30000, "Baltimore", "Rotterdam")
        # Core pipeline must always work
        assert "recommendation" in result
        assert "vessel_analysis" in result
        assert "route_estimate" in result
        assert "data_quality" in result

    def test_disclaimer_never_claims_live_data(self):
        """Market intelligence disclaimer must contain SYNTHETIC and never 'LIVE'."""
        from app.main import analyze_shipping_request
        result = analyze_shipping_request("iron_ore", 75000, "Paradip", "Rotterdam")
        mi = result["market_intelligence"]
        disclaimer = mi["market_snapshot"]["disclaimer"]
        assert "SYNTHETIC" in disclaimer
        assert "LIVE" not in disclaimer
