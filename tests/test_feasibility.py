"""Unit tests for vessel feasibility engine and port physical constraints."""

import pytest
from app.models.port import Port
from app.models.request import ShippingRequest
from app.models.vessel import Vessel
from app.services.cargo_service import CargoService
from app.services.feasibility import FeasibilityEngine
from app.utils.constants import DataQualityStatus, FeasibilityStatus


@pytest.fixture
def cargo_service():
    return CargoService()


@pytest.fixture
def feasibility_engine(cargo_service):
    return FeasibilityEngine(cargo_service)


@pytest.fixture
def handysize_vessel():
    return Vessel(
        vessel_class="Handysize",
        min_capacity_tonnes=15000,
        max_capacity_tonnes=39999,
        typical_draft_m=10.0,
        typical_length_m=180.0,
        typical_beam_m=28.4,
        avg_speed_knots=13.0,
        supported_cargo=["iron_ore", "coal", "grain", "steel_coils", "steel_plates", "steel_products"],
        data_status=DataQualityStatus.VERIFIED,
        source="BIMCO Standard Handysize",
    )


@pytest.fixture
def panamax_vessel():
    return Vessel(
        vessel_class="Panamax",
        min_capacity_tonnes=65000,
        max_capacity_tonnes=84999,
        typical_draft_m=14.5,
        typical_length_m=229.0,
        typical_beam_m=32.3,
        avg_speed_knots=14.0,
        supported_cargo=["iron_ore", "coal", "grain", "bauxite"],
        data_status=DataQualityStatus.VERIFIED,
        source="Baltic Exchange Panamax",
    )


@pytest.fixture
def capesize_vessel():
    return Vessel(
        vessel_class="Capesize",
        min_capacity_tonnes=100000,
        max_capacity_tonnes=200000,
        typical_draft_m=18.2,
        typical_length_m=292.0,
        typical_beam_m=45.0,
        avg_speed_knots=14.5,
        supported_cargo=["iron_ore", "coal", "bauxite"],
        data_status=DataQualityStatus.VERIFIED,
        source="Baltic Exchange Capesize",
    )


@pytest.fixture
def paradip_port():
    return Port(
        port_name="Paradip",
        country="India",
        latitude=20.2644,
        longitude=86.6715,
        max_draft_m=17.1,
        max_length_m=260.0,
        max_beam_m=48.0,
        data_status=DataQualityStatus.VERIFIED,
        source="Paradip Port Authority",
    )


@pytest.fixture
def rotterdam_port():
    return Port(
        port_name="Rotterdam",
        country="Netherlands",
        latitude=51.9244,
        longitude=4.4777,
        max_draft_m=24.0,
        max_length_m=400.0,
        max_beam_m=60.0,
        data_status=DataQualityStatus.VERIFIED,
        source="Port of Rotterdam Authority",
    )


@pytest.fixture
def haldia_port():
    return Port(
        port_name="Haldia",
        country="India",
        latitude=22.0257,
        longitude=88.0645,
        max_draft_m=8.5,
        max_length_m=195.0,
        max_beam_m=32.2,
        data_status=DataQualityStatus.VERIFIED,
        source="Syama Prasad Mookerjee Port",
    )


def test_capacity_fits(feasibility_engine, panamax_vessel, paradip_port, rotterdam_port):
    """Test when cargo parcel cleanly fits within vessel payload limits."""
    req = ShippingRequest(
        cargo_type="iron_ore",
        cargo_quantity_tonnes=75000,
        origin_port="Paradip",
        destination_port="Rotterdam",
    )
    result = feasibility_engine.evaluate_vessel(panamax_vessel, req, paradip_port, rotterdam_port)
    assert result.feasibility_status == FeasibilityStatus.FEASIBLE
    assert result.checks["capacity"] is True
    assert result.capacity_utilization == pytest.approx(75000 / 84999, rel=1e-3)
    assert len(result.rejection_reasons) == 0


def test_capacity_exceeds(feasibility_engine, handysize_vessel, paradip_port, rotterdam_port):
    """Test when cargo parcel exceeds maximum deadweight capacity."""
    req = ShippingRequest(
        cargo_type="iron_ore",
        cargo_quantity_tonnes=75000,
        origin_port="Paradip",
        destination_port="Rotterdam",
    )
    result = feasibility_engine.evaluate_vessel(handysize_vessel, req, paradip_port, rotterdam_port)
    assert result.feasibility_status == FeasibilityStatus.NOT_FEASIBLE
    assert result.checks["capacity"] is False
    assert any("Insufficient cargo capacity" in r for r in result.rejection_reasons)


def test_low_utilization_warning(feasibility_engine, capesize_vessel, paradip_port, rotterdam_port):
    """Test low capacity utilization generates warning but doesn't reject by default."""
    req = ShippingRequest(
        cargo_type="iron_ore",
        cargo_quantity_tonnes=40000,
        origin_port="Paradip",
        destination_port="Rotterdam",
    )
    result = feasibility_engine.evaluate_vessel(capesize_vessel, req, paradip_port, rotterdam_port)
    # Capesize length is 292m, Paradip max length is 260m -> will fail length check
    assert result.checks["capacity"] is True
    assert any("Low capacity utilization" in w for w in result.warnings)


def test_draft_incompatible(feasibility_engine, panamax_vessel, haldia_port, rotterdam_port):
    """Test vessel draft exceeding shallow port max draft (Haldia 8.5m vs Panamax 14.5m)."""
    req = ShippingRequest(
        cargo_type="coal",
        cargo_quantity_tonnes=70000,
        origin_port="Haldia",
        destination_port="Rotterdam",
    )
    result = feasibility_engine.evaluate_vessel(panamax_vessel, req, haldia_port, rotterdam_port)
    assert result.feasibility_status == FeasibilityStatus.NOT_FEASIBLE
    assert result.checks["origin_draft"] is False
    assert any("Draft restriction at origin" in r for r in result.rejection_reasons)


def test_length_incompatible(feasibility_engine, capesize_vessel, paradip_port, rotterdam_port):
    """Test Capesize length (292m) exceeding Paradip max length (260m)."""
    req = ShippingRequest(
        cargo_type="iron_ore",
        cargo_quantity_tonnes=120000,
        origin_port="Paradip",
        destination_port="Rotterdam",
    )
    result = feasibility_engine.evaluate_vessel(capesize_vessel, req, paradip_port, rotterdam_port)
    assert result.feasibility_status == FeasibilityStatus.NOT_FEASIBLE
    assert result.checks["origin_length"] is False
    assert any("Length restriction at origin" in r for r in result.rejection_reasons)


def test_missing_port_constraints_conditional_feasibility(feasibility_engine, handysize_vessel, rotterdam_port):
    """Test that missing draft data leads to CONDITIONALLY_FEASIBLE and clear warnings."""
    unverified_port = Port(
        port_name="TestPort",
        country="TestCountry",
        latitude=10.0,
        longitude=80.0,
        max_draft_m=None,  # Missing draft
        max_length_m=200.0,
        max_beam_m=32.0,
        data_status=DataQualityStatus.MISSING,
        source="Unverified Berth",
    )
    req = ShippingRequest(
        cargo_type="grain",
        cargo_quantity_tonnes=25000,
        origin_port="TestPort",
        destination_port="Rotterdam",
    )
    result = feasibility_engine.evaluate_vessel(handysize_vessel, req, unverified_port, rotterdam_port)
    assert result.feasibility_status == FeasibilityStatus.CONDITIONALLY_FEASIBLE
    assert result.checks["origin_draft"] is None
    assert any("maximum draft is not recorded/verified" in w for w in result.warnings)
