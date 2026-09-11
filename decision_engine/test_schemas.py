from schemas import (
    CostBreakdown,
    RiskAssessment,
    DecisionScore,
    BookingDecision,
    OptimizationOption,
    OptimizationResult
)


def test_all_schemas():
    cost = CostBreakdown(
        freight_cost=8000000,
        charter_cost=2500000,
        port_cost=700000,
        delay_cost=100000,
        other_cost=200000,
        total_cost=11500000
    )

    risk = RiskAssessment(
        freight_volatility=40,
        port_congestion=30,
        vessel_reliability=0.90,
        delay_probability=20,
        forecast_uncertainty=15,
        risk_score=25.5,
        risk_category="MODERATE"
    )

    score = DecisionScore(
        cost_score=80,
        risk_score=25.5,
        forecast_score=85,
        reliability_score=90,
        overall_score=80.5
    )

    decision = BookingDecision(
        decision="BOOK_NOW",
        decision_score=80.5,
        risk_score=25.5,
        forecast_score=85,
        reasons=[
            "Overall decision score is strong.",
            "Risk is within the acceptable range."
        ]
    )

    options = [
        OptimizationOption(
            option_id="VESSEL_A",
            decision_score=80.5,
            rank=1
        ),
        OptimizationOption(
            option_id="VESSEL_B",
            decision_score=72.0,
            rank=2
        )
    ]

    result = OptimizationResult(
        ranked_options=options,
        best_option_id="VESSEL_A"
    )

    assert cost.total_cost == 11500000
    assert risk.risk_category == "MODERATE"
    assert score.overall_score == 80.5
    assert decision.decision == "BOOK_NOW"
    assert len(result.ranked_options) == 2
    assert result.best_option_id == "VESSEL_A"