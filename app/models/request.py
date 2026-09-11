"""Request and response models for shipping intelligence API."""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field, model_validator
from app.models.vessel import VesselAnalysisItem
from app.utils.constants import (
    DataQualityStatus,
    OverallDataQuality,
    RecommendationConfidence,
    RecommendationStatus,
)


class ShippingRequest(BaseModel):
    """Input parameters for evaluating freight booking and vessel feasibility."""
    cargo_type: str = Field(..., description="Type of cargo to transport (e.g. iron_ore, coal, grain)")
    cargo_quantity_tonnes: float = Field(..., description="Cargo parcel quantity in metric tonnes")
    origin_port: str = Field(..., description="Port of loading (POL)")
    destination_port: str = Field(..., description="Port of discharge (POD)")
    shipping_deadline_days: Optional[float] = Field(None, description="Optional maximum allowed transit days")

    @model_validator(mode="after")
    def validate_request(self) -> "ShippingRequest":
        # Validate cargo_type
        if not self.cargo_type or not self.cargo_type.strip():
            raise ValueError("cargo_type cannot be empty")
        self.cargo_type = self.cargo_type.strip().lower()

        # Validate cargo_quantity_tonnes
        if self.cargo_quantity_tonnes <= 0:
            raise ValueError("cargo_quantity_tonnes must be greater than 0")

        # Validate origin_port
        if not self.origin_port or not self.origin_port.strip():
            raise ValueError("origin_port cannot be empty")
        self.origin_port = self.origin_port.strip()

        # Validate destination_port
        if not self.destination_port or not self.destination_port.strip():
            raise ValueError("destination_port cannot be empty")
        self.destination_port = self.destination_port.strip()

        # Validate origin != destination
        if self.origin_port.lower() == self.destination_port.lower():
            raise ValueError("origin_port and destination_port cannot be the same")

        # Validate shipping_deadline_days
        if self.shipping_deadline_days is not None and self.shipping_deadline_days <= 0:
            raise ValueError("shipping_deadline_days must be greater than 0 if provided")

        return self


class DistanceEstimate(BaseModel):
    """Geographic distance calculation details."""
    value: float = Field(..., description="Estimated distance in specified units")
    unit: str = Field("nautical_miles", description="Distance measurement unit")
    method: str = Field("geographic_estimate", description="Methodology used for calculation")


class RouteEstimate(BaseModel):
    """Route calculation and estimated voyage duration."""
    origin_port: str = Field(..., description="Origin loading port")
    destination_port: str = Field(..., description="Destination discharge port")
    distance_estimate: DistanceEstimate = Field(..., description="Estimated geographic transit distance")
    estimated_duration_days: float = Field(..., description="Estimated voyage duration in days based on vessel speed")
    deadline_met: Optional[bool] = Field(None, description="Whether transit fits within deadline if specified")
    warning: str = Field(
        "Geographic distance is an idealized great-circle estimate. Actual maritime sea routes, TSS channels, and canal transit will vary.",
        description="Maritime navigation disclaimer",
    )


class RecommendationResult(BaseModel):
    """Recommended vessel class and decision reasoning."""
    recommended_vessel: Optional[str] = Field(None, description="Best suited vessel class or None if unavailable")
    status: RecommendationStatus = Field(..., description="Status of the recommendation")
    recommendation_confidence: RecommendationConfidence = Field(..., description="Confidence level in recommendation")
    reasoning: List[str] = Field(default_factory=list, description="Explicit bulleted justifications for selection")
    message: Optional[str] = Field(None, description="Optional explanatory message when no vessel is recommended")


class DataQualityReport(BaseModel):
    """Summary of data verification statuses across all components."""
    overall_status: OverallDataQuality = Field(..., description="Composite data quality level")
    origin_port_status: DataQualityStatus = Field(..., description="Data status of origin port")
    destination_port_status: DataQualityStatus = Field(..., description="Data status of destination port")
    vessel_data_status: DataQualityStatus = Field(..., description="Data status of vessel database")
    unverified_elements: List[str] = Field(default_factory=list, description="List of unverified or missing data fields")


class ShippingResponse(BaseModel):
    """Complete intelligence report for a shipping request."""
    request: Dict[str, Any] = Field(..., description="Echo of original request parameters")
    vessel_analysis: List[VesselAnalysisItem] = Field(..., description="Detailed feasibility for all vessel classes")
    recommendation: RecommendationResult = Field(..., description="Primary vessel recommendation and rationale")
    route_estimate: RouteEstimate = Field(..., description="Route distance and duration estimation")
    data_quality: DataQualityReport = Field(..., description="Data reliability audit report")
    # Phase 2 extension — optional so existing tests need no changes
    market_intelligence: Optional[Any] = Field(
        None,
        description="Market data snapshot and freight rate forecast (Phase 2). None if market data unavailable.",
    )
    # Phase 3 extensions — all optional, backward-compatible
    port_operations: Optional[Any] = Field(
        None,
        description="Operational congestion for origin and destination ports (Phase 3).",
    )
    risk_assessment: Optional[Any] = Field(
        None,
        description="Weather and marine risk score for the route (Phase 3).",
    )
    vessel_economics: Optional[Any] = Field(
        None,
        description="Voyage cost comparison across all vessel classes (Phase 3).",
    )
    # Phase 4 extension — integrated decision engine output
    decision: Optional[Any] = Field(
        None,
        description=(
            "Integrated charter decision: CHARTER NOW / WAIT / NEGOTIATE, "
            "with confidence, overall_score, factor_scores, and reasons (Phase 4)."
        ),
    )
