"""
Scenario and what-if analysis for the M6 Decision & Optimization Engine.

Allows the system to test how changes in cost, risk, and market
conditions affect the final booking decision.
"""

from engine import evaluate_option


def apply_percentage_change(value, percentage):
    """
    Apply a percentage change to a numeric value.

    Example:
        10,000,000 with +10% -> 11,000,000
    """

    return value * (1 + percentage / 100)


def create_scenario(base_option, changes):
    """
    Create a modified copy of an option.

    `changes` contains field names and percentage changes.

    Example:
        {
            "freight_cost": 10,
            "port_congestion": 20
        }
    """

    scenario = base_option.copy()

    for field, percentage in changes.items():

        if field in scenario:
            scenario[field] = apply_percentage_change(
                scenario[field],
                percentage
            )

    return scenario


def evaluate_scenario(base_option, changes):
    """
    Apply scenario changes and run the modified option
    through the complete M6 decision engine.
    """

    scenario = create_scenario(
        base_option,
        changes
    )

    result = evaluate_option(
        option_id=scenario["option_id"],

        freight_cost=scenario["freight_cost"],
        charter_cost=scenario["charter_cost"],
        port_cost=scenario["port_cost"],
        delay_cost=scenario["delay_cost"],
        other_cost=scenario["other_cost"],

        freight_volatility=scenario["freight_volatility"],
        port_congestion=scenario["port_congestion"],
        vessel_reliability=scenario["vessel_reliability"],
        delay_probability=scenario["delay_probability"],
        forecast_uncertainty=scenario["forecast_uncertainty"],

        cost_score=scenario["cost_score"],
        forecast_score=scenario["forecast_score"],
        reliability_score=scenario["reliability_score"]
    )

    return result


def compare_scenario_results(base_result, scenario_result):
    """
    Compare the base decision with a scenario decision.
    """

    base_score = base_result["decision_score"]
    scenario_score = scenario_result["decision_score"]

    score_change = scenario_score - base_score

    return {
        "base_score": base_score,
        "scenario_score": scenario_score,
        "score_change": round(score_change, 2),
        "base_decision": base_result["booking_decision"]["decision"],
        "scenario_decision": scenario_result["booking_decision"]["decision"]
    }