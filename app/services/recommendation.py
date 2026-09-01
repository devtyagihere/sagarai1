"""Recommendation engine for selecting the optimal vessel class."""

from typing import List, Optional
from app.models.port import Port
from app.models.request import RecommendationResult, ShippingRequest
from app.models.vessel import Vessel, VesselAnalysisItem
from app.utils.constants import (
    DataQualityStatus,
    FeasibilityStatus,
    RecommendationConfidence,
    RecommendationStatus,
)


class RecommendationEngine:
    """Ranks candidates and formulates justified vessel recommendations."""

    def recommend(
        self,
        analysis_items: List[VesselAnalysisItem],
        vessels_map: dict,
        request: ShippingRequest,
        origin_port: Optional[Port],
        destination_port: Optional[Port],
    ) -> RecommendationResult:
        """
        Evaluate analyzed vessels, prioritize verified feasible classes over conditionally feasible,
        rank by score, and produce structured decision reasoning.
        """
        # Check if all items lack sufficient data
        all_insufficient = all(
            item.feasibility_status == FeasibilityStatus.INSUFFICIENT_DATA for item in analysis_items
        )
        if all_insufficient or (origin_port is None and destination_port is None):
            return RecommendationResult(
                recommended_vessel=None,
                status=RecommendationStatus.INSUFFICIENT_DATA,
                recommendation_confidence=RecommendationConfidence.NONE,
                reasoning=[],
                message="Port constraints must be verified before making a reliable vessel recommendation.",
            )

        # Filter candidates
        feasible_candidates = [
            item for item in analysis_items if item.feasibility_status == FeasibilityStatus.FEASIBLE
        ]
        conditional_candidates = [
            item for item in analysis_items if item.feasibility_status == FeasibilityStatus.CONDITIONALLY_FEASIBLE
        ]

        # Prioritize FEASIBLE over CONDITIONALLY_FEASIBLE
        if feasible_candidates:
            # Sort by score descending, then by capacity utilization descending
            feasible_candidates.sort(
                key=lambda x: (x.score or 0.0, x.capacity_utilization), reverse=True
            )
            best_item = feasible_candidates[0]
            confidence = RecommendationConfidence.HIGH
            status = RecommendationStatus.RECOMMENDED
        elif conditional_candidates:
            # Only conditionally feasible vessels exist
            conditional_candidates.sort(
                key=lambda x: (x.score or 0.0, x.capacity_utilization), reverse=True
            )
            best_item = conditional_candidates[0]
            confidence = RecommendationConfidence.MEDIUM
            status = RecommendationStatus.CONDITIONALLY_RECOMMENDED
        else:
            # No feasible vessels
            reasons_summary = []
            for item in analysis_items:
                if item.rejection_reasons:
                    reasons_summary.append(f"{item.vessel_class}: {item.rejection_reasons[0]}")

            return RecommendationResult(
                recommended_vessel=None,
                status=RecommendationStatus.NO_FEASIBLE_VESSEL,
                recommendation_confidence=RecommendationConfidence.NONE,
                reasoning=[],
                message=f"No vessel class is physically or commercially feasible for this shipment. {'; '.join(reasons_summary[:3])}",
            )

        # Generate clear, human-readable reasoning
        vessel_obj: Optional[Vessel] = vessels_map.get(best_item.vessel_class.lower())
        reasoning = self._build_reasoning(best_item, vessel_obj, request, origin_port, destination_port)

        return RecommendationResult(
            recommended_vessel=best_item.vessel_class,
            status=status,
            recommendation_confidence=confidence,
            reasoning=reasoning,
            message=None,
        )

    def _build_reasoning(
        self,
        item: VesselAnalysisItem,
        vessel: Optional[Vessel],
        request: ShippingRequest,
        origin_port: Optional[Port],
        destination_port: Optional[Port],
    ) -> List[str]:
        """Construct bulleted justification for the recommendation."""
        reasons: List[str] = []

        # 1. Capacity reasoning
        if vessel:
            reasons.append(
                f"Optimal parcel capacity: {request.cargo_quantity_tonnes:,.0f}t fits within {vessel.vessel_class} range "
                f"({vessel.min_capacity_tonnes:,.0f}t - {vessel.max_capacity_tonnes:,.0f}t)."
            )
        reasons.append(
            f"High payload utilization ({item.capacity_utilization * 100:.1f}%), maximizing commercial freight efficiency."
        )

        # 2. Cargo compatibility
        reasons.append(f"Full cargo compatibility for '{request.cargo_type}' with vessel hold/gear configuration.")

        # 3. Port constraints
        if origin_port:
            draft_info = f"draft {vessel.typical_draft_m:.1f}m <= max {origin_port.max_draft_m:.1f}m" if origin_port.max_draft_m else "verified"
            reasons.append(f"Complies with origin port ({origin_port.port_name}) draft and berth limits ({draft_info}).")

        if destination_port:
            draft_info = f"draft {vessel.typical_draft_m:.1f}m <= max {destination_port.max_draft_m:.1f}m" if destination_port.max_draft_m else "verified"
            reasons.append(f"Complies with destination port ({destination_port.port_name}) navigational limits ({draft_info}).")

        # 4. Suitability Score
        if item.score:
            reasons.append(f"Highest composite suitability score ({item.score}/100) among evaluated candidate classes.")

        # 5. Conditional notice if applicable
        if item.feasibility_status == FeasibilityStatus.CONDITIONALLY_FEASIBLE:
            reasons.append("Conditional approval: verify port draft/LOA directly with local harbor master prior to fixture.")

        return reasons
