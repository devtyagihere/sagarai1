from scoring import calculate_decision_score


score = calculate_decision_score(
    cost_score=80,
    risk_score=25,
    forecast_score=85,
    reliability_score=90
)

print("DECISION SCORE")
print("--------------------")
print(f"Overall Score: {score}/100")