from scenarios import evaluate_scenario, compare_scenario_results
from engine import evaluate_option


def get_base_option():
    return {
        "option_id": "VESSEL_C",
        "freight_cost": 8500000,
        "charter_cost": 2600000,
        "port_cost": 500000,
        "delay_cost": 50000,
        "other_cost": 100000,
        "freight_volatility": 25,
        "port_congestion": 20,
        "vessel_reliability": 0.95,
        "delay_probability": 10,
        "forecast_uncertainty": 10,
        "cost_score": 75,
        "forecast_score": 90,
        "reliability_score": 95
    }


def get_base_result(option):
    return evaluate_option(
        option_id=option["option_id"],
        freight_cost=option["freight_cost"],
        charter_cost=option["charter_cost"],
        port_cost=option["port_cost"],
        delay_cost=option["delay_cost"],
        other_cost=option["other_cost"],
        freight_volatility=option["freight_volatility"],
        port_congestion=option["port_congestion"],
        vessel_reliability=option["vessel_reliability"],
        delay_probability=option["delay_probability"],
        forecast_uncertainty=option["forecast_uncertainty"],
        cost_score=option["cost_score"],
        forecast_score=option["forecast_score"],
        reliability_score=option["reliability_score"]
    )


def test_freight_cost_scenario():
    option = get_base_option()
    base_result = get_base_result(option)

    scenario_result = evaluate_scenario(
        option,
        {"freight_cost": 10}
    )

    comparison = compare_scenario_results(
        base_result,
        scenario_result
    )

    assert "scenario_score" in comparison
    assert "score_change" in comparison
    assert "scenario_decision" in comparison


def test_port_congestion_scenario():
    option = get_base_option()
    base_result = get_base_result(option)

    scenario_result = evaluate_scenario(
        option,
        {"port_congestion": 20}
    )

    comparison = compare_scenario_results(
        base_result,
        scenario_result
    )

    assert "scenario_score" in comparison
    assert "score_change" in comparison
    assert "scenario_decision" in comparison


def test_delay_probability_scenario():
    option = get_base_option()
    base_result = get_base_result(option)

    scenario_result = evaluate_scenario(
        option,
        {"delay_probability": 30}
    )

    comparison = compare_scenario_results(
        base_result,
        scenario_result
    )

    assert "scenario_score" in comparison
    assert "score_change" in comparison
    assert "scenario_decision" in comparison