"""End-to-end integration tests for Shipping & Vessel Intelligence Engine."""

import json
from pathlib import Path
import pytest
from pydantic import ValidationError

from app.main import analyze_shipping_request
from config import BASE_DIR


def test_case_insensitive_matching():
    """Verify that lower, upper, and mixed-case port and cargo queries resolve accurately."""
    res1 = analyze_shipping_request(
        cargo_type="IRON_ORE",
        cargo_quantity_tonnes=75000,
        origin_port="paradip",
        destination_port="ROTTERDAM",
    )
    res2 = analyze_shipping_request(
        cargo_type="iron_ore",
        cargo_quantity_tonnes=75000,
        origin_port="PARADIP",
        destination_port="rotterdam",
    )
    assert res1["recommendation"]["recommended_vessel"] == "Panamax"
    assert res2["recommendation"]["recommended_vessel"] == "Panamax"
    assert res1["route_estimate"]["distance_estimate"]["value"] == res2["route_estimate"]["distance_estimate"]["value"]


def test_invalid_request_validations():
    """Verify Pydantic input validation catches errors."""
    # Negative quantity
    with pytest.raises(ValidationError):
        analyze_shipping_request(
            cargo_type="coal",
            cargo_quantity_tonnes=-500,
            origin_port="Paradip",
            destination_port="Rotterdam",
        )

    # Identical origin and destination
    with pytest.raises(ValidationError):
        analyze_shipping_request(
            cargo_type="coal",
            cargo_quantity_tonnes=50000,
            origin_port="Paradip",
            destination_port="Paradip",
        )

    # Empty port
    with pytest.raises(ValidationError):
        analyze_shipping_request(
            cargo_type="coal",
            cargo_quantity_tonnes=50000,
            origin_port="",
            destination_port="Rotterdam",
        )


def test_all_sample_requests_execute():
    """Verify that all scenarios in examples/sample_requests.json run without unhandled errors."""
    samples_path = BASE_DIR / "examples" / "sample_requests.json"
    assert samples_path.exists()

    with open(samples_path, "r", encoding="utf-8") as f:
        samples = json.load(f)

    for sample in samples:
        req = sample["request"]
        res = analyze_shipping_request(
            cargo_type=req["cargo_type"],
            cargo_quantity_tonnes=req["cargo_quantity_tonnes"],
            origin_port=req["origin_port"],
            destination_port=req["destination_port"],
            shipping_deadline_days=req.get("shipping_deadline_days"),
        )
        assert "recommendation" in res
        assert "vessel_analysis" in res
        assert "route_estimate" in res
        assert "data_quality" in res
