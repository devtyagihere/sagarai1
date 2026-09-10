import math


# --------------------------------------------------
# MARINE RISK SCORE
# --------------------------------------------------

def calculate_marine_risk(
    wave_height,
    wave_period
):
    """
    Calculate a 0-100 marine risk score.

    Higher wave height and long-period waves
    increase the marine risk.
    """

    # --------------------------------------------------
    # MISSING DATA
    # --------------------------------------------------

    if wave_height is None:
        return {
            "marine_risk_score": None,
            "marine_risk_level": "Unavailable"
        }

    if wave_period is None:
        return {
            "marine_risk_score": None,
            "marine_risk_level": "Unavailable"
        }

    try:
        wave_height = float(wave_height)
        wave_period = float(wave_period)

    except (TypeError, ValueError):

        return {
            "marine_risk_score": None,
            "marine_risk_level": "Unavailable"
        }

    # --------------------------------------------------
    # WAVE HEIGHT RISK
    # --------------------------------------------------

    if wave_height < 1.0:

        height_score = 0

    elif wave_height < 1.5:

        height_score = 20

    elif wave_height < 2.0:

        height_score = 40

    elif wave_height < 3.0:

        height_score = 60

    elif wave_height < 4.0:

        height_score = 80

    else:

        height_score = 100

    # --------------------------------------------------
    # WAVE PERIOD RISK
    # --------------------------------------------------

    if wave_period < 7:

        period_score = 0

    elif wave_period < 9:

        period_score = 20

    elif wave_period < 11:

        period_score = 40

    elif wave_period < 13:

        period_score = 60

    elif wave_period < 15:

        period_score = 80

    else:

        period_score = 100

    # --------------------------------------------------
    # COMBINE RISKS
    # --------------------------------------------------

    marine_risk_score = (
        0.7 * height_score
        +
        0.3 * period_score
    )

    marine_risk_score = round(
        marine_risk_score,
        2
    )

    # --------------------------------------------------
    # RISK LEVEL
    # --------------------------------------------------

    if marine_risk_score < 25:

        risk_level = "Low"

    elif marine_risk_score < 50:

        risk_level = "Moderate"

    elif marine_risk_score < 75:

        risk_level = "High"

    else:

        risk_level = "Severe"

    return {
        "marine_risk_score": marine_risk_score,
        "marine_risk_level": risk_level
    }


# --------------------------------------------------
# DIRECT TEST
# --------------------------------------------------

if __name__ == "__main__":

    print("\n========== MARINE RISK TEST ==========")

    wave_height = float(
        input("Enter wave height (m): ")
    )

    wave_period = float(
        input("Enter wave period (s): ")
    )

    result = calculate_marine_risk(
        wave_height,
        wave_period
    )

    print(
        "\nMarine Risk Score:",
        result["marine_risk_score"]
    )

    print(
        "Marine Risk Level:",
        result["marine_risk_level"]
    )