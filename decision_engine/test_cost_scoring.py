from scoring import calculate_cost_scores


def test_cost_normalization():
    costs = [
        11500000,
        10000000,
        13000000
    ]

    scores = calculate_cost_scores(costs)

    assert len(scores) == 3

    # Lower cost should receive a better score
    assert scores[1] > scores[0]
    assert scores[0] > scores[2]

    # All scores should be between 0 and 100
    assert all(0 <= score <= 100 for score in scores)