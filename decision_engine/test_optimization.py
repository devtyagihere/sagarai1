from optimization import rank_options, get_best_option


def test_rank_options():
    options = [
        {
            "option_id": "VESSEL_A",
            "decision_score": 82.5
        },
        {
            "option_id": "VESSEL_B",
            "decision_score": 74.2
        },
        {
            "option_id": "VESSEL_C",
            "decision_score": 91.3
        },
        {
            "option_id": "VESSEL_D",
            "decision_score": 68.7
        }
    ]

    ranked = rank_options(options)

    assert ranked[0]["option_id"] == "VESSEL_C"
    assert ranked[0]["rank"] == 1
    assert ranked[-1]["option_id"] == "VESSEL_D"


def test_get_best_option():
    options = [
        {
            "option_id": "VESSEL_A",
            "decision_score": 82.5
        },
        {
            "option_id": "VESSEL_B",
            "decision_score": 74.2
        },
        {
            "option_id": "VESSEL_C",
            "decision_score": 91.3
        },
        {
            "option_id": "VESSEL_D",
            "decision_score": 68.7
        }
    ]

    best = get_best_option(options)

    assert best["option_id"] == "VESSEL_C"
    assert best["decision_score"] == 91.3