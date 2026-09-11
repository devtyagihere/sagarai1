"""
Vessel Economics Service — voyage cost comparison across all vessel classes.

FORMULAS (documented):
  voyage_cost_usd = daily_rate_usd × voyage_days
  cost_per_mt_usd = voyage_cost_usd / cargo_quantity_tonnes

Daily rates are SYNTHETIC indicative values based on Baltic Exchange 2023-2024
average ranges. Not real charter quotes.

The service compares all vessel classes including not-feasible ones (clearly
labelled), so users can see why smaller/cheaper vessels are excluded.

IMPORTANT: Incompatible vessels (cargo check False) are always excluded from
           the "cheapest feasible" recommendation regardless of cost.
"""

from typing import List, Optional

from app.models.operations import VesselEconomicsItem, VesselEconomicsResult
from app.models.vessel import VesselAnalysisItem
from app.utils.constants import FeasibilityStatus
from config import VESSEL_DAILY_RATES_USD, MARKET_DATA_SOURCE


class VesselEconomicsService:
    """
    Computes per-voyage cost for every analysed vessel class.

    Inputs:
      - analysis_items: output of FeasibilityEngine (already scored)
      - voyage_days:    from RouteService
      - cargo_quantity: from ShippingRequest
      - recommended_vessel: name of RecommendationEngine winner

    Outputs:
      VesselEconomicsResult with a sorted comparison table.
    """

    def compute(
        self,
        analysis_items: List[VesselAnalysisItem],
        voyage_days: float,
        cargo_quantity_tonnes: float,
        recommended_vessel: Optional[str] = None,
    ) -> VesselEconomicsResult:
        """Build cost comparison for all vessel classes."""

        if voyage_days <= 0 or cargo_quantity_tonnes <= 0:
            return VesselEconomicsResult(
                cargo_quantity_tonnes=cargo_quantity_tonnes,
                voyage_days=voyage_days,
                comparison=[],
                cheapest_feasible_vessel=None,
                recommended_vessel=recommended_vessel,
            )

        items: List[VesselEconomicsItem] = []
        for ai in analysis_items:
            daily_rate = VESSEL_DAILY_RATES_USD.get(ai.vessel_class.lower(), 15_000)
            voyage_cost = round(daily_rate * voyage_days, 2)
            cost_per_mt = round(voyage_cost / cargo_quantity_tonnes, 4)
            is_rec = (
                recommended_vessel is not None
                and ai.vessel_class.lower() == recommended_vessel.lower()
            )
            items.append(VesselEconomicsItem(
                vessel_class=ai.vessel_class,
                daily_rate_usd=daily_rate,
                voyage_days=round(voyage_days, 1),
                voyage_cost_usd=voyage_cost,
                cost_per_mt_usd=cost_per_mt,
                cargo_quantity_tonnes=cargo_quantity_tonnes,
                feasibility_status=ai.feasibility_status.value,
                is_recommended=is_rec,
            ))

        # Sort: feasible first (by cost_per_mt), then conditional, then not-feasible
        def _sort_key(x: VesselEconomicsItem):
            order = {
                FeasibilityStatus.FEASIBLE.value: 0,
                FeasibilityStatus.CONDITIONALLY_FEASIBLE.value: 1,
                FeasibilityStatus.NOT_FEASIBLE.value: 2,
                FeasibilityStatus.INSUFFICIENT_DATA.value: 3,
            }
            return (order.get(x.feasibility_status, 9), x.cost_per_mt_usd)

        items.sort(key=_sort_key)

        # Cheapest FEASIBLE vessel (cargo check must be True)
        cheapest = None
        for ai in analysis_items:
            if ai.feasibility_status == FeasibilityStatus.FEASIBLE:
                if ai.checks.get("cargo") is True:
                    # Find match in items
                    for it in items:
                        if it.vessel_class == ai.vessel_class:
                            if cheapest is None or it.cost_per_mt_usd < cheapest.cost_per_mt_usd:
                                cheapest = it

        voyage_days_used = voyage_days
        if recommended_vessel:
            for it in items:
                if it.vessel_class.lower() == recommended_vessel.lower():
                    voyage_days_used = it.voyage_days
                    break

        return VesselEconomicsResult(
            cargo_quantity_tonnes=cargo_quantity_tonnes,
            voyage_days=voyage_days_used,
            comparison=items,
            cheapest_feasible_vessel=cheapest.vessel_class if cheapest else None,
            recommended_vessel=recommended_vessel,
            data_source=MARKET_DATA_SOURCE,
        )


default_vessel_economics_service = VesselEconomicsService()
