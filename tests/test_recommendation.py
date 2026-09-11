"""Unit tests for vessel recommendation engine and multi-factor scoring."""

import pytest
from app.main import analyze_shipping_request
from app.services.data_loader import default_data_loader
from app.utils.constants import RecommendationConfidence, RecommendationStatus


@pytest.fixture(autouse=True)
def load_data():
    default_data_loader.load_all()


def test_standard_panamax_recommendation():
    """Verify standard 75,000t iron ore parcel from Paradip to Rotterdam selects Panamax."""
    response = analyze_shipping_request(
        cargo_type="iron_ore",
        cargo_quantity_tonnes=75000,
        origin_port="Paradip",
        destination_port="Rotterdam",
        shipping_deadline_days=30,
    )
    rec = response["recommendation"]
    assert rec["recommended_vessel"] == "Panamax"
    assert rec["status"] == RecommendationStatus.RECOMMENDED
    assert rec["recommendation_confidence"] == RecommendationConfidence.HIGH
    assert len(rec["reasoning"]) > 0

    # Verify score exists and is transparent
    panamax_analysis = next(v for v in response["vessel_analysis"] if v["vessel_class"] == "Panamax")
    assert panamax_analysis["score"] is not None
    assert panamax_analysis["score"] > 80.0
    assert panamax_analysis["score_breakdown"]["capacity_utilization"] > 0
    assert panamax_analysis["score_breakdown"]["port_confidence"] > 0


def test_capesize_deepwater_recommendation():
    """Verify 160,000t coal shipment to deepwater Gangavaram port selects Capesize."""
    response = analyze_shipping_request(
        cargo_type="coal",
        cargo_quantity_tonnes=160000,
        origin_port="Port Hedland",
        destination_port="Gangavaram",
    )
    rec = response["recommendation"]
    assert rec["recommended_vessel"] == "Capesize"
    assert rec["status"] == RecommendationStatus.RECOMMENDED


def test_breakbulk_steel_geared_recommendation():
    """Verify 25,000t steel coils selects geared Handysize vessel."""
    response = analyze_shipping_request(
        cargo_type="steel_coils",
        cargo_quantity_tonnes=25000,
        origin_port="Dhamra",
        destination_port="Singapore",
    )
    rec = response["recommendation"]
    assert rec["recommended_vessel"] in ("Handysize", "Handymax", "Supramax")
    assert rec["status"] == RecommendationStatus.RECOMMENDED

    # Verify gearless Panamax and Capesize are rejected
    panamax = next(v for v in response["vessel_analysis"] if v["vessel_class"] == "Panamax")
    assert panamax["feasibility_status"] == "not_feasible"
    assert any("geared" in r for r in panamax["rejection_reasons"])


def test_no_feasible_vessel_oversized_cargo():
    """Verify extremely oversized parcel (300,000t) returns NO_FEASIBLE_VESSEL."""
    response = analyze_shipping_request(
        cargo_type="iron_ore",
        cargo_quantity_tonnes=300000,
        origin_port="Port Hedland",
        destination_port="Rotterdam",
    )
    rec = response["recommendation"]
    assert rec["recommended_vessel"] is None
    assert rec["status"] == RecommendationStatus.NO_FEASIBLE_VESSEL
    assert rec["recommendation_confidence"] == RecommendationConfidence.NONE
    assert rec["message"] is not None


def test_conditionally_feasible_port_data():
    """Verify recommendation confidence drops when port data is unverified or estimated."""
    response = analyze_shipping_request(
        cargo_type="grain",
        cargo_quantity_tonnes=30000,
        origin_port="Port_Alpha",
        destination_port="Port_Beta",
    )
    rec = response["recommendation"]
    assert rec["status"] == RecommendationStatus.CONDITIONALLY_RECOMMENDED
    assert rec["recommendation_confidence"] == RecommendationConfidence.MEDIUM
    assert response["data_quality"]["overall_status"] != "fully_verified"
