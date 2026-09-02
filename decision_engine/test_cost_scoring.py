from scoring import calculate_cost_scores


costs = [
    11500000,
    10000000,
    13000000
]


scores = calculate_cost_scores(costs)


print("COST NORMALIZATION")
print("==============================")

for cost, score in zip(costs, scores):
    print(
        f"Cost: ₹{cost:,.0f}"
        f" → Cost Score: {score}/100"
    )