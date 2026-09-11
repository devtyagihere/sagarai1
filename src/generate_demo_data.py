import numpy as np
import pandas as pd

# Reproducible results
np.random.seed(42)

# --------------------------------------------------
# 1. Historical dates
# --------------------------------------------------
dates = pd.date_range(
    start="2021-01-01",
    end="2025-12-31",
    freq="D"
)

n = len(dates)

# --------------------------------------------------
# 2. Routes and cargo types
# --------------------------------------------------
routes = [
    ("Shanghai", "Rotterdam"),
    ("Singapore", "Rotterdam"),
    ("Mumbai", "Rotterdam"),
    ("Shanghai", "Los Angeles"),
    ("Mumbai", "Dubai"),
]

cargo_types = [
    "Steel",
    "Iron Ore",
    "Coal",
]

route = np.random.choice(
    [f"{origin}-{destination}" for origin, destination in routes],
    size=n
)

cargo = np.random.choice(cargo_types, size=n)

# --------------------------------------------------
# 3. Seasonality
# --------------------------------------------------
day_of_year = dates.dayofyear.values

seasonality = (
    1
    + 0.08 * np.sin(2 * np.pi * day_of_year / 365.25)
)

# --------------------------------------------------
# 4. BDI / Shipping index
# --------------------------------------------------
bdi = (
    1500
    + 500 * np.sin(2 * np.pi * day_of_year / 365.25)
    + np.cumsum(np.random.normal(0, 8, n))
)

bdi = np.clip(bdi, 500, 5000)

# --------------------------------------------------
# 5. Oil / fuel price
# --------------------------------------------------
oil_price = (
    75
    + 12 * np.sin(2 * np.pi * day_of_year / 365.25)
    + np.cumsum(np.random.normal(0, 0.15, n))
)

oil_price = np.clip(oil_price, 40, 140)

# --------------------------------------------------
# 6. Commodity price
# --------------------------------------------------
commodity_price = (
    110
    + 15 * np.sin(2 * np.pi * day_of_year / 365.25)
    + np.cumsum(np.random.normal(0, 0.25, n))
)

commodity_price = np.clip(commodity_price, 60, 180)

# --------------------------------------------------
# 7. Commodity demand
# --------------------------------------------------
commodity_demand = (
    100
    + 10 * np.sin(2 * np.pi * day_of_year / 365.25)
    + np.random.normal(0, 5, n)
)

commodity_demand = np.clip(commodity_demand, 60, 140)

# --------------------------------------------------
# 8. Weather disruption
# --------------------------------------------------
weather_disruption = np.random.choice(
    [0, 1, 2, 3],
    size=n,
    p=[0.70, 0.20, 0.08, 0.02]
)

# --------------------------------------------------
# 9. Port congestion
# --------------------------------------------------
port_congestion = np.clip(
    np.random.normal(40, 15, n)
    + weather_disruption * 8,
    0,
    100
)

# --------------------------------------------------
# 10. Currency / macro indicator
# --------------------------------------------------
usd_index = (
    100
    + 4 * np.sin(2 * np.pi * day_of_year / 365.25)
    + np.random.normal(0, 1.5, n)
)

# --------------------------------------------------
# 11. Route effect
# --------------------------------------------------
route_effect = np.array([
    {
        "Shanghai-Rotterdam": 1.20,
        "Singapore-Rotterdam": 1.10,
        "Mumbai-Rotterdam": 0.95,
        "Shanghai-Los Angeles": 1.15,
        "Mumbai-Dubai": 0.80,
    }[r]
    for r in route
])

# --------------------------------------------------
# 12. Cargo effect
# --------------------------------------------------
cargo_effect = np.array([
    {
        "Steel": 1.05,
        "Iron Ore": 1.15,
        "Coal": 0.95,
    }[c]
    for c in cargo
])

# --------------------------------------------------
# 13. Freight rate
# --------------------------------------------------
# The target is intentionally influenced by
# multiple variables so the ML model has patterns to learn.

freight_rate = (
    700
    + 0.45 * bdi
    + 3.2 * oil_price
    + 2.0 * commodity_price
    + 4.0 * commodity_demand
    + 70 * weather_disruption
    + 4.5 * port_congestion
    - 2.5 * usd_index
)

freight_rate = (
    freight_rate
    * seasonality
    * route_effect
    * cargo_effect
)

# Add realistic market noise
freight_rate += np.random.normal(0, 100, n)

freight_rate = np.clip(freight_rate, 500, None)

# --------------------------------------------------
# 14. Create DataFrame
# --------------------------------------------------
df = pd.DataFrame({
    "date": dates,
    "origin_port": [r.split("-")[0] for r in route],
    "destination_port": [r.split("-")[1] for r in route],
    "cargo_type": cargo,
    "freight_rate": np.round(freight_rate, 2),
    "bdi": np.round(bdi, 2),
    "oil_price": np.round(oil_price, 2),
    "commodity_price": np.round(commodity_price, 2),
    "commodity_demand": np.round(commodity_demand, 2),
    "weather_disruption": weather_disruption,
    "port_congestion": np.round(port_congestion, 2),
    "usd_index": np.round(usd_index, 2),
})

# --------------------------------------------------
# 15. Save dataset
# --------------------------------------------------
output_path = "data/demo_data.csv"

df.to_csv(output_path, index=False)

print("Demo dataset generated successfully!")
print(f"Rows: {len(df)}")
print(f"Columns: {len(df.columns)}")
print(f"Saved to: {output_path}")
print("\nFirst 5 rows:")
print(df.head())