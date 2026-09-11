"""Unit tests for cargo compatibility and steel product differentiation."""

import pytest
from app.models.vessel import Vessel
from app.services.cargo_service import CargoService
from app.services.data_loader import default_data_loader
from app.utils.constants import DataQualityStatus


@pytest.fixture
def cargo_service():
    default_data_loader.load_all()
    return CargoService(default_data_loader)


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
        source="BIMCO",
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
        source="Baltic Exchange",
    )


def test_standard_dry_bulk_compatibility(cargo_service, panamax_vessel):
    """Test standard iron ore and coal compatibility with Panamax."""
    res_ore = cargo_service.check_compatibility("iron_ore", panamax_vessel)
    assert res_ore["compatible"] is True

    res_coal = cargo_service.check_compatibility("coal", panamax_vessel)
    assert res_coal["compatible"] is True


def test_steel_product_differentiation(cargo_service, handysize_vessel, panamax_vessel):
    """Test steel coils requires geared handling and fails on gearless Panamax."""
    # Handysize supports geared steel coils
    res_handy = cargo_service.check_compatibility("steel_coils", handysize_vessel)
    assert res_handy["compatible"] is True

    # Gearless Panamax fails for steel coils
    res_panamax = cargo_service.check_compatibility("steel_coils", panamax_vessel)
    assert res_panamax["compatible"] is False
    assert "geared" in res_panamax["reason"]


def test_ambiguous_generic_steel(cargo_service, handysize_vessel):
    """Test that ambiguous 'steel' requests clarification for specific steel forms."""
    res = cargo_service.check_compatibility("steel", handysize_vessel)
    assert res["compatible"] is False
    assert "Specify exact steel form" in res["reason"]


def test_incompatible_liquid_cargo(cargo_service, handysize_vessel):
    """Test liquid crude petroleum is rejected on dry bulkers."""
    res = cargo_service.check_compatibility("crude_oil", handysize_vessel)
    assert res["compatible"] is False
    assert "incompatible" in res["reason"].lower()
