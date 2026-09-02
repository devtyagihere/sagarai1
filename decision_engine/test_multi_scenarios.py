from scenarios import evaluate_multi_option_scenario


options = [
    {
        "option_id": "VESSEL_A",
        "freight_cost": 8000000,
        "charter_cost": 2500000,
        "port_cost": 700000,
        "delay_cost": 100000,
        "other_cost": 200000,

        "freight_volatility": 40,
        "port_congestion": 30,
        "vessel_reliability": 0.90,
        "delay_probability": 20,
        "forecast_uncertainty": 15,

        "forecast_score": 85,
        "reliability_score": 90
    },

    {
        "option_id": "VESSEL_B",
        "freight_cost": 7500000,
        "charter_cost": 2300000,
        "port_cost": 900000,
        "delay_cost": 300000,
        "other_cost": 150000,

        "freight_volatility": 55,
        "port_congestion": 50,
        "vessel_reliability": 0.82,
        "delay_probability": 35,
        "forecast_uncertainty": 25,

        "forecast_score": 70,
        "reliability_score": 82
    },

    {
        "option_id": "VESSEL_C",
        "freight_cost": 8500000,
        "charter_cost": 2600000,
        "port_cost": 500000,
        "delay_cost": 50000,
        "other_cost": 100000,

        "freight_volatility": 25,
        "port_congestion": 20,
        "vessel_reliability": 0.95,
        "delay_probability": 10,
        "forecast_uncertainty": 10,

        "forecast_score": 90,
        "reliability_score": 95
    }
]


# Scenario:
# Vessel C freight cost increases by 10%.

result = evaluate_multi_option_scenario(
    options,
    "VESSEL_C",
    {
        "freight_cost": 10
    }
)


print("MULTI-OPTION SCENARIO TEST")
print("==============================")

print("\nRANKING AFTER SCENARIO")

for option in result["ranked_options"]:
    print(
        f"Rank {option['rank']}: "
        f"{option['option_id']} "
        f"-> {option['decision_score']}/100"
    )


print("\nBEST OPTION")
print("==============================")
print(result["best_option"]["option_id"])


print("\nDETAILED RESULTS")
print("==============================")

for option in result["evaluated_options"]:
    print(
        option["option_id"],
        "| Cost:",
        option["cost"]["total_cost"],
        "| Cost score included in decision:",
        option["decision_score"],
        "| Decision:",
        option["booking_decision"]["decision"]
    )
# ==========================================
# AUTOMATED CHECKS
# ==========================================

assert result["best_option"]["option_id"] == "VESSEL_B"

# Vessel C freight cost should have increased by 10%.
vessel_c = next(
    option
    for option in result["evaluated_options"]
    if option["option_id"] == "VESSEL_C"
)

assert vessel_c["cost"]["total_cost"] == 12600000

# Scenario should cause Vessel C to be ranked last.
assert result["ranked_options"][-1]["option_id"] == "VESSEL_C"

print("\nALL SCENARIO ASSERTIONS PASSED")