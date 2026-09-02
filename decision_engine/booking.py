"""
Booking decision module for the freight intelligence system.

Converts the optimization result into an actionable
booking recommendation.
"""

from config import BOOK_THRESHOLD, WAIT_THRESHOLD


def make_booking_decision(
    decision_score,
    risk_score,
    forecast_score
):
    """
    Generate a booking recommendation.

    Parameters
    ----------
    decision_score : float
        Overall decision score from 0-100.

    risk_score : float
        Risk score from 0-100.
        Higher means greater risk.

    forecast_score : float
        Forecast opportunity score from 0-100.
        Higher means a better opportunity to book.

    Returns
    -------
    dict
        Booking decision and explanation.
    """

    reasons = []

    # Very high risk should prevent an immediate booking.
    if risk_score >= 75:
        decision = "CHOOSE_ALTERNATIVE"
        reasons.append("Operational risk is very high.")

    # Strong overall score and acceptable risk.
    elif decision_score >= BOOK_THRESHOLD and risk_score <= 50:
        decision = "BOOK_NOW"
        reasons.append("Overall decision score is strong.")
        reasons.append("Risk is within the acceptable range.")

        if forecast_score >= 75:
            reasons.append(
                "Freight market conditions favor booking now."
            )

    # Weak score means waiting may be preferable.
    elif decision_score < WAIT_THRESHOLD:
        decision = "WAIT"
        reasons.append(
            "Overall decision score is below the booking threshold."
        )

        if forecast_score < 50:
            reasons.append(
                "Current freight-market opportunity is weak."
            )

    # Everything else is uncertain.
    else:
        decision = "WAIT"
        reasons.append(
            "The option does not have enough advantage "
            "to justify immediate booking."
        )

    return {
        "decision": decision,
        "decision_score": decision_score,
        "risk_score": risk_score,
        "forecast_score": forecast_score,
        "reasons": reasons
    }