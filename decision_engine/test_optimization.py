from optimization import rank_options, get_best_option


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

print("OPTION RANKING")
print("--------------------")

for option in ranked:
    print(
        f"Rank {option['rank']}: "
        f"{option['option_id']} "
        f"→ {option['decision_score']}/100"
    )


best = get_best_option(options)

print("\nBEST OPTION")
print("--------------------")
print(best["option_id"])