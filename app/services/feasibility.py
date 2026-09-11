"""Vessel feasibility evaluation engine."""

from typing import Dict, List, Optional
from app.models.port import Port
from app.models.request import ShippingRequest
from app.models.vessel import Vessel, VesselAnalysisItem
from app.services.cargo_service import CargoService
from app.utils.constants import DataQualityStatus, FeasibilityStatus
from config import LOW_UTILIZATION_THRESHOLD


class FeasibilityEngine:
    """Evaluates physical, commercial, and operational feasibility of vessel classes."""

    def __init__(self, cargo_service: Optional[CargoService] = None):
        self.cargo_service = cargo_service or CargoService()

    def evaluate_vessel(
        self,
        vessel: Vessel,
        request: ShippingRequest,
        origin_port: Optional[Port],
        destination_port: Optional[Port],
    ) -> VesselAnalysisItem:
        """
        Evaluate a vessel against shipping request parameters, origin port, and destination port.

        Returns a detailed VesselAnalysisItem with checks, warnings, and feasibility status.
        """
        checks: Dict[str, Optional[bool]] = {}
        warnings: List[str] = []
        rejection_reasons: List[str] = []

        # ---------------------------------------------------------
        # 1. CAPACITY & UTILIZATION CHECK
        # ---------------------------------------------------------
        cargo_qty = request.cargo_quantity_tonnes
        capacity_utilization = round(cargo_qty / vessel.max_capacity_tonnes, 4)

        if cargo_qty <= vessel.max_capacity_tonnes:
            checks["capacity"] = True
            if capacity_utilization < LOW_UTILIZATION_THRESHOLD:
                warnings.append(
                    f"Low capacity utilization ({capacity_utilization * 100:.1f}%). "
                    f"Vessel class {vessel.vessel_class} may be commercially inefficient for {cargo_qty:,.0f} tonnes."
                )
            if cargo_qty < vessel.min_capacity_tonnes:
                warnings.append(
                    f"Parcel size ({cargo_qty:,.0f}t) is below typical minimum commercial threshold "
                    f"({vessel.min_capacity_tonnes:,.0f}t) for {vessel.vessel_class}."
                )
        else:
            checks["capacity"] = False
            rejection_reasons.append(
                f"Insufficient cargo capacity: parcel of {cargo_qty:,.0f}t exceeds maximum deadweight of {vessel.max_capacity_tonnes:,.0f}t."
            )

        # ---------------------------------------------------------
        # 2. CARGO COMPATIBILITY CHECK
        # ---------------------------------------------------------
        cargo_result = self.cargo_service.check_compatibility(request.cargo_type, vessel)
        checks["cargo"] = cargo_result["compatible"]
        if not cargo_result["compatible"]:
            rejection_reasons.append(cargo_result["reason"])

        # ---------------------------------------------------------
        # 3. ORIGIN PORT CONSTRAINTS CHECK
        # ---------------------------------------------------------
        has_origin_unverified = False
        if origin_port is None:
            checks["origin_draft"] = None
            checks["origin_length"] = None
            checks["origin_beam"] = None
            warnings.append(f"Origin port '{request.origin_port}' not found in port database.")
            has_origin_unverified = True
        else:
            # Check Origin Draft
            if origin_port.max_draft_m is not None:
                if vessel.typical_draft_m <= origin_port.max_draft_m:
                    checks["origin_draft"] = True
                else:
                    checks["origin_draft"] = False
                    rejection_reasons.append(
                        f"Draft restriction at origin ({origin_port.port_name}): vessel draft ({vessel.typical_draft_m:.1f}m) "
                        f"exceeds port max draft ({origin_port.max_draft_m:.1f}m)."
                    )
            else:
                checks["origin_draft"] = None
                warnings.append(f"Origin port '{origin_port.port_name}' maximum draft is not recorded/verified.")
                has_origin_unverified = True

            # Check Origin Length (LOA)
            if origin_port.max_length_m is not None:
                if vessel.typical_length_m <= origin_port.max_length_m:
                    checks["origin_length"] = True
                else:
                    checks["origin_length"] = False
                    rejection_reasons.append(
                        f"Length restriction at origin ({origin_port.port_name}): vessel LOA ({vessel.typical_length_m:.1f}m) "
                        f"exceeds port max length ({origin_port.max_length_m:.1f}m)."
                    )
            else:
                checks["origin_length"] = None
                warnings.append(f"Origin port '{origin_port.port_name}' maximum length is not recorded/verified.")
                has_origin_unverified = True

            # Check Origin Beam
            if origin_port.max_beam_m is not None:
                if vessel.typical_beam_m <= origin_port.max_beam_m:
                    checks["origin_beam"] = True
                else:
                    checks["origin_beam"] = False
                    rejection_reasons.append(
                        f"Beam restriction at origin ({origin_port.port_name}): vessel beam ({vessel.typical_beam_m:.1f}m) "
                        f"exceeds port max beam ({origin_port.max_beam_m:.1f}m)."
                    )
            else:
                checks["origin_beam"] = None
                warnings.append(f"Origin port '{origin_port.port_name}' maximum beam is not recorded/verified.")
                has_origin_unverified = True

            if origin_port.data_status != DataQualityStatus.VERIFIED:
                has_origin_unverified = True
                warnings.append(
                    f"Origin port '{origin_port.port_name}' data status is '{origin_port.data_status.value}'."
                )

        # ---------------------------------------------------------
        # 4. DESTINATION PORT CONSTRAINTS CHECK
        # ---------------------------------------------------------
        has_dest_unverified = False
        if destination_port is None:
            checks["destination_draft"] = None
            checks["destination_length"] = None
            checks["destination_beam"] = None
            warnings.append(f"Destination port '{request.destination_port}' not found in port database.")
            has_dest_unverified = True
        else:
            # Check Destination Draft
            if destination_port.max_draft_m is not None:
                if vessel.typical_draft_m <= destination_port.max_draft_m:
                    checks["destination_draft"] = True
                else:
                    checks["destination_draft"] = False
                    rejection_reasons.append(
                        f"Draft restriction at destination ({destination_port.port_name}): vessel draft ({vessel.typical_draft_m:.1f}m) "
                        f"exceeds port max draft ({destination_port.max_draft_m:.1f}m)."
                    )
            else:
                checks["destination_draft"] = None
                warnings.append(f"Destination port '{destination_port.port_name}' maximum draft is not recorded/verified.")
                has_dest_unverified = True

            # Check Destination Length (LOA)
            if destination_port.max_length_m is not None:
                if vessel.typical_length_m <= destination_port.max_length_m:
                    checks["destination_length"] = True
                else:
                    checks["destination_length"] = False
                    rejection_reasons.append(
                        f"Length restriction at destination ({destination_port.port_name}): vessel LOA ({vessel.typical_length_m:.1f}m) "
                        f"exceeds port max length ({destination_port.max_length_m:.1f}m)."
                    )
            else:
                checks["destination_length"] = None
                warnings.append(f"Destination port '{destination_port.port_name}' maximum length is not recorded/verified.")
                has_dest_unverified = True

            # Check Destination Beam
            if destination_port.max_beam_m is not None:
                if vessel.typical_beam_m <= destination_port.max_beam_m:
                    checks["destination_beam"] = True
                else:
                    checks["destination_beam"] = False
                    rejection_reasons.append(
                        f"Beam restriction at destination ({destination_port.port_name}): vessel beam ({vessel.typical_beam_m:.1f}m) "
                        f"exceeds port max beam ({destination_port.max_beam_m:.1f}m)."
                    )
            else:
                checks["destination_beam"] = None
                warnings.append(f"Destination port '{destination_port.port_name}' maximum beam is not recorded/verified.")
                has_dest_unverified = True

            if destination_port.data_status != DataQualityStatus.VERIFIED:
                has_dest_unverified = True
                warnings.append(
                    f"Destination port '{destination_port.port_name}' data status is '{destination_port.data_status.value}'."
                )

        # Check vessel data status
        has_vessel_unverified = vessel.data_status != DataQualityStatus.VERIFIED
        if has_vessel_unverified:
            warnings.append(f"Vessel class '{vessel.vessel_class}' specifications are '{vessel.data_status.value}'.")

        # ---------------------------------------------------------
        # 5. DETERMINE FEASIBILITY STATUS
        # ---------------------------------------------------------
        # Any definitive False fails the feasibility
        has_failed_check = any(val is False for val in checks.values())

        if has_failed_check:
            feasibility_status = FeasibilityStatus.NOT_FEASIBLE
        elif origin_port is None and destination_port is None:
            feasibility_status = FeasibilityStatus.INSUFFICIENT_DATA
            warnings.append("Insufficient data: neither origin nor destination port could be identified.")
        elif has_origin_unverified or has_dest_unverified or has_vessel_unverified:
            feasibility_status = FeasibilityStatus.CONDITIONALLY_FEASIBLE
        else:
            feasibility_status = FeasibilityStatus.FEASIBLE

        return VesselAnalysisItem(
            vessel_class=vessel.vessel_class,
            feasibility_status=feasibility_status,
            checks=checks,
            capacity_utilization=capacity_utilization,
            warnings=warnings,
            rejection_reasons=rejection_reasons,
            data_status=vessel.data_status,
        )
