"""Transparent multi-criteria vessel scoring engine."""

from typing import Dict, Optional
from app.models.port import Port
from app.models.request import ShippingRequest
from app.models.vessel import ScoreBreakdown, Vessel, VesselAnalysisItem
from app.utils.constants import DataQualityStatus, FeasibilityStatus
from config import DEFAULT_SCORING_WEIGHTS


class ScoringEngine:
    """Calculates transparent, weighted suitability scores for feasible vessel candidates."""

    def __init__(self, weights: Optional[Dict[str, float]] = None):
        self.weights = weights or DEFAULT_SCORING_WEIGHTS

    def calculate_score(
        self,
        analysis_item: VesselAnalysisItem,
        vessel: Vessel,
        request: ShippingRequest,
        origin_port: Optional[Port],
        destination_port: Optional[Port],
    ) -> VesselAnalysisItem:
        """
        Compute normalized scores across four distinct dimensions.

        If the vessel is NOT_FEASIBLE or INSUFFICIENT_DATA, score is set to None.
        """
        if analysis_item.feasibility_status in (FeasibilityStatus.NOT_FEASIBLE, FeasibilityStatus.INSUFFICIENT_DATA):
            analysis_item.score = None
            analysis_item.score_breakdown = None
            return analysis_item

        w_util = self.weights.get("capacity_utilization", 0.40)
        w_port = self.weights.get("port_confidence", 0.30)
        w_cargo = self.weights.get("cargo_compatibility", 0.20)
        w_eff = self.weights.get("operational_efficiency", 0.10)

        # ---------------------------------------------------------
        # 1. CAPACITY UTILIZATION SCORE (0 - 100 raw)
        # ---------------------------------------------------------
        # High utilization (0.80 - 1.0) scores 90-100.
        # Below 0.50 receives a steeper curve penalty for commercial inefficiency.
        util = analysis_item.capacity_utilization
        if util > 1.0:
            raw_util_score = 0.0
        elif util >= 0.85:
            raw_util_score = 90.0 + ((util - 0.85) / 0.15) * 10.0
        elif util >= 0.60:
            raw_util_score = 70.0 + ((util - 0.60) / 0.25) * 20.0
        elif util >= 0.30:
            raw_util_score = 40.0 + ((util - 0.30) / 0.30) * 30.0
        else:
            raw_util_score = max(0.0, util * 100.0)

        util_points = round(raw_util_score * w_util, 2)

        # ---------------------------------------------------------
        # 2. PORT CONFIDENCE SCORE (0 - 100 raw)
        # ---------------------------------------------------------
        raw_port_score = 100.0
        if origin_port is None or origin_port.data_status != DataQualityStatus.VERIFIED:
            raw_port_score -= 25.0
        if origin_port and not origin_port.has_complete_constraints():
            raw_port_score -= 15.0

        if destination_port is None or destination_port.data_status != DataQualityStatus.VERIFIED:
            raw_port_score -= 25.0
        if destination_port and not destination_port.has_complete_constraints():
            raw_port_score -= 15.0

        if vessel.data_status != DataQualityStatus.VERIFIED:
            raw_port_score -= 10.0

        raw_port_score = max(20.0, raw_port_score)
        port_points = round(raw_port_score * w_port, 2)

        # ---------------------------------------------------------
        # 3. CARGO COMPATIBILITY SCORE (0 - 100 raw)
        # ---------------------------------------------------------
        # cargo check tri-state: True=compatible, False=incompatible, None=unknown
        # True  → 100 : full credit (feasibility already validated it)
        # False → 0   : vessel is cargo-incompatible and must never be recommended
        # None  → 50  : conditional / unverifiable (e.g. partial data)
        cargo_check = analysis_item.checks.get("cargo")
        if cargo_check is True:
            raw_cargo_score = 100.0
        elif cargo_check is False:
            raw_cargo_score = 0.0     # incompatible — hard disqualifier
        else:
            raw_cargo_score = 50.0   # unknown/conditional

        cargo_points = round(raw_cargo_score * w_cargo, 2)

        # ---------------------------------------------------------
        # 4. OPERATIONAL EFFICIENCY SCORE (0 - 100 raw)
        # ---------------------------------------------------------
        # Faster sea speed (12-15 knots) and ideal parcel-to-min-capacity ratio
        speed_ratio = min(1.0, max(0.6, vessel.avg_speed_knots / 15.0))
        commercial_fit = 1.0 if vessel.min_capacity_tonnes <= request.cargo_quantity_tonnes <= vessel.max_capacity_tonnes else 0.7
        raw_eff_score = (speed_ratio * 0.6 + commercial_fit * 0.4) * 100.0

        eff_points = round(raw_eff_score * w_eff, 2)

        # Total Composite Score
        total_score = round(util_points + port_points + cargo_points + eff_points, 1)

        # Penalty if conditionally feasible
        if analysis_item.feasibility_status == FeasibilityStatus.CONDITIONALLY_FEASIBLE:
            total_score = round(total_score * 0.90, 1)  # 10% confidence discount

        analysis_item.score = total_score
        analysis_item.score_breakdown = ScoreBreakdown(
            capacity_utilization=util_points,
            port_confidence=port_points,
            cargo_compatibility=cargo_points,
            operational_efficiency=eff_points,
        )

        return analysis_item
