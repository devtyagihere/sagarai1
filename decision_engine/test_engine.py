from engine import evaluate_option, optimize_options


def test_decision_engine_end_to_end():
    vessel_a = evaluate_option(
        option_id="VESSEL_A",
        freight_cost=8000000,
        charter_cost=2500000,
        port_cost=700000,
        delay_cost=100000,
        other_cost=200000,
        freight_volatility=40,
        port_congestion=30,
        vessel_reliability=0.90,
        delay_probability=20,
        forecast_uncertainty=15,
        cost_score=80,
        forecast_score=85,
        reliability_score=90
    )

    vessel_b = evaluate_option(
        option_id="VESSEL_B",
        freight_cost=7500000,
        charter_cost=2300000,
        port_cost=900000,
        delay_cost=300000,
        other_cost=150000,
        freight_volatility=55,
        port_congestion=50,
        vessel_reliability=0.82,
        delay_probability=35,
        forecast_uncertainty=25,
        cost_score=85,
        forecast_score=70,
        reliability_score=82
    )

    vessel_c = evaluate_option(
        option_id="VESSEL_C",
        freight_cost=8500000,
        charter_cost=2600000,
        port_cost=500000,
        delay_cost=50000,
        other_cost=100000,
        freight_volatility=25,
        port_congestion=20,
        vessel_reliability=0.95,
        delay_probability=10,
        forecast_uncertainty=10,
        cost_score=75,
        forecast_score=90,
        reliability_score=95
    )

    # Basic checks for each evaluated option
    assert vessel_a["option_id"] == "VESSEL_A"
    assert vessel_b["option_id"] == "VESSEL_B"
    assert vessel_c["option_id"] == "VESSEL_C"

    assert 0 <= vessel_a["decision_score"] <= 100
    assert 0 <= vessel_b["decision_score"] <= 100
    assert 0 <= vessel_c["decision_score"] <= 100

    # Prepare options for optimization
    options = [
        {
            "option_id": vessel_a["option_id"],
            "decision_score": vessel_a["decision_score"]
        },
        {
            "option_id": vessel_b["option_id"],
            "decision_score": vessel_b["decision_score"]
        },
        {
            "option_id": vessel_c["option_id"],
            "decision_score": vessel_c["decision_score"]
        }
    ]

    # Optimize
    result = optimize_options(options)

    # Check optimization output
    assert "ranked_options" in result
    assert "best_option" in result

    assert len(result["ranked_options"]) == 3
    assert result["best_option"]["option_id"] in [
        "VESSEL_A",
        "VESSEL_B",
        "VESSEL_C"
    ]