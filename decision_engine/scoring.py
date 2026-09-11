"""
Decision scoring module for the freight intelligence system.

Combines cost, risk, forecast opportunity,
and vessel reliability into one decision score.
"""

from config import DECISION_WEIGHTS


def calculate_decision_score(
    cost_score,
    risk_score,
    forecast_score,
    reliability_score
):
    """
    Calculate an overall decision score from 0 to 100.

    Higher score = better option.

    Parameters
    ----------
    cost_score : float
        Score from 0-100 where higher means lower cost.

    risk_score : float
        Risk from 0-100 where higher means more risk.

    forecast_score : float
        Score from 0-100 where higher means a better
        freight-market opportunity.

    reliability_score : float
        Score from 0-100 where higher means more reliable.

    Returns
    -------
    float
        Overall decision score from 0-100.
    """

    # Convert risk into a positive score.
    risk_score_positive = 100 - risk_score

    decision_score = (
        cost_score * DECISION_WEIGHTS["cost"]
        + risk_score_positive * DECISION_WEIGHTS["risk"]
        + forecast_score * DECISION_WEIGHTS["forecast"]
        + reliability_score * DECISION_WEIGHTS["reliability"]
    )

    return round(decision_score, 2) 

def calculate_cost_scores(costs):
    """
    Convert a list of total costs into normalized scores from 0 to 100.

    Lower cost = higher score.

    Parameters
    ----------
    costs : list of float
        Total costs for available options.

    Returns
    -------
    list of float
        Cost scores corresponding to the input costs.
    """

    if not costs:
        return []

    if any(cost < 0 for cost in costs):
        raise ValueError("Costs cannot be negative.")

    min_cost = min(costs)
    max_cost = max(costs)

    # If every option has the same cost,
    # give every option a neutral score.
    if min_cost == max_cost:
        return [100.0 for _ in costs]

    scores = []

    for cost in costs:

        score = (
            (max_cost - cost)
            / (max_cost - min_cost)
        ) * 100

        scores.append(round(score, 2))

    return scores