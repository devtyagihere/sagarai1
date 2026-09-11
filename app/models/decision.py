"""
Pydantic models for Phase 4 — Integrated Decision Engine.

DecisionResult is the final output that combines all upstream module signals
into a single transparent CHARTER NOW / WAIT / NEGOTIATE action.
"""

from typing import Dict, List, Optional
from pydantic import BaseModel, Field


class FactorScore(BaseModel):
    """
    Score for a single decision factor.

    raw_value   — the input value extracted from upstream module output
                  (e.g. BDI direction, congestion score, forecast % change)
    score       — normalised 0-100 score (100 = most favourable to charter now)
    weight      — the weight of this factor in the overall score (0-1)
    contribution— score × weight -> partial contribution to overall_score
    signal      — human-readable verdict for this factor
    """
    factor_name: str = Field(..., description="Factor identifier (e.g. 'freight_trend')")
    raw_value: Optional[float] = Field(None, description="Raw numeric input used to derive the score")
    raw_label: Optional[str] = Field(None, description="Raw label/direction input (e.g. 'up', 'LOW-MODERATE')")
    score: float = Field(..., ge=0, le=100, description="Normalised factor score (0=worst, 100=best for chartering)")
    weight: float = Field(..., description="Factor weight (sum of all weights = 1.0)")
    contribution: float = Field(..., description="score x weight -- partial contribution to overall_score")
    signal: str = Field(..., description="Human-readable verdict for this factor")
    data_available: bool = Field(True, description="False if underlying data was missing/unavailable")


class DecisionResult(BaseModel):
    """
    Final integrated charter decision.

    action      — CHARTER NOW / WAIT / NEGOTIATE
    confidence  — HIGH / MODERATE / LOW
    overall_score — weighted sum of all factor scores (0-100)
    """

    # -- Core Decision -------------------------------------------------------
    action: str = Field(
        ...,
        description="Recommended action: 'CHARTER NOW', 'WAIT', or 'NEGOTIATE'",
    )
    confidence: str = Field(
        ...,
        description="Decision confidence: HIGH / MODERATE / LOW",
    )
    overall_score: float = Field(
        ..., ge=0, le=100,
        description=(
            "Composite score 0-100. "
            ">=65 -> CHARTER NOW, 40-64 -> NEGOTIATE, <40 -> WAIT"
        ),
    )

    # -- Recommended Vessel -------------------------------------------------
    recommended_vessel: Optional[str] = Field(
        None,
        description="Best vessel class recommended by FeasibilityEngine + ScoringEngine",
    )
    feasible_vessel_available: bool = Field(
        False,
        description="True if at least one vessel class passed feasibility checks",
    )

    # -- Factor Breakdown ----------------------------------------------------
    factor_scores: List[FactorScore] = Field(
        default_factory=list,
        description="Per-factor score breakdown -- fully transparent",
    )
    factors_available: int = Field(
        0,
        description="Number of factors for which data was available (max 7)",
    )
    factors_total: int = Field(7, description="Total number of decision factors")

    # -- Reasoning -----------------------------------------------------------
    reasons: List[str] = Field(
        default_factory=list,
        description="Ordered list of plain-English reasons supporting the decision",
    )
    confidence_rationale: str = Field(
        "",
        description="Explanation of why this confidence level was assigned",
    )

    # -- Formula Documentation -----------------------------------------------
    formula_note: str = Field(
        (
            "overall_score = sum(factor_score_i * weight_i) across 7 factors. "
            "Weights: freight_trend=0.20, bdi_trend=0.15, oil_trend=0.10, "
            "commodity_trend=0.10, port_congestion=0.15, risk=0.15, vessel_economics=0.15. "
            "Thresholds: >=65 -> CHARTER NOW, 40-64 -> NEGOTIATE, <40 -> WAIT."
        ),
        description="Documented formula for overall_score and decision thresholds",
    )
    data_source: str = Field(
        "SYNTHETIC",
        description="Data provenance label -- all inputs are from SYNTHETIC datasets",
    )
    disclaimer: str = Field(
        (
            "Decision scores are computed from SYNTHETIC market data. "
            "This is an educational demonstration -- not suitable for real charter decisions."
        ),
        description="Mandatory data disclaimer",
    )
