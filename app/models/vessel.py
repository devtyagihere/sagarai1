"""Vessel data models and feasibility assessment structures."""

from typing import Dict, List, Optional
from pydantic import BaseModel, Field
from app.utils.constants import DataQualityStatus, FeasibilityStatus


class Vessel(BaseModel):
    """Vessel class specification and physical parameters."""
    vessel_class: str = Field(..., description="Classification name (e.g., Handysize, Supramax)")
    min_capacity_tonnes: float = Field(..., description="Minimum commercial parcel deadweight in tonnes")
    max_capacity_tonnes: float = Field(..., description="Maximum deadweight carrying capacity in tonnes")
    typical_draft_m: float = Field(..., description="Typical laden draft in meters")
    typical_length_m: float = Field(..., description="Typical overall length (LOA) in meters")
    typical_beam_m: float = Field(..., description="Typical vessel beam in meters")
    avg_speed_knots: float = Field(..., description="Average laden sea speed in knots")
    supported_cargo: List[str] = Field(default_factory=list, description="List of compatible cargo types")
    data_status: DataQualityStatus = Field(DataQualityStatus.VERIFIED, description="Data verification status")
    source: str = Field(..., description="Maritime classification reference or standard source")


class ScoreBreakdown(BaseModel):
    """Granular multi-criteria breakdown of vessel score."""
    capacity_utilization: float = Field(..., description="Points earned from payload efficiency (0-100 normalized)")
    port_confidence: float = Field(..., description="Points earned from port data verification confidence")
    cargo_compatibility: float = Field(..., description="Points earned from cargo-specific fit")
    operational_efficiency: float = Field(..., description="Points earned from sea speed and size optimization")


class VesselAnalysisItem(BaseModel):
    """Detailed evaluation result for a single vessel class."""
    vessel_class: str = Field(..., description="Evaluated vessel class")
    feasibility_status: FeasibilityStatus = Field(..., description="Feasibility state outcome")
    checks: Dict[str, Optional[bool]] = Field(default_factory=dict, description="Detailed boolean check matrix")
    capacity_utilization: float = Field(..., description="Ratio of cargo quantity to maximum capacity")
    score: Optional[float] = Field(None, description="Composite suitability score (0-100)")
    score_breakdown: Optional[ScoreBreakdown] = Field(None, description="Detailed scoring criteria breakdown")
    warnings: List[str] = Field(default_factory=list, description="Operational or data warnings")
    rejection_reasons: List[str] = Field(default_factory=list, description="Reasons why vessel was rejected")
    data_status: DataQualityStatus = Field(DataQualityStatus.VERIFIED, description="Quality status of vessel specs")
