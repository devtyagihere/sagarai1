"""
Pydantic models for Phase 3 — Port Operations, Risk Assessment, Vessel Economics.
"""
from typing import List, Optional
from pydantic import BaseModel, Field


# ── Port Operations ──────────────────────────────────────────────────────────

class PortCongestion(BaseModel):
    """Operational congestion state for a single port."""
    port_name: str
    vessels_working: int       = Field(..., description="Active vessels at berth")
    vessels_waiting: int       = Field(..., description="Vessels at anchorage waiting for berth")
    congestion_score: float    = Field(..., ge=0, le=100, description="Composite congestion score 0-100")
    congestion_level: str      = Field(..., description="LOW / LOW-MODERATE / MODERATE / HIGH / VERY HIGH")
    average_waiting_days: float= Field(..., description="Current average vessel waiting time (days)")
    congestion_forecast_7d: float  = Field(..., description="Projected congestion score in 7 days")
    congestion_forecast_15d: float = Field(..., description="Projected congestion score in 15 days")
    congestion_forecast_30d: float = Field(..., description="Projected congestion score in 30 days")
    data_source: str           = Field("SYNTHETIC", description="Data provenance: SYNTHETIC/DEMO/REAL")
    formula_used: str          = Field("", description="Documented formula for congestion_score")


class PortOperationsResult(BaseModel):
    """Congestion data for both origin and destination ports."""
    origin: Optional[PortCongestion]      = None
    destination: Optional[PortCongestion] = None
    combined_delay_risk: str              = Field("", description="Worst-case delay risk label")
    data_source: str                      = Field("SYNTHETIC")


# ── Risk Assessment ──────────────────────────────────────────────────────────

class WeatherRisk(BaseModel):
    wind_speed_bft: float       = Field(..., description="Beaufort scale wind estimate (0-12)")
    wave_height_m: float        = Field(..., description="Estimated significant wave height (metres)")
    storm_probability_pct: float= Field(..., description="Probability of storm encounter (0-100 %)")
    weather_risk_score: float   = Field(..., ge=0, le=100)


class MarineRisk(BaseModel):
    sea_state: str              = Field(..., description="WMO sea state descriptor")
    cyclone_risk_pct: float     = Field(..., description="Seasonal cyclone encounter probability (0-100 %)")
    environmental_sensitivity: float = Field(..., ge=0, le=100,
                                            description="Ecological sensitivity index of route (0-100)")
    marine_risk_score: float    = Field(..., ge=0, le=100)


class RiskAssessment(BaseModel):
    """Full risk assessment for a maritime route."""
    route: str                  = Field(..., description="Origin → Destination")
    month_assessed: str         = Field(..., description="Month of assessment (YYYY-MM)")
    weather_risk: WeatherRisk
    marine_risk: MarineRisk
    overall_risk_score: float   = Field(..., ge=0, le=100,
        description="Composite 0-100 score: 0=very low, 100=very high")
    risk_level: str             = Field(...,
        description="LOW / LOW-MODERATE / MODERATE / HIGH / VERY HIGH")
    key_hazards: List[str]      = Field(default_factory=list,
        description="Top risk factors driving the overall score")
    data_source: str            = Field("SYNTHETIC")
    formula_note: str           = Field("",
        description="Documented formula used to compute scores")


# ── Vessel Economics ─────────────────────────────────────────────────────────

class VesselEconomicsItem(BaseModel):
    """Cost estimate for one vessel class on the proposed voyage."""
    vessel_class: str
    daily_rate_usd: int         = Field(..., description="Charter/hire rate USD per day")
    voyage_days: float          = Field(..., description="Estimated voyage duration in days")
    voyage_cost_usd: float      = Field(..., description="voyage_cost = daily_rate × voyage_days")
    cost_per_mt_usd: float      = Field(..., description="cost_per_mt = voyage_cost / cargo_quantity")
    cargo_quantity_tonnes: float= Field(..., description="Cargo quantity used for cost_per_mt")
    feasibility_status: str     = Field(..., description="FEASIBLE / CONDITIONALLY_FEASIBLE / NOT_FEASIBLE")
    is_recommended: bool        = Field(False, description="True for the recommended vessel")


class VesselEconomicsResult(BaseModel):
    """Voyage economics comparison across all vessel classes."""
    cargo_quantity_tonnes: float
    voyage_days: float          = Field(..., description="Voyage days for recommended vessel")
    comparison: List[VesselEconomicsItem] = Field(default_factory=list,
        description="All vessels sorted by cost_per_mt ascending (feasible first)")
    cheapest_feasible_vessel: Optional[str] = None
    recommended_vessel: Optional[str]       = None
    data_source: str            = Field("SYNTHETIC",
        description="Daily rate data source (SYNTHETIC/DEMO/REAL)")
    formula_note: str           = Field(
        "voyage_cost = daily_rate_usd × voyage_days; "
        "cost_per_mt = voyage_cost / cargo_quantity_tonnes",
        description="Cost formulas used"
    )
