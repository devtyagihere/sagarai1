"""
Adapter layer to map real outputs from M1, M2, and M3
into the M6 Decision Engine input formats.
"""

from typing import Any, Dict


def adapt_team_inputs(
    option_id: str,
    vessel_data: Dict[str, Any],
    market_data: Dict[str, Any],
    port_data: Dict[str, Any],
    cost_score: float = 80.0,
    charter_cost: float = 0.0,
    port_cost: float = 0.0,
    delay_cost: float = 0.0,
    other_cost: float = 0.0,
) -> Dict[str, Any]:
    """
    Combines outputs from M1, M2, and M3 into the format required
    by decision_engine.engine.evaluate_option().
    """
    freight_cost = float(
        vessel_data.get("estimated_total_freight_cost", 0.0)
        or vessel_data.get("freight_cost", 0.0)
    )

    freight_volatility = float(
        market_data.get("Volatility_4W_Pct", 15.0)
    )

    rmse = market_data.get("Historical_RMSE", 10.0)
    forecast_uncertainty = min(100.0, max(0.0, float(rmse) * 5.0))

    port_congestion = float(
        port_data.get("congestion_score", 0.0)
    )

    raw_reliability = float(
        vessel_data.get("score", 85.0)
        if vessel_data.get("score") is not None
        else 85.0
    )
    vessel_reliability = max(0.0, min(1.0, raw_reliability / 100.0))

    avg_wait = float(port_data.get("average_waiting_days", 1.0))
    delay_probability = min(100.0, max(0.0, avg_wait * 15.0))

    direction = market_data.get("Direction", "Stable")
    if direction == "Increase":
        forecast_score = 75.0
    elif direction == "Decrease":
        forecast_score = 30.0
    else:
        forecast_score = 50.0

    reliability_score = raw_reliability

    return {
        "option_id": option_id,
        "freight_cost": freight_cost,
        "charter_cost": charter_cost,
        "port_cost": port_cost,
        "delay_cost": delay_cost,
        "other_cost": other_cost,
        "freight_volatility": freight_volatility,
        "port_congestion": port_congestion,
        "vessel_reliability": vessel_reliability,
        "delay_probability": delay_probability,
        "forecast_uncertainty": forecast_uncertainty,
        "cost_score": cost_score,
        "forecast_score": forecast_score,
        "reliability_score": reliability_score,
    }