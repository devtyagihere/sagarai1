from cost import calculate_total_cost


result = calculate_total_cost(
    freight_cost=8000000,
    charter_cost=2500000,
    port_cost=700000,
    delay_cost=100000,
    other_cost=200000
)

print("COST BREAKDOWN")
print("--------------------")

for key, value in result.items():
    print(f"{key}: ₹{value:,.2f}")