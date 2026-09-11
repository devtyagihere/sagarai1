"""
Scenario and what-if analysis for the M6 Decision & Optimization Engine.

Allows the system to test how changes in cost, risk, and market
conditions affect the final booking decision.
"""

from engine import (
    evaluate_option,
    evaluate_options
)

from optimization import (
    rank_options,
    get_best_option
)


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

def evaluate_multi_option_scenario(options, option_id, changes):
    """
    Evaluate a what-if scenario for one option while keeping
    the other available options unchanged.

    Parameters
    ----------
    options : list of dict
        Available booking options.

    option_id : str
        ID of the option being modified.

    changes : dict
        Percentage changes to apply.

    Returns
    -------
    dict
        Ranked scenario results and best option.
    """

    # Create independent copies so the original options
    # are not modified.
    scenario_options = [
        option.copy()
        for option in options
    ]

    # Find the selected option.
    selected_option = None

    for option in scenario_options:
        if option["option_id"] == option_id:
            selected_option = option
            break

    if selected_option is None:
        raise ValueError(
            f"Option '{option_id}' was not found."
        )

    # Apply the requested percentage changes.
    for field, percentage in changes.items():

        if field not in selected_option:
            raise ValueError(
                f"Field '{field}' does not exist "
                f"for option '{option_id}'."
            )

        selected_option[field] = apply_percentage_change(
            selected_option[field],
            percentage
        )

    # Recalculate all options.
    evaluated_options = evaluate_options(
        scenario_options
    )

    # Extract information needed for optimization.
    optimization_options = [
        {
            "option_id": option["option_id"],
            "decision_score": option["decision_score"]
        }
        for option in evaluated_options
    ]

    optimized = rank_options(
        optimization_options
    )

    return {
        "evaluated_options": evaluated_options,
        "ranked_options": optimized,
        "best_option": get_best_option(optimized)
    }