from scenarios import (
    evaluate_scenario,
    compare_scenario_results
)

from engine import evaluate_option


# ==========================================
# BASE OPTION
# ==========================================

base_option = {
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

    "cost_score": 75,
    "forecast_score": 90,
    "reliability_score": 95
}


# ==========================================
# BASE DECISION
# ==========================================

base_result = evaluate_option(
    option_id=base_option["option_id"],

    freight_cost=base_option["freight_cost"],
    charter_cost=base_option["charter_cost"],
    port_cost=base_option["port_cost"],
    delay_cost=base_option["delay_cost"],
    other_cost=base_option["other_cost"],

    freight_volatility=base_option["freight_volatility"],
    port_congestion=base_option["port_congestion"],
    vessel_reliability=base_option["vessel_reliability"],
    delay_probability=base_option["delay_probability"],
    forecast_uncertainty=base_option["forecast_uncertainty"],

    cost_score=base_option["cost_score"],
    forecast_score=base_option["forecast_score"],
    reliability_score=base_option["reliability_score"]
)


print("M6 SCENARIO ANALYSIS")
print("==============================")

print("\nBASE CASE")
print("------------------------------")
print(f"Score: {base_result['decision_score']}/100")
print(
    f"Decision: "
    f"{base_result['booking_decision']['decision']}"
)


# ==========================================
# SCENARIO 1
# Freight cost increases by 10%
# ==========================================

freight_scenario = evaluate_scenario(
    base_option,
    {
        "freight_cost": 10
    }
)

freight_comparison = compare_scenario_results(
    base_result,
    freight_scenario
)


print("\nSCENARIO 1 — FREIGHT COST +10%")
print("------------------------------")
print(f"New Score: {freight_comparison['scenario_score']}/100")
print(f"Score Change: {freight_comparison['score_change']}")
print(f"Decision: {freight_comparison['scenario_decision']}")


# ==========================================
# SCENARIO 2
# Port congestion increases by 20%
# ==========================================

port_scenario = evaluate_scenario(
    base_option,
    {
        "port_congestion": 20
    }
)

port_comparison = compare_scenario_results(
    base_result,
    port_scenario
)


print("\nSCENARIO 2 — PORT CONGESTION +20%")
print("------------------------------")
print(f"New Score: {port_comparison['scenario_score']}/100")
print(f"Score Change: {port_comparison['score_change']}")
print(f"Decision: {port_comparison['scenario_decision']}")


# ==========================================
# SCENARIO 3
# Delay probability increases by 30%
# ==========================================

delay_scenario = evaluate_scenario(
    base_option,
    {
        "delay_probability": 30
    }
)

delay_comparison = compare_scenario_results(
    base_result,
    delay_scenario
)


print("\nSCENARIO 3 — DELAY PROBABILITY +30%")
print("------------------------------")
print(f"New Score: {delay_comparison['scenario_score']}/100")
print(f"Score Change: {delay_comparison['score_change']}")
print(f"Decision: {delay_comparison['scenario_decision']}")