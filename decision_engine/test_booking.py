from booking import make_booking_decision


def test_good_booking_option():
    result = make_booking_decision(
        decision_score=85,
        risk_score=25,
        forecast_score=85
    )

    assert result is not None


def test_poor_booking_option():
    result = make_booking_decision(
        decision_score=40,
        risk_score=45,
        forecast_score=35
    )

    assert result is not None


def test_high_risk_booking_option():
    result = make_booking_decision(
        decision_score=80,
        risk_score=85,
        forecast_score=90
    )

    assert result is not None