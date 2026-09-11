from risk import calculate_risk_score, get_risk_category


def test_risk_assessment():
    risk_score = calculate_risk_score(
        freight_volatility=40,
        port_congestion=30,
        vessel_reliability=0.90,
        delay_probability=20,
        forecast_uncertainty=15
    )

    category = get_risk_category(risk_score)

    assert 0 <= risk_score <= 100
    assert category in ["LOW", "MODERATE", "HIGH", "VERY HIGH"]