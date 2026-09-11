"""
Main Decision & Optimization Engine.

This module orchestrates the individual M6 components:
cost, risk, scoring, optimization, and booking.
"""

from cost import calculate_total_cost
from risk import calculate_risk_score, get_risk_category
from scoring import calculate_decision_score
from optimization import rank_options, get_best_option
from booking import make_booking_decision


def evaluate_option(
    option_id,
    freight_cost,
    charter_cost,
    port_cost,
    delay_cost,
    other_cost,
    freight_volatility,
    port_congestion,
    vessel_reliability,
    delay_probability,
    forecast_uncertainty,
    cost_score,
    forecast_score,
    reliability_score
):
    """
    Evaluate one booking option through the complete M6 pipeline.

    Returns a dictionary containing cost, risk, score,
    and booking decision information.
    """

    # -----------------------------------
    # 1. Calculate total cost
    # -----------------------------------

    cost_result = calculate_total_cost(
        freight_cost=freight_cost,
        charter_cost=charter_cost,
        port_cost=port_cost,
        delay_cost=delay_cost,
        other_cost=other_cost
    )

    # -----------------------------------
    # 2. Calculate risk
    # -----------------------------------

    risk_score = calculate_risk_score(
        freight_volatility=freight_volatility,
        port_congestion=port_congestion,
        vessel_reliability=vessel_reliability,
        delay_probability=delay_probability,
        forecast_uncertainty=forecast_uncertainty
    )

    risk_category = get_risk_category(risk_score)

    # -----------------------------------
    # 3. Calculate overall decision score
    # -----------------------------------

    decision_score = calculate_decision_score(
        cost_score=cost_score,
        risk_score=risk_score,
        forecast_score=forecast_score,
        reliability_score=reliability_score
    )

    # -----------------------------------
    # 4. Generate booking decision
    # -----------------------------------

    booking_decision = make_booking_decision(
        decision_score=decision_score,
        risk_score=risk_score,
        forecast_score=forecast_score
    )

    return {
        "option_id": option_id,
        "cost": cost_result,
        "risk": {
            "score": risk_score,
            "category": risk_category
        },
        "decision_score": decision_score,
        "booking_decision": booking_decision
    }


def optimize_options(options):
    """
    Rank already-evaluated options and return the best option.

    Each option must contain:
        option_id
        decision_score
    """

    ranked = rank_options(options)
    best = get_best_option(ranked)

    return {
        "ranked_options": ranked,
        "best_option": best
    }

from scoring import calculate_cost_scores


def evaluate_options(options):
    """
    Evaluate multiple booking options.

    Cost scores are calculated automatically based on the
    relative total cost of all available options.

    Parameters
    ----------
    options : list of dict
        Each option must contain the fields required by
        evaluate_option, except cost_score.

    Returns
    -------
    list of dict
        Fully evaluated options.
    """

    # -----------------------------------
    # 1. Calculate total cost for each option
    # -----------------------------------

    cost_results = []

    for option in options:

        cost_result = calculate_total_cost(
            freight_cost=option["freight_cost"],
            charter_cost=option["charter_cost"],
            port_cost=option["port_cost"],
            delay_cost=option["delay_cost"],
            other_cost=option.get("other_cost", 0)
        )

        cost_results.append(cost_result)

    # -----------------------------------
    # 2. Extract total costs
    # -----------------------------------

    total_costs = [
        result["total_cost"]
        for result in cost_results
    ]

    # -----------------------------------
    # 3. Automatically calculate cost scores
    # -----------------------------------

    cost_scores = calculate_cost_scores(total_costs)

    # -----------------------------------
    # 4. Evaluate every option
    # -----------------------------------

    evaluated_options = []

    for option, cost_score in zip(options, cost_scores):

        evaluated = evaluate_option(
            option_id=option["option_id"],

            freight_cost=option["freight_cost"],
            charter_cost=option["charter_cost"],
            port_cost=option["port_cost"],
            delay_cost=option["delay_cost"],
            other_cost=option.get("other_cost", 0),

            freight_volatility=option["freight_volatility"],
            port_congestion=option["port_congestion"],
            vessel_reliability=option["vessel_reliability"],
            delay_probability=option["delay_probability"],
            forecast_uncertainty=option["forecast_uncertainty"],

            cost_score=cost_score,
            forecast_score=option["forecast_score"],
            reliability_score=option["reliability_score"]
        )

        evaluated_options.append(evaluated)

    return evaluated_options