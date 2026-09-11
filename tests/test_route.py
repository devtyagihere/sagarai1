"""Unit tests for geographic route distance and voyage duration service."""

import pytest
from app.models.port import Port
from app.models.vessel import Vessel
from app.services.route_service import RouteService
from app.utils.constants import DataQualityStatus


@pytest.fixture
def route_service():
    return RouteService()


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
def panamax_vessel():
    return Vessel(
        vessel_class="Panamax",
        min_capacity_tonnes=65000,
        max_capacity_tonnes=84999,
        typical_draft_m=14.5,
        typical_length_m=229.0,
        typical_beam_m=32.3,
        avg_speed_knots=14.0,
        supported_cargo=["iron_ore", "coal"],
        data_status=DataQualityStatus.VERIFIED,
        source="Baltic Exchange",
    )


def test_distance_calculation(route_service, paradip_port, rotterdam_port):
    """Test geographic distance between Paradip and Rotterdam returns valid nautical miles."""
    estimate = route_service.estimate_route(paradip_port, rotterdam_port)
    assert estimate.distance_estimate.unit == "nautical_miles"
    # After Bug 4 fix: method is 'sea_lane_estimate' (detour factor applied)
    assert estimate.distance_estimate.method == "sea_lane_estimate"
    # Sea-lane adjusted distance Paradip - Rotterdam is approx 4,000 - 6,000 NM (geodesic x 1.15)
    assert 4000 <= estimate.distance_estimate.value <= 6000


def test_voyage_duration_calculation(route_service, paradip_port, rotterdam_port, panamax_vessel):
    """Test voyage duration calculation using vessel speed."""
    estimate = route_service.estimate_route(paradip_port, rotterdam_port, panamax_vessel)
    assert estimate.estimated_duration_days > 0
    expected_days = round(estimate.distance_estimate.value / (14.0 * 24.0), 1)
    assert estimate.estimated_duration_days == pytest.approx(expected_days, abs=0.1)


def test_deadline_met(route_service, paradip_port, rotterdam_port, panamax_vessel):
    """Test shipping deadline evaluation."""
    # Long deadline (e.g. 40 days) should be met
    estimate_met = route_service.estimate_route(paradip_port, rotterdam_port, panamax_vessel, deadline_days=40.0)
    assert estimate_met.deadline_met is True

    # Very short deadline (e.g. 3 days) should NOT be met
    estimate_failed = route_service.estimate_route(paradip_port, rotterdam_port, panamax_vessel, deadline_days=3.0)
    assert estimate_failed.deadline_met is False


def test_route_warning_present(route_service, paradip_port, rotterdam_port):
    """Ensure transparent warning regarding sea-lane estimate vs actual route."""
    estimate = route_service.estimate_route(paradip_port, rotterdam_port)
    # After Bug 4 fix: warning text updated to reflect detour factor application
    assert "detour factor" in estimate.warning
