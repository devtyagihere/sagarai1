from booking import make_booking_decision


# -----------------------------------
# Scenario 1: Good option
# -----------------------------------

good_option = make_booking_decision(
    decision_score=85,
    risk_score=25,
    forecast_score=85
)

print("SCENARIO 1")
print("--------------------")
print(good_option)


# -----------------------------------
# Scenario 2: Poor option
# -----------------------------------

poor_option = make_booking_decision(
    decision_score=40,
    risk_score=45,
    forecast_score=35
)

print("\nSCENARIO 2")
print("--------------------")
print(poor_option)


# -----------------------------------
# Scenario 3: Very high risk
# -----------------------------------

high_risk_option = make_booking_decision(
    decision_score=80,
    risk_score=85,
    forecast_score=90
)

print("\nSCENARIO 3")
print("--------------------")
print(high_risk_option)