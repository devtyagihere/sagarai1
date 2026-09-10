import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data" / "processed"

INPUT_FILE = DATA_DIR / "freight_fuel_features.csv"
OUTPUT_FILE = DATA_DIR / "freight_trend_intelligence.csv"


df = pd.read_csv(INPUT_FILE)

df["Date"] = pd.to_datetime(df["Date"])
df = df.sort_values("Date").reset_index(drop=True)


routes = {
    "Gulf_Vessel": "US Gulf → Japan",
    "Pacific_Vessel": "Pacific Northwest → Japan",
}


results = []

for vessel_column, route in routes.items():

    latest = df.iloc[-1]

    current_price = latest[vessel_column]

    price_4w_ago = df[vessel_column].shift(4).iloc[-1]
    price_12w_ago = df[vessel_column].shift(12).iloc[-1]

    change_4w = current_price - price_4w_ago
    change_12w = current_price - price_12w_ago

    pct_change_4w = (change_4w / price_4w_ago) * 100
    pct_change_12w = (change_12w / price_12w_ago) * 100

    volatility_4w = (
        df[vessel_column]
        .pct_change()
        .rolling(4)
        .std()
        .iloc[-1]
        * 100
    )

    if pct_change_4w >= 1:
        trend = "Rising"
    elif pct_change_4w <= -1:
        trend = "Falling"
    else:
        trend = "Stable"

    results.append({
        "Route": route,
        "Latest_Date": latest["Date"].strftime("%Y-%m-%d"),
        "Current_Price": round(current_price, 2),
        "Change_4W": round(change_4w, 2),
        "Change_4W_Pct": round(pct_change_4w, 2),
        "Change_12W": round(change_12w, 2),
        "Change_12W_Pct": round(pct_change_12w, 2),
        "Volatility_4W_Pct": round(volatility_4w, 2),
        "Trend": trend,
    })


output = pd.DataFrame(results)

output.to_csv(
    OUTPUT_FILE,
    index=False,
)


print("=" * 70)
print("FREIGHT TREND INTELLIGENCE")
print("=" * 70)

for _, row in output.iterrows():

    print()
    print(row["Route"])
    print("-" * 70)

    print(f"Current price:       {row['Current_Price']:.2f}")
    print(f"4-week change:       {row['Change_4W']:+.2f}")
    print(f"4-week change (%):   {row['Change_4W_Pct']:+.2f}%")
    print(f"12-week change:      {row['Change_12W']:+.2f}")
    print(f"12-week change (%):  {row['Change_12W_Pct']:+.2f}%")
    print(f"4-week volatility:   {row['Volatility_4W_Pct']:.2f}%")
    print(f"Trend:               {row['Trend']}")


print()
print("=" * 70)
print("TREND INTELLIGENCE CREATED")
print("=" * 70)
print()
print(f"Output: {OUTPUT_FILE}")