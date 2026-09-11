"""
Risk calculation module for the freight intelligence system.
"""

from config import RISK_WEIGHTS


def calculate_risk_score(
    freight_volatility,
    port_congestion,
    vessel_reliability,
    delay_probability,
    forecast_uncertainty
):
    """
    Calculate an overall operational risk score from 0 to 100.

    Higher score = higher risk.
    """

    # Reliability is normally represented as:
    # 0 = unreliable
    # 1 = highly reliable
    #
    # Therefore, convert it into a risk value.
    vessel_reliability_risk = (1 - vessel_reliability) * 100

    risk_score = (
        freight_volatility * RISK_WEIGHTS["freight_volatility"]
        + port_congestion * RISK_WEIGHTS["port_congestion"]
        + vessel_reliability_risk * RISK_WEIGHTS["vessel_reliability"]
        + delay_probability * RISK_WEIGHTS["delay_probability"]
        + forecast_uncertainty * RISK_WEIGHTS["forecast_uncertainty"]
    )

    return round(risk_score, 2)


def get_risk_category(risk_score):
    """
    Convert a numerical risk score into a category.
    """

    if risk_score <= 25:
        return "LOW"

    elif risk_score <= 50:
        return "MODERATE"

    elif risk_score <= 75:
        return "HIGH"

    else:
        return "VERY HIGH"