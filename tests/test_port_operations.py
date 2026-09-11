"""
Tests for PortOperationsService — congestion scoring and classification.
DATA: SYNTHETIC — labeled throughout.
"""
import pytest
from app.services.port_operations import PortOperationsService, _classify
from app.models.operations import PortCongestion, PortOperationsResult

@pytest.fixture(scope="module")
def svc():
    s = PortOperationsService()
    return s

class TestCongestionClassification:
    def test_low(self):         assert _classify(10.0) == "LOW"
    def test_low_moderate(self):assert _classify(35.0) == "LOW-MODERATE"
    def test_moderate(self):    assert _classify(55.0) == "MODERATE"
    def test_high(self):        assert _classify(72.0) == "HIGH"
    def test_very_high(self):   assert _classify(85.0) == "VERY HIGH"
    def test_boundary_low(self):assert _classify(25.0) == "LOW-MODERATE"
    def test_boundary_very_high(self): assert _classify(80.0) == "VERY HIGH"

class TestDatasetLoading:
    def test_known_port_returns_congestion(self, svc):
        c = svc.get_port_congestion("Paradip")
        assert c is not None
        assert isinstance(c, PortCongestion)

    def test_unknown_port_returns_none(self, svc):
        c = svc.get_port_congestion("Atlantis")
        assert c is None

    def test_case_insensitive_lookup(self, svc):
        c1 = svc.get_port_congestion("paradip")
        c2 = svc.get_port_congestion("PARADIP")
        assert c1 is not None and c2 is not None
        assert c1.congestion_score == c2.congestion_score

class TestPortCongestionFields:
    def test_score_in_range(self, svc):
        c = svc.get_port_congestion("Rotterdam")
        assert 0.0 <= c.congestion_score <= 100.0

    def test_vessels_working_positive(self, svc):
        c = svc.get_port_congestion("Shanghai")
        assert c.vessels_working >= 1

    def test_vessels_waiting_non_negative(self, svc):
        c = svc.get_port_congestion("Qingdao")
        assert c.vessels_waiting >= 0

    def test_forecast_fields_present(self, svc):
        c = svc.get_port_congestion("Port Hedland")
        assert c.congestion_forecast_7d  >= 0
        assert c.congestion_forecast_15d >= 0
        assert c.congestion_forecast_30d >= 0

    def test_data_source_is_synthetic(self, svc):
        c = svc.get_port_congestion("Visakhapatnam")
        assert c.data_source == "SYNTHETIC"

    def test_formula_used_field_populated(self, svc):
        c = svc.get_port_congestion("Haldia")
        assert len(c.formula_used) > 10

    def test_congestion_level_consistent_with_score(self, svc):
        c = svc.get_port_congestion("Paradip")
        expected = _classify(c.congestion_score)
        assert c.congestion_level == expected

class TestPortOperationsResult:
    def test_both_ports_found(self, svc):
        r = svc.get_port_operations_result("Paradip", "Rotterdam")
        assert r.origin is not None
        assert r.destination is not None

    def test_combined_delay_risk_is_valid(self, svc):
        r = svc.get_port_operations_result("Paradip", "Rotterdam")
        valid = {"LOW","LOW-MODERATE","MODERATE","HIGH","VERY HIGH"}
        assert r.combined_delay_risk in valid

    def test_combined_is_worst_of_two(self, svc):
        """Combined risk should be >= each individual port level."""
        order = ["LOW","LOW-MODERATE","MODERATE","HIGH","VERY HIGH"]
        r = svc.get_port_operations_result("Gopalpur", "Shanghai")
        ol = order.index(r.origin.congestion_level if r.origin else "LOW")
        dl = order.index(r.destination.congestion_level if r.destination else "LOW")
        cl = order.index(r.combined_delay_risk)
        assert cl == max(ol, dl)

    def test_missing_file_raises_error(self, tmp_path):
        bad_svc = PortOperationsService(path=tmp_path / "nofile.csv")
        with pytest.raises(FileNotFoundError):
            bad_svc.get_port_congestion("Paradip")
