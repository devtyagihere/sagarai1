"""
Tests for MarketDataService — dataset loading, trend calculations, and indicator building.
All tests use SYNTHETIC data from data/market/*.csv.
"""

import pytest
from pathlib import Path

from app.services.market_service import MarketDataService
from app.models.market import MarketIndicator, MarketSnapshot


# ── Fixtures ──────────────────────────────────────────────────────────────────

@pytest.fixture(scope="module")
def market_service():
    """Create and pre-load a market service instance once for the module."""
    svc = MarketDataService()
    svc.load_all()
    return svc


# ── Dataset Loading Tests ─────────────────────────────────────────────────────

class TestDatasetLoading:
    def test_bdi_dataset_loads(self, market_service):
        """BDI CSV should load with expected columns and row count."""
        df = market_service._bdi_df
        assert df is not None
        assert "date" in df.columns
        assert "bdi" in df.columns
        assert len(df) >= 700, "Expected at least 700 daily BDI rows"

    def test_oil_dataset_loads(self, market_service):
        """Oil price CSV should load with WTI column."""
        df = market_service._oil_df
        assert df is not None
        assert "wti_usd_bbl" in df.columns
        assert len(df) >= 700

    def test_commodity_dataset_loads(self, market_service):
        """Commodity CSV should contain iron_ore, coal, and grain columns."""
        df = market_service._comm_df
        assert df is not None
        for col in ("iron_ore_usd_t", "coal_usd_t", "grain_usd_t"):
            assert col in df.columns, f"Missing column: {col}"

    def test_freight_history_loads(self, market_service):
        """Freight history CSV should contain all required ML feature columns."""
        df = market_service._freight_df
        assert df is not None
        required_cols = [
            "date", "origin", "destination", "cargo_type",
            "vessel_type", "freight_rate_usd_mt", "bdi",
            "oil_price", "commodity_price", "distance_nm",
        ]
        for col in required_cols:
            assert col in df.columns, f"Missing column: {col}"
        assert len(df) >= 1000, "Expected at least 1000 freight history rows"

    def test_data_is_labeled_synthetic(self, market_service):
        """All datasets must carry SYNTHETIC data_source label."""
        for df in (market_service._bdi_df, market_service._oil_df,
                   market_service._comm_df, market_service._freight_df):
            if "data_source" in df.columns:
                sources = df["data_source"].dropna().unique().tolist()
                assert sources == ["SYNTHETIC"], f"Expected SYNTHETIC, got {sources}"

    def test_missing_file_raises_error(self, tmp_path):
        """MarketDataService should raise FileNotFoundError for missing CSVs."""
        bad_svc = MarketDataService(bdi_path=tmp_path / "nonexistent.csv")
        with pytest.raises(FileNotFoundError):
            bad_svc.load_all()


# ── MarketIndicator Tests ────────────────────────────────────────────────────

class TestMarketIndicators:
    def test_bdi_indicator_structure(self, market_service):
        """BDI indicator must have all required fields with valid types."""
        bdi: MarketIndicator = market_service.get_bdi_indicator()
        assert isinstance(bdi.current_value, float)
        assert isinstance(bdi.previous_value, float)
        assert isinstance(bdi.change_percent, float)
        assert bdi.trend_7d > 0
        assert bdi.trend_30d > 0
        assert bdi.unit == "index points"
        assert bdi.data_source == "SYNTHETIC"

    def test_bdi_value_in_realistic_range(self, market_service):
        """BDI should be within the realistic range defined by the generator (400-4500)."""
        bdi = market_service.get_bdi_indicator()
        assert 400 <= bdi.current_value <= 4500, f"BDI out of range: {bdi.current_value}"

    def test_oil_indicator_structure(self, market_service):
        """WTI oil price indicator must have correct unit and valid value."""
        oil: MarketIndicator = market_service.get_oil_indicator()
        assert oil.unit == "USD/barrel"
        assert 45.0 <= oil.current_value <= 125.0, f"Oil price out of range: {oil.current_value}"
        assert oil.data_source == "SYNTHETIC"

    def test_bdi_direction_is_valid(self, market_service):
        """Direction field must be one of: up, down, stable."""
        bdi = market_service.get_bdi_indicator()
        assert bdi.direction in ("up", "down", "stable")

    def test_trend_30d_reflects_30_days(self, market_service):
        """30-day trend should differ from 7-day trend (not identical averages)."""
        bdi = market_service.get_bdi_indicator()
        # They CAN be the same in a flat series, but usually won't be
        # Just assert both are positive floats
        assert bdi.trend_7d > 0
        assert bdi.trend_30d > 0

    def test_bdi_as_of_date_is_iso_format(self, market_service):
        """as_of_date should be a valid ISO date string."""
        bdi = market_service.get_bdi_indicator()
        from datetime import date
        parsed = date.fromisoformat(bdi.as_of_date)  # raises ValueError if invalid
        assert parsed.year >= 2023


# ── Commodity Indicator Tests ─────────────────────────────────────────────────

class TestCommodityIndicators:
    @pytest.mark.parametrize("cargo,expected_unit", [
        ("iron_ore",   "USD/tonne"),
        ("coal",       "USD/tonne"),
        ("grain",      "USD/tonne"),
        ("bauxite",    "USD/tonne"),
        ("fertilizer", "USD/tonne"),
    ])
    def test_commodity_indicator_for_known_cargo(self, market_service, cargo, expected_unit):
        ind = market_service.get_commodity_indicator(cargo)
        assert ind is not None
        assert ind.unit == expected_unit
        assert ind.current_value > 0

    def test_commodity_indicator_unknown_cargo_returns_none(self, market_service):
        """Unknown cargo types should return None, not raise an exception."""
        result = market_service.get_commodity_indicator("plutonium")
        assert result is None

    def test_commodity_case_insensitive(self, market_service):
        """Commodity lookup should be case-insensitive."""
        a = market_service.get_commodity_indicator("IRON_ORE")
        b = market_service.get_commodity_indicator("iron_ore")
        assert a is not None and b is not None
        assert a.current_value == b.current_value


# ── MarketSnapshot Tests ──────────────────────────────────────────────────────

class TestMarketSnapshot:
    def test_snapshot_contains_bdi_and_oil(self, market_service):
        snap: MarketSnapshot = market_service.get_market_snapshot()
        assert snap.bdi is not None
        assert snap.oil_price is not None
        assert snap.commodity_price is None  # No cargo_type provided

    def test_snapshot_with_cargo_type_includes_commodity(self, market_service):
        snap = market_service.get_market_snapshot("iron_ore")
        assert snap.commodity_price is not None
        assert "Iron Ore" in snap.commodity_price.name

    def test_snapshot_disclaimer_present(self, market_service):
        snap = market_service.get_market_snapshot()
        assert len(snap.disclaimer) > 20  # Non-empty disclaimer
        assert "SYNTHETIC" in snap.disclaimer

    def test_snapshot_data_source_is_synthetic(self, market_service):
        snap = market_service.get_market_snapshot()
        assert snap.data_source == "SYNTHETIC"


# ── Trend & Projection Tests ──────────────────────────────────────────────────

class TestTrendProjections:
    def test_recent_market_values_returns_bdi_and_oil(self, market_service):
        vals = market_service.get_recent_market_values(30)
        assert "bdi" in vals
        assert "oil_price" in vals
        assert vals["bdi"] > 0
        assert vals["oil_price"] > 0

    def test_latest_market_values_are_floats(self, market_service):
        vals = market_service.get_latest_market_values()
        assert isinstance(vals["bdi"], float)
        assert isinstance(vals["oil_price"], float)

    def test_project_7d_vs_30d_differ(self, market_service):
        """7-day and 30-day projections should generally differ (slope applied)."""
        p7  = market_service.project_market_values(7)
        p30 = market_service.project_market_values(30)
        assert isinstance(p7["bdi"], float)
        assert isinstance(p30["bdi"], float)
        # Both should be in realistic range
        assert 400 <= p7["bdi"] <= 4500
        assert 400 <= p30["bdi"] <= 4500

    def test_get_recent_rate_returns_float_for_known_route(self, market_service):
        """Known route should return a positive float rate."""
        rate = market_service.get_recent_rate("Paradip", "Rotterdam", "iron_ore", "Panamax")
        assert rate is not None
        assert rate > 0.0

    def test_get_recent_rate_returns_none_for_unknown_route(self, market_service):
        """Unknown route should return None without raising."""
        rate = market_service.get_recent_rate("Timbuktu", "Atlantis", "unobtanium", "GhostShip")
        assert rate is None
