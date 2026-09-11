"""Port data models and constraint definitions."""

from typing import List, Optional
from pydantic import BaseModel, Field, field_validator
from app.utils.constants import DataQualityStatus


class Port(BaseModel):
    """Port entity with geographic coordinates and physical operational constraints."""
    port_name: str = Field(..., description="Standardized name of the port")
    country: str = Field(..., description="Country where the port is located")
    latitude: float = Field(..., description="Port latitude coordinate")
    longitude: float = Field(..., description="Port longitude coordinate")
    max_draft_m: Optional[float] = Field(None, description="Maximum permissible vessel draft in meters")
    max_length_m: Optional[float] = Field(None, description="Maximum permissible vessel LOA in meters")
    max_beam_m: Optional[float] = Field(None, description="Maximum permissible vessel beam in meters")
    data_status: DataQualityStatus = Field(DataQualityStatus.VERIFIED, description="Data verification status")
    source: str = Field(..., description="Official handbook, port tariff or data source")
    last_verified: Optional[str] = Field(None, description="ISO date when port specifications were last verified")

    @field_validator("latitude")
    @classmethod
    def validate_latitude(cls, v: float) -> float:
        if not (-90.0 <= v <= 90.0):
            raise ValueError("Latitude must be between -90 and 90 degrees")
        return v

    @field_validator("longitude")
    @classmethod
    def validate_longitude(cls, v: float) -> float:
        if not (-180.0 <= v <= 180.0):
            raise ValueError("Longitude must be between -180 and 180 degrees")
        return v

    def is_verified(self) -> bool:
        """Check if port data is officially verified."""
        return self.data_status == DataQualityStatus.VERIFIED

    def get_missing_constraints(self) -> List[str]:
        """Identify which operational constraints are unrecorded/missing."""
        missing = []
        if self.max_draft_m is None:
            missing.append("max_draft_m")
        if self.max_length_m is None:
            missing.append("max_length_m")
        if self.max_beam_m is None:
            missing.append("max_beam_m")
        return missing

    def has_complete_constraints(self) -> bool:
        """Return True if all physical limits (draft, length, beam) are present."""
        return len(self.get_missing_constraints()) == 0
