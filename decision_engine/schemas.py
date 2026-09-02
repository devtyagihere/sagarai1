"""
Data schemas for the M6 Decision & Optimization Engine.

These schemas define the structure of data flowing through
the decision engine.
"""

from pydantic import BaseModel, Field


class CostBreakdown(BaseModel):
    """Breakdown of all major shipment costs."""

    freight_cost: float = Field(ge=0)
    charter_cost: float = Field(ge=0)
    port_cost: float = Field(ge=0)
    delay_cost: float = Field(ge=0)
    other_cost: float = Field(default=0, ge=0)
    total_cost: float = Field(ge=0)


class RiskAssessment(BaseModel):
    """Operational risk assessment."""

    freight_volatility: float = Field(ge=0, le=100)
    port_congestion: float = Field(ge=0, le=100)
    vessel_reliability: float = Field(ge=0, le=1)
    delay_probability: float = Field(ge=0, le=100)
    forecast_uncertainty: float = Field(ge=0, le=100)

    risk_score: float = Field(ge=0, le=100)
    risk_category: str


class DecisionScore(BaseModel):
    """Overall score used to compare booking options."""

    cost_score: float = Field(ge=0, le=100)
    risk_score: float = Field(ge=0, le=100)
    forecast_score: float = Field(ge=0, le=100)
    reliability_score: float = Field(ge=0, le=100)

    overall_score: float = Field(ge=0, le=100)


class BookingDecision(BaseModel):
    """Final actionable booking recommendation."""

    decision: str
    decision_score: float = Field(ge=0, le=100)
    risk_score: float = Field(ge=0, le=100)
    forecast_score: float = Field(ge=0, le=100)

    reasons: list[str]


class OptimizationOption(BaseModel):
    """A single vessel/route booking option."""

    option_id: str
    decision_score: float = Field(ge=0, le=100)
    rank: int | None = None


class OptimizationResult(BaseModel):
    """Result returned after comparing multiple options."""

    ranked_options: list[OptimizationOption]
    best_option_id: str | None