"""Test integration adapter using sample payloads from M1, M2, and M3."""

from adapter import adapt_team_inputs
from engine import evaluate_option, optimize_options


def test_team_payload_integration():
    m1_vessel_payload = {
        "estimated_total_freight_cost": 745824.0,
        "score": 88.0,
    }

    m2_market_payload = {
        "Volatility_4W_Pct": 12.5,
        "Historical_RMSE": 2.83,
        "Direction": "Increase",
    }

    m3_port_payload = {
        "congestion_score": 42.0,
        "average_waiting_days": 1.5,
    }

    adapted_input = adapt_team_inputs(
        option_id="Panamax_Option_1",
        vessel_data=m1_vessel_payload,
        market_data=m2_market_payload,
        port_data=m3_port_payload,
        cost_score=85.0,
    )

    result = evaluate_option(**adapted_input)

    assert result["option_id"] == "Panamax_Option_1"
    assert 0 <= result["decision_score"] <= 100


def test_team_multi_option_ranking():
    panamax_adapted = adapt_team_inputs(
        option_id="Panamax",
        vessel_data={"estimated_total_freight_cost": 745824.0, "score": 88.0},
        market_data={"Volatility_4W_Pct": 10.0, "Historical_RMSE": 2.0, "Direction": "Increase"},
        port_data={"congestion_score": 30.0, "average_waiting_days": 1.0},
        cost_score=85.0,
    )

    supramax_adapted = adapt_team_inputs(
        option_id="Supramax",
        vessel_data={"estimated_total_freight_cost": 750190.0, "score": 82.0},
        market_data={"Volatility_4W_Pct": 14.0, "Historical_RMSE": 2.5, "Direction": "Increase"},
        port_data={"congestion_score": 30.0, "average_waiting_days": 1.0},
        cost_score=80.0,
    )

    vessel_a = evaluate_option(**panamax_adapted)
    vessel_b = evaluate_option(**supramax_adapted)

    options_to_rank = [
        {"option_id": vessel_a["option_id"], "decision_score": vessel_a["decision_score"]},
        {"option_id": vessel_b["option_id"], "decision_score": vessel_b["decision_score"]},
    ]

    optimization_result = optimize_options(options_to_rank)

    assert len(optimization_result["ranked_options"]) == 2
    assert optimization_result["best_option"]["option_id"] in ["Panamax", "Supramax"]