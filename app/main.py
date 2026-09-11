"""Main orchestration module for Shipping & Vessel Intelligence Engine."""

import argparse
import json
import sys
from typing import Any, Dict, List, Optional

from app.models.port import Port
from app.models.request import (
    DataQualityReport,
    DistanceEstimate,
    RecommendationResult,
    RouteEstimate,
    ShippingRequest,
    ShippingResponse,
)
from app.models.vessel import VesselAnalysisItem
from app.services.cargo_service import CargoService
from app.services.data_loader import DataLoader, default_data_loader
from app.services.feasibility import FeasibilityEngine
from app.services.recommendation import RecommendationEngine
from app.services.route_service import RouteService
from app.services.scoring import ScoringEngine
from app.utils.constants import (
    DataQualityStatus,
    OverallDataQuality,
    RecommendationConfidence,
    RecommendationStatus,
)

# Phase 2: Market data + forecasting (imported with graceful fallback)
try:
    from app.models.market import MarketAndForecastResult
    from app.services.market_service import default_market_service
    from app.services.freight_forecasting import default_forecasting_service
    _MARKET_AVAILABLE = True
except ImportError:
    _MARKET_AVAILABLE = False

# Phase 3: Port operations, risk, vessel economics (graceful fallback)
try:
    from app.services.port_operations import default_port_ops_service
    from app.services.risk_service import default_risk_service
    from app.services.vessel_economics import default_vessel_economics_service
    _PHASE3_AVAILABLE = True
except ImportError:
    _PHASE3_AVAILABLE = False

# Phase 4: Integrated Decision Engine (graceful fallback)
try:
    from app.services.decision_engine import default_decision_engine
    _PHASE4_AVAILABLE = True
except ImportError:
    _PHASE4_AVAILABLE = False


def analyze_shipping_request(
    cargo_type: str,
    cargo_quantity_tonnes: float,
    origin_port: str,
    destination_port: str,
    shipping_deadline_days: Optional[float] = None,
    data_loader: Optional[DataLoader] = None,
) -> Dict[str, Any]:
    """
    Analyze maritime freight shipment feasibility, vessel suitability, and route transit.

    Args:
        cargo_type: Commodity identifier (e.g. 'iron_ore', 'coal', 'grain', 'steel_coils').
        cargo_quantity_tonnes: Shipment weight in metric tonnes (> 0).
        origin_port: Loading port name.
        destination_port: Discharge port name.
        shipping_deadline_days: Optional maximum delivery window in days.
        data_loader: Optional custom DataLoader instance.

    Returns:
        JSON-compatible Python dictionary adhering to the ShippingResponse schema.
    """
    loader = data_loader or default_data_loader
    loader.load_all()

    # 1. Validate Input Request
    request = ShippingRequest(
        cargo_type=cargo_type,
        cargo_quantity_tonnes=cargo_quantity_tonnes,
        origin_port=origin_port,
        destination_port=destination_port,
        shipping_deadline_days=shipping_deadline_days,
    )

    # 2. Retrieve Port Specifications
    origin_port_obj = loader.get_port(request.origin_port)
    dest_port_obj = loader.get_port(request.destination_port)

    # 3. Retrieve Vessels & Setup Services
    vessels = loader.get_vessels()
    vessels_map = {v.vessel_class.lower(): v for v in vessels}

    cargo_service = CargoService(loader)
    feasibility_engine = FeasibilityEngine(cargo_service)
    scoring_engine = ScoringEngine()
    recommendation_engine = RecommendationEngine()
    route_service = RouteService()

    # 4. Evaluate Feasibility and Compute Scores for each Vessel Class
    analysis_items: List[VesselAnalysisItem] = []
    for vessel in vessels:
        analysis_item = feasibility_engine.evaluate_vessel(
            vessel=vessel,
            request=request,
            origin_port=origin_port_obj,
            destination_port=dest_port_obj,
        )
        analysis_item = scoring_engine.calculate_score(
            analysis_item=analysis_item,
            vessel=vessel,
            request=request,
            origin_port=origin_port_obj,
            destination_port=dest_port_obj,
        )
        analysis_items.append(analysis_item)

    # 5. Determine Recommended Vessel Class
    recommendation: RecommendationResult = recommendation_engine.recommend(
        analysis_items=analysis_items,
        vessels_map=vessels_map,
        request=request,
        origin_port=origin_port_obj,
        destination_port=dest_port_obj,
    )

    # 6. Estimate Geographic Route & Voyage Duration
    best_vessel = None
    if recommendation.recommended_vessel:
        best_vessel = vessels_map.get(recommendation.recommended_vessel.lower())

    if origin_port_obj and dest_port_obj:
        route_estimate = route_service.estimate_route(
            origin_port=origin_port_obj,
            destination_port=dest_port_obj,
            vessel=best_vessel,
            deadline_days=request.shipping_deadline_days,
        )
    else:
        # Graceful fallback when ports are unknown
        route_estimate = RouteEstimate(
            origin_port=request.origin_port,
            destination_port=request.destination_port,
            distance_estimate=DistanceEstimate(
                value=0.0,
                unit="nautical_miles",
                method="geographic_estimate",
            ),
            estimated_duration_days=0.0,
            deadline_met=None,
            warning="Unable to calculate geographic distance: one or both ports not found in coordinate database.",
        )

    # 7. Audit Data Quality & Verification
    data_quality = _build_data_quality_report(origin_port_obj, dest_port_obj, analysis_items)

    # 8. Phase 2 — Market Data & Freight Rate Forecast (graceful: never breaks core pipeline)
    market_intelligence = None
    if _MARKET_AVAILABLE:
        market_intelligence = _build_market_intelligence(
            request=request,
            route_estimate=route_estimate,
            recommendation=recommendation,
        )

    # 9. Phase 3 — Port Operations, Risk, Vessel Economics (graceful: never breaks core pipeline)
    port_operations = None
    risk_assessment = None
    vessel_economics = None
    if _PHASE3_AVAILABLE:
        port_operations = _build_port_operations(request.origin_port, request.destination_port)
        risk_assessment = _build_risk_assessment(request.origin_port, request.destination_port)
        vessel_economics = _build_vessel_economics(
            analysis_items=analysis_items,
            voyage_days=route_estimate.estimated_duration_days,
            cargo_quantity=request.cargo_quantity_tonnes,
            recommended_vessel=recommendation.recommended_vessel,
        )

    # 10. Phase 4 — Integrated Decision Engine (graceful: never breaks core pipeline)
    decision = None
    if _PHASE4_AVAILABLE:
        decision = _build_decision(
            market_intelligence=market_intelligence,
            port_operations=port_operations,
            risk_assessment=risk_assessment,
            vessel_economics=vessel_economics,
            recommended_vessel=recommendation.recommended_vessel,
            analysis_items=analysis_items,
        )

    # 11. Assemble Full Response
    response = ShippingResponse(
        request={
            "cargo_type": request.cargo_type,
            "cargo_quantity_tonnes": request.cargo_quantity_tonnes,
            "origin_port": request.origin_port,
            "destination_port": request.destination_port,
            "shipping_deadline_days": request.shipping_deadline_days,
        },
        vessel_analysis=analysis_items,
        recommendation=recommendation,
        route_estimate=route_estimate,
        data_quality=data_quality,
        market_intelligence=market_intelligence,
        port_operations=port_operations,
        risk_assessment=risk_assessment,
        vessel_economics=vessel_economics,
        decision=decision,
    )

    return response.model_dump()


def _build_market_intelligence(
    request: ShippingRequest,
    route_estimate: "RouteEstimate",
    recommendation: "RecommendationResult",
) -> Optional[Dict[str, Any]]:
    """
    Collect market snapshot and freight forecast for the current request.
    Returns None on any error so the core pipeline is never interrupted.
    """
    try:
        market_snapshot = default_market_service.get_market_snapshot(request.cargo_type)
        vessel_type = recommendation.recommended_vessel or "Panamax"
        distance_nm = route_estimate.distance_estimate.value if route_estimate else 4000.0

        freight_forecast = default_forecasting_service.forecast(
            origin=request.origin_port,
            destination=request.destination_port,
            cargo_type=request.cargo_type,
            vessel_type=vessel_type,
            distance_nm=distance_nm,
        )
        model_evaluation = default_forecasting_service.get_evaluation()

        result = MarketAndForecastResult(
            market_snapshot=market_snapshot,
            freight_forecast=freight_forecast,
            model_evaluation=model_evaluation,
        )
        return result.model_dump()
    except Exception:
        return None


def _build_port_operations(origin: str, destination: str) -> Optional[Dict[str, Any]]:
    """
    Collect operational congestion data for origin and destination ports.
    Physical feasibility is NOT re-computed here — that is FeasibilityEngine's job.
    Returns None on any error.
    """
    try:
        result = default_port_ops_service.get_port_operations_result(origin, destination)
        return result.model_dump()
    except Exception:
        return None


def _build_risk_assessment(origin: str, destination: str) -> Optional[Dict[str, Any]]:
    """
    Compute weather and marine risk score for the route.
    Returns None on any error.
    """
    try:
        result = default_risk_service.assess(origin, destination)
        return result.model_dump()
    except Exception:
        return None


def _build_vessel_economics(
    analysis_items: List[VesselAnalysisItem],
    voyage_days: float,
    cargo_quantity: float,
    recommended_vessel: Optional[str],
) -> Optional[Dict[str, Any]]:
    """
    Build voyage cost comparison for all vessel classes.
    Returns None on any error.
    """
    try:
        result = default_vessel_economics_service.compute(
            analysis_items=analysis_items,
            voyage_days=voyage_days,
            cargo_quantity_tonnes=cargo_quantity,
            recommended_vessel=recommended_vessel,
        )
        return result.model_dump()
    except Exception:
        return None


def _build_decision(
    market_intelligence: Optional[Dict[str, Any]],
    port_operations: Optional[Dict[str, Any]],
    risk_assessment: Optional[Dict[str, Any]],
    vessel_economics: Optional[Dict[str, Any]],
    recommended_vessel: Optional[str],
    analysis_items: Optional[List[VesselAnalysisItem]] = None,
) -> Optional[Dict[str, Any]]:
    """
    Run the Phase 4 integrated decision engine.
    Combines all upstream module outputs into CHARTER NOW / WAIT / NEGOTIATE.
    Returns None on any error so the core pipeline is never interrupted.
    """
    try:
        result = default_decision_engine.decide(
            market_intelligence=market_intelligence,
            port_operations=port_operations,
            risk_assessment=risk_assessment,
            vessel_economics=vessel_economics,
            recommended_vessel=recommended_vessel,
            analysis_items=analysis_items,
        )
        return result.model_dump()
    except Exception:
        return None


def _build_data_quality_report(
    origin_port: Optional[Port],
    dest_port: Optional[Port],
    analysis_items: List[VesselAnalysisItem],
) -> DataQualityReport:
    """Assess integrity and verification status of inputs and datasets."""
    unverified: List[str] = []

    origin_status = origin_port.data_status if origin_port else DataQualityStatus.MISSING
    dest_status = dest_port.data_status if dest_port else DataQualityStatus.MISSING

    if origin_port is None:
        unverified.append("Origin port not found in verified registry")
    else:
        if origin_port.data_status != DataQualityStatus.VERIFIED:
            unverified.append(f"Origin port '{origin_port.port_name}' status is {origin_port.data_status.value}")
        for missing_field in origin_port.get_missing_constraints():
            unverified.append(f"Origin port '{origin_port.port_name}' missing constraint: {missing_field}")

    if dest_port is None:
        unverified.append("Destination port not found in verified registry")
    else:
        if dest_port.data_status != DataQualityStatus.VERIFIED:
            unverified.append(f"Destination port '{dest_port.port_name}' status is {dest_port.data_status.value}")
        for missing_field in dest_port.get_missing_constraints():
            unverified.append(f"Destination port '{dest_port.port_name}' missing constraint: {missing_field}")

    vessel_statuses = {item.data_status for item in analysis_items}
    vessel_overall = DataQualityStatus.VERIFIED if all(s == DataQualityStatus.VERIFIED for s in vessel_statuses) else DataQualityStatus.ESTIMATED

    for item in analysis_items:
        if item.data_status != DataQualityStatus.VERIFIED:
            unverified.append(f"Vessel class '{item.vessel_class}' status is {item.data_status.value}")

    # Determine overall data quality
    if origin_status == DataQualityStatus.MISSING or dest_status == DataQualityStatus.MISSING:
        overall = OverallDataQuality.INSUFFICIENT
    elif origin_status == DataQualityStatus.VERIFIED and dest_status == DataQualityStatus.VERIFIED and not unverified:
        overall = OverallDataQuality.FULLY_VERIFIED
    elif (origin_status == DataQualityStatus.VERIFIED or dest_status == DataQualityStatus.VERIFIED) or unverified:
        overall = OverallDataQuality.PARTIALLY_VERIFIED
    else:
        overall = OverallDataQuality.ESTIMATED

    return DataQualityReport(
        overall_status=overall,
        origin_port_status=origin_status,
        destination_port_status=dest_status,
        vessel_data_status=vessel_overall,
        unverified_elements=unverified,
    )


def main() -> None:
    """CLI Entrypoint for running maritime intelligence analysis."""
    parser = argparse.ArgumentParser(
        description="Shipping & Vessel Intelligence Engine - AI-Powered Freight Booking Decision Platform"
    )
    parser.add_argument("--cargo", "-c", type=str, default="iron_ore", help="Cargo type (e.g. iron_ore, coal, grain)")
    parser.add_argument("--quantity", "-q", type=float, default=75000, help="Cargo quantity in metric tonnes")
    parser.add_argument("--origin", "-o", type=str, default="Paradip", help="Origin port name")
    parser.add_argument("--destination", "-d", type=str, default="Rotterdam", help="Destination port name")
    parser.add_argument("--deadline", "-t", type=float, default=None, help="Shipping deadline in days (optional)")
    parser.add_argument("--file", "-f", type=str, default=None, help="JSON input file path")
    parser.add_argument("--pretty", action="store_true", default=True, help="Pretty-print JSON output")

    args = parser.parse_args()

    try:
        if args.file:
            with open(args.file, "r", encoding="utf-8") as fp:
                data = json.load(fp)
            result = analyze_shipping_request(
                cargo_type=data["cargo_type"],
                cargo_quantity_tonnes=float(data["cargo_quantity_tonnes"]),
                origin_port=data["origin_port"],
                destination_port=data["destination_port"],
                shipping_deadline_days=data.get("shipping_deadline_days"),
            )
        else:
            result = analyze_shipping_request(
                cargo_type=args.cargo,
                cargo_quantity_tonnes=args.quantity,
                origin_port=args.origin,
                destination_port=args.destination,
                shipping_deadline_days=args.deadline,
            )

        indent = 2 if args.pretty else None
        print(json.dumps(result, indent=indent))

    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
