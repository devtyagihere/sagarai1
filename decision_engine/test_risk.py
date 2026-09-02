from risk import calculate_risk_score, get_risk_category


risk_score = calculate_risk_score(
    freight_volatility=40,
    port_congestion=30,
    vessel_reliability=0.90,
    delay_probability=20,
    forecast_uncertainty=15
)

category = get_risk_category(risk_score)

print("RISK ASSESSMENT")
print("--------------------")
print(f"Risk Score: {risk_score}/100")
print(f"Risk Category: {category}")