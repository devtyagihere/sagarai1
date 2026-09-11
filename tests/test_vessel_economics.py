"""
Tests for VesselEconomicsService — voyage cost and vessel comparison.

Formulas:
  voyage_cost = daily_rate_usd × voyage_days
  cost_per_mt = voyage_cost / cargo_quantity_tonnes

Incompatible vessels must be excluded from cheapest_feasible_vessel.
DATA: SYNTHETIC daily rates.
"""
import pytest
from app.services.vessel_economics import VesselEconomicsService
from app.models.operations import VesselEconomicsResult, VesselEconomicsItem
from app.main import analyze_shipping_request
from app.utils.constants import FeasibilityStatus

@pytest.fixture(scope="module")
def svc():
    return VesselEconomicsService()

@pytest.fixture(scope="module")
def iron_ore_analysis():
    """Full analysis for a standard iron ore route."""
    return analyze_shipping_request("iron_ore", 75000, "Paradip", "Rotterdam", 30)

@pytest.fixture(scope="module")
def steel_coil_analysis():
    """Steel coils — Capesize and Panamax are incompatible."""
    return analyze_shipping_request("steel_coils", 12000, "Visakhapatnam", "Rotterdam")

class TestFormulas:
    def test_voyage_cost_formula(self, svc):
        """voyage_cost = daily_rate × voyage_days"""
        from app.services.data_loader import default_data_loader
        from app.services.feasibility import FeasibilityEngine
        from app.services.cargo_service import CargoService
        from app.models.request import ShippingRequest
        from app.services.scoring import ScoringEngine

        result = analyze_shipping_request("iron_ore", 75000, "Paradip", "Rotterdam")
        econ = result["vessel_economics"]
        voyage_days = econ["voyage_days"]
        for item in econ["comparison"]:
            expected_cost = round(item["daily_rate_usd"] * voyage_days, 2)
            assert abs(item["voyage_cost_usd"] - expected_cost) < 0.1, (
                f"{item['vessel_class']}: expected {expected_cost}, got {item['voyage_cost_usd']}"
            )

    def test_cost_per_mt_formula(self, iron_ore_analysis):
        """cost_per_mt = voyage_cost / cargo_quantity_tonnes"""
        econ = iron_ore_analysis["vessel_economics"]
        cargo_qty = econ["cargo_quantity_tonnes"]
        for item in econ["comparison"]:
            expected = round(item["voyage_cost_usd"] / cargo_qty, 4)
            assert abs(item["cost_per_mt_usd"] - expected) < 0.01, (
                f"{item['vessel_class']}: expected {expected}, got {item['cost_per_mt_usd']}"
            )

class TestVesselComparison:
    def test_comparison_contains_all_vessel_classes(self, iron_ore_analysis):
        econ = iron_ore_analysis["vessel_economics"]
        classes = {i["vessel_class"].lower() for i in econ["comparison"]}
        expected = {"handysize","handymax","supramax","panamax","capesize","mini-bulker"}
        assert expected == classes

    def test_feasible_vessels_listed_before_infeasible(self, iron_ore_analysis):
        econ = iron_ore_analysis["vessel_economics"]
        order_map = {"feasible": 0, "conditionally_feasible": 1, "not_feasible": 2}
        statuses = [order_map.get(i["feasibility_status"], 9) for i in econ["comparison"]]
        assert statuses == sorted(statuses), "Feasible vessels must appear before infeasible"

    def test_cheapest_feasible_has_lowest_cost_per_mt(self, iron_ore_analysis):
        econ = iron_ore_analysis["vessel_economics"]
        cheapest_name = econ["cheapest_feasible_vessel"]
        if cheapest_name is None:
            pytest.skip("No feasible vessel found")
        feasible = [i for i in econ["comparison"]
                    if i["feasibility_status"] == "feasible"]
        min_cost = min(i["cost_per_mt_usd"] for i in feasible)
        cheapest_item = next(i for i in feasible if i["vessel_class"] == cheapest_name)
        assert cheapest_item["cost_per_mt_usd"] == min_cost

    def test_daily_rates_positive(self, iron_ore_analysis):
        econ = iron_ore_analysis["vessel_economics"]
        for item in econ["comparison"]:
            assert item["daily_rate_usd"] > 0

    def test_voyage_cost_positive(self, iron_ore_analysis):
        econ = iron_ore_analysis["vessel_economics"]
        for item in econ["comparison"]:
            assert item["voyage_cost_usd"] > 0

    def test_recommended_vessel_flagged(self, iron_ore_analysis):
        econ = iron_ore_analysis["vessel_economics"]
        rec = iron_ore_analysis["recommendation"]["recommended_vessel"]
        if rec:
            flagged = [i for i in econ["comparison"] if i["is_recommended"]]
            assert len(flagged) == 1
            assert flagged[0]["vessel_class"].lower() == rec.lower()

class TestIncompatibleVesselExclusion:
    def test_capesize_not_feasible_for_steel_coils(self, steel_coil_analysis):
        """Capesize does not support steel_coils — must appear as NOT_FEASIBLE."""
        econ = steel_coil_analysis["vessel_economics"]
        capesize = next(
            i for i in econ["comparison"] if i["vessel_class"].lower() == "capesize"
        )
        assert capesize["feasibility_status"] == "not_feasible"

    def test_panamax_not_feasible_for_steel_coils(self, steel_coil_analysis):
        """Panamax does not support steel_coils — must appear as NOT_FEASIBLE."""
        econ = steel_coil_analysis["vessel_economics"]
        panamax = next(
            i for i in econ["comparison"] if i["vessel_class"].lower() == "panamax"
        )
        assert panamax["feasibility_status"] == "not_feasible"

    def test_cheapest_feasible_excludes_incompatible(self, steel_coil_analysis):
        """cheapest_feasible_vessel must not be Capesize or Panamax for steel_coils."""
        econ = steel_coil_analysis["vessel_economics"]
        cheapest = econ.get("cheapest_feasible_vessel")
        if cheapest:
            assert cheapest.lower() not in {"capesize", "panamax"}

    def test_incompatible_cargo_score_is_zero(self, steel_coil_analysis):
        """After scoring fix: Capesize cargo_compatibility must be 0 for steel_coils."""
        vessel_analysis = steel_coil_analysis["vessel_analysis"]
        capesize = next(
            v for v in vessel_analysis if v["vessel_class"].lower() == "capesize"
        )
        if capesize.get("score_breakdown"):
            assert capesize["score_breakdown"]["cargo_compatibility"] == 0.0

class TestEdgeCases:
    def test_zero_voyage_days_returns_empty_comparison(self, svc):
        result = svc.compute([], voyage_days=0, cargo_quantity_tonnes=50000)
        assert result.comparison == []

    def test_zero_cargo_returns_empty_comparison(self, svc):
        result = svc.compute([], voyage_days=14, cargo_quantity_tonnes=0)
        assert result.comparison == []

    def test_economics_in_full_response(self, iron_ore_analysis):
        """vessel_economics key must be present in full analyze response."""
        assert "vessel_economics" in iron_ore_analysis
        assert iron_ore_analysis["vessel_economics"] is not None

    def test_formula_note_present(self, iron_ore_analysis):
        econ = iron_ore_analysis["vessel_economics"]
        assert "voyage_cost" in econ["formula_note"]
        assert "cost_per_mt" in econ["formula_note"]

class TestPhase3PipelineIntegration:
    def test_full_response_has_port_operations(self):
        result = analyze_shipping_request("iron_ore", 75000, "Paradip", "Rotterdam")
        assert "port_operations" in result
        assert result["port_operations"] is not None

    def test_full_response_has_risk_assessment(self):
        result = analyze_shipping_request("iron_ore", 75000, "Paradip", "Rotterdam")
        assert "risk_assessment" in result
        assert result["risk_assessment"] is not None

    def test_full_response_has_vessel_economics(self):
        result = analyze_shipping_request("iron_ore", 75000, "Paradip", "Rotterdam")
        assert "vessel_economics" in result
        assert result["vessel_economics"] is not None

    def test_port_operations_has_origin_and_destination(self):
        result = analyze_shipping_request("coal", 60000, "Samarinda", "Qingdao")
        po = result["port_operations"]
        assert po["origin"] is not None
        assert po["destination"] is not None

    def test_risk_assessment_score_non_negative(self):
        result = analyze_shipping_request("grain", 30000, "Baltimore", "Rotterdam")
        ra = result["risk_assessment"]
        assert ra["overall_risk_score"] >= 0

    def test_core_fields_always_present(self):
        """Core pipeline must never be broken by Phase 3."""
        result = analyze_shipping_request("iron_ore", 75000, "Paradip", "Rotterdam")
        for key in ("recommendation","vessel_analysis","route_estimate","data_quality"):
            assert key in result
