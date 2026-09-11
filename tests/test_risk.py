"""
Tests for RiskService — weather and marine risk scoring.
0 = very low risk, 100 = very high risk. DATA: SYNTHETIC.
"""
import pytest
from app.services.risk_service import RiskService, _classify_risk, _region
from app.models.operations import RiskAssessment, WeatherRisk, MarineRisk

@pytest.fixture(scope="module")
def svc():
    return RiskService()

class TestRiskClassification:
    def test_low(self):              assert _classify_risk(10.0)  == "LOW"
    def test_low_moderate(self):     assert _classify_risk(30.0)  == "LOW-MODERATE"
    def test_moderate(self):         assert _classify_risk(50.0)  == "MODERATE"
    def test_high(self):             assert _classify_risk(68.0)  == "HIGH"
    def test_very_high(self):        assert _classify_risk(80.0)  == "VERY HIGH"

class TestRegionMapping:
    def test_paradip_is_bay_of_bengal(self):
        assert _region("Paradip") == "bay_of_bengal"
    def test_rotterdam_is_north_atlantic(self):
        assert _region("Rotterdam") == "north_atlantic"
    def test_singapore_is_south_china_sea(self):
        assert _region("Singapore") == "south_china_sea"
    def test_unknown_port_is_generic(self):
        assert _region("Atlantis") == "generic"

class TestRiskAssessmentStructure:
    def test_returns_risk_assessment(self, svc):
        r = svc.assess("Paradip", "Rotterdam")
        assert isinstance(r, RiskAssessment)

    def test_overall_score_in_range(self, svc):
        r = svc.assess("Paradip", "Rotterdam")
        assert 0.0 <= r.overall_risk_score <= 100.0

    def test_weather_risk_score_in_range(self, svc):
        r = svc.assess("Paradip", "Rotterdam")
        assert 0.0 <= r.weather_risk.weather_risk_score <= 100.0

    def test_marine_risk_score_in_range(self, svc):
        r = svc.assess("Paradip", "Rotterdam")
        assert 0.0 <= r.marine_risk.marine_risk_score <= 100.0

    def test_risk_level_is_valid(self, svc):
        r = svc.assess("Paradip", "Rotterdam")
        assert r.risk_level in {"LOW","LOW-MODERATE","MODERATE","HIGH","VERY HIGH"}

    def test_key_hazards_is_list(self, svc):
        r = svc.assess("Paradip", "Rotterdam")
        assert isinstance(r.key_hazards, list)
        assert len(r.key_hazards) >= 1

    def test_route_field_contains_ports(self, svc):
        r = svc.assess("Paradip", "Rotterdam")
        assert "Paradip" in r.route
        assert "Rotterdam" in r.route

    def test_data_source_is_synthetic(self, svc):
        r = svc.assess("Paradip", "Rotterdam")
        assert r.data_source == "SYNTHETIC"

    def test_formula_note_present(self, svc):
        r = svc.assess("Paradip", "Rotterdam")
        assert len(r.formula_note) > 20

class TestRiskComparisons:
    def test_bay_of_bengal_riskier_than_generic(self, svc):
        """Bay of Bengal route should score higher risk than two unknown generic ports."""
        r_high = svc.assess("Paradip", "Haldia")
        r_low  = svc.assess("Port_Alpha", "Port_Beta")
        assert r_high.overall_risk_score >= r_low.overall_risk_score

    def test_unknown_ports_do_not_crash(self, svc):
        r = svc.assess("NonexistentPort1", "NonexistentPort2")
        assert r is not None
        assert 0 <= r.overall_risk_score <= 100

    @pytest.mark.parametrize("origin,dest", [
        ("Paradip",    "Rotterdam"),
        ("Samarinda",  "Shanghai"),
        ("Port Hedland","Qingdao"),
        ("Baltimore",  "Rotterdam"),
    ])
    def test_various_routes_return_valid_result(self, svc, origin, dest):
        r = svc.assess(origin, dest)
        assert r.overall_risk_score >= 0
        assert r.risk_level in {"LOW","LOW-MODERATE","MODERATE","HIGH","VERY HIGH"}

class TestWeatherAndMarineComponents:
    def test_wind_speed_non_negative(self, svc):
        r = svc.assess("Paradip", "Rotterdam")
        assert r.weather_risk.wind_speed_bft >= 0

    def test_wave_height_non_negative(self, svc):
        r = svc.assess("Paradip", "Rotterdam")
        assert r.weather_risk.wave_height_m >= 0

    def test_storm_probability_in_range(self, svc):
        r = svc.assess("Paradip", "Rotterdam")
        assert 0 <= r.weather_risk.storm_probability_pct <= 100

    def test_cyclone_risk_in_range(self, svc):
        r = svc.assess("Paradip", "Rotterdam")
        assert 0 <= r.marine_risk.cyclone_risk_pct <= 100

    def test_env_sensitivity_in_range(self, svc):
        r = svc.assess("Paradip", "Rotterdam")
        assert 0 <= r.marine_risk.environmental_sensitivity <= 100

    def test_sea_state_is_string(self, svc):
        r = svc.assess("Paradip", "Rotterdam")
        assert isinstance(r.marine_risk.sea_state, str)
        assert len(r.marine_risk.sea_state) > 0
