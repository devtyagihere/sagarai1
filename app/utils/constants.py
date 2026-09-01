"""Constants, Enums, and Standardization maps for Maritime Intelligence."""

from enum import Enum


class FeasibilityStatus(str, Enum):
    """Feasibility outcome for a vessel evaluated against a shipping request."""
    FEASIBLE = "feasible"
    CONDITIONALLY_FEASIBLE = "conditionally_feasible"
    NOT_FEASIBLE = "not_feasible"
    INSUFFICIENT_DATA = "insufficient_data"


class DataQualityStatus(str, Enum):
    """Reliability status for dataset attributes."""
    VERIFIED = "verified"
    ESTIMATED = "estimated"
    DEMO = "demo"
    MISSING = "missing"


class OverallDataQuality(str, Enum):
    """Aggregated data quality rating for the analysis."""
    FULLY_VERIFIED = "fully_verified"
    PARTIALLY_VERIFIED = "partially_verified"
    ESTIMATED = "estimated"
    INSUFFICIENT = "insufficient"


class RecommendationStatus(str, Enum):
    """Status of the recommendation engine selection."""
    RECOMMENDED = "recommended"
    CONDITIONALLY_RECOMMENDED = "conditionally_recommended"
    NO_FEASIBLE_VESSEL = "no_feasible_vessel"
    INSUFFICIENT_DATA = "insufficient_data"


class RecommendationConfidence(str, Enum):
    """Confidence level in the recommended vessel."""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    NONE = "none"


class CargoCategory(str, Enum):
    """Major cargo category classifications."""
    DRY_BULK = "dry_bulk"
    BREAK_BULK = "break_bulk"
    GENERAL_CARGO = "general_cargo"
