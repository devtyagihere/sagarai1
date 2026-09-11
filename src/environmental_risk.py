# --------------------------------------------------
# COMBINED ENVIRONMENTAL RISK
# --------------------------------------------------

def calculate_environmental_risk(
    weather_disruption,
    marine_risk_score
):

    # --------------------------------------------------
    # MISSING DATA
    # --------------------------------------------------

    if weather_disruption is None:
        return {
            "environmental_risk_score": None,
            "environmental_risk_level": "Unavailable"
        }

    if marine_risk_score is None:
        return {
            "environmental_risk_score": None,
            "environmental_risk_level": "Unavailable"
        }

    # --------------------------------------------------
    # CONVERT WEATHER DISRUPTION TO 0-100
    # --------------------------------------------------

    weather_score = (
        100
        if int(weather_disruption) == 1
        else 0
    )

    # --------------------------------------------------
    # COMBINE WEATHER + MARINE
    # --------------------------------------------------

    environmental_risk_score = (
        0.4 * weather_score
        +
        0.6 * float(marine_risk_score)
    )

    environmental_risk_score = round(
        environmental_risk_score,
        2
    )

    # --------------------------------------------------
    # RISK LEVEL
    # --------------------------------------------------

    if environmental_risk_score < 25:

        risk_level = "Low"

    elif environmental_risk_score < 50:

        risk_level = "Moderate"

    elif environmental_risk_score < 75:

        risk_level = "High"

    else:

        risk_level = "Severe"

    return {
        "environmental_risk_score":
            environmental_risk_score,

        "environmental_risk_level":
            risk_level
    }


# --------------------------------------------------
# DIRECT TEST
# --------------------------------------------------

if __name__ == "__main__":

    print(
        "\n========== ENVIRONMENTAL RISK TEST =========="
    )

    weather_disruption = int(
        input(
            "Enter weather disruption (0/1): "
        )
    )

    marine_risk_score = float(
        input(
            "Enter marine risk score (0-100): "
        )
    )

    result = calculate_environmental_risk(
        weather_disruption,
        marine_risk_score
    )

    print(
        "\nEnvironmental Risk Score:",
        result["environmental_risk_score"]
    )

    print(
        "Environmental Risk Level:",
        result["environmental_risk_level"]
    )