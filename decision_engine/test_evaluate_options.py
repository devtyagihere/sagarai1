from engine import evaluate_options


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


results = evaluate_options(options)


print("M6 MULTI-OPTION EVALUATION")
print("==============================")

for result in results:

    print("\nOPTION:", result["option_id"])

    print("Total Cost:",
          result["cost"]["total_cost"])

    print("Risk Score:",
          result["risk"]["score"])

    print("Risk Category:",
          result["risk"]["category"])

    print("Decision Score:",
          result["decision_score"])

    print("Booking Decision:",
          result["booking_decision"]["decision"])