import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data" / "processed"

FORECAST_FILE = DATA_DIR / "next_week_forecast.csv"
TREND_FILE = DATA_DIR / "freight_trend_intelligence.csv"
OUTPUT_FILE = DATA_DIR / "freight_decision_intelligence.csv"


def route_name(target):
    routes = {
        "Gulf_Vessel": "US Gulf → Japan",
        "Pacific_Vessel": "Pacific Northwest → Japan",
    }

    return routes.get(target, target)


def get_decision(forecast_pct, trend, risk):
    if risk == "High Risk":
        return "Monitor Closely"

    if forecast_pct >= 1 and trend == "Rising":
        return "Prepare for Higher Freight Cost"

    if forecast_pct <= -1 and trend == "Falling":
        return "Potential Freight Cost Saving"

    if forecast_pct >= 1:
        return "Watch for Rising Freight Cost"

    if forecast_pct <= -1:
        return "Watch for Falling Freight Cost"

    if trend == "Rising":
        return "Monitor Rising Trend"

    if trend == "Falling":
        return "Monitor Falling Trend"

    return "Hold / Monitor"


# Load files
forecast = pd.read_csv(FORECAST_FILE)
trend = pd.read_csv(TREND_FILE)


# Add matching route name to forecast data
forecast["Route"] = forecast["Target"].apply(route_name)


# Merge using the human-readable route
decision = forecast.merge(
    trend,
    on=["Route"],
    how="left",
)


# Build final decision intelligence
output = pd.DataFrame({
    "Route": decision["Route"],
    "Latest_Date": decision["Latest_Date_x"],
    "Current_Price": decision["Current_Price_x"].round(2),
    "Forecast_Price": decision["Predicted_Next_Week_Price"].round(2),
    "Forecast_Change": decision["Predicted_Change"].round(2),
    "Forecast_Change_Pct": decision["Predicted_Change_Pct"].round(2),
    "Forecast_Lower_Bound": decision["Forecast_Lower_Bound"].round(2),
    "Forecast_Upper_Bound": decision["Forecast_Upper_Bound"].round(2),
    "Direction": decision["Direction"],
    "Signal": decision["Signal"],
    "Risk": decision["Risk"],
    "Trend_4W": decision["Trend"],
    "Change_4W_Pct": decision["Change_4W_Pct"].round(2),
    "Change_12W_Pct": decision["Change_12W_Pct"].round(2),
    "Volatility_4W_Pct": decision["Volatility_4W_Pct"].round(2),
})


# Generate final decision
output["Decision"] = output.apply(
    lambda row: get_decision(
        row["Forecast_Change_Pct"],
        row["Trend_4W"],
        row["Risk"],
    ),
    axis=1,
)


# Save final output
output.to_csv(
    OUTPUT_FILE,
    index=False,
)


print("=" * 75)
print("FREIGHT DECISION INTELLIGENCE")
print("=" * 75)

for _, row in output.iterrows():

    print()
    print("-" * 75)
    print(row["Route"])
    print("-" * 75)

    print(f"Current price:          {row['Current_Price']:.2f}")
    print(f"Forecast price:         {row['Forecast_Price']:.2f}")
    print(f"Forecast change:        {row['Forecast_Change']:+.2f}")
    print(f"Forecast change (%):    {row['Forecast_Change_Pct']:+.2f}%")

    print(
        f"Forecast range:         "
        f"{row['Forecast_Lower_Bound']:.2f} - "
        f"{row['Forecast_Upper_Bound']:.2f}"
    )

    print(f"Direction:              {row['Direction']}")
    print(f"Signal:                 {row['Signal']}")
    print(f"Risk:                   {row['Risk']}")
    print(f"4-week trend:           {row['Trend_4W']}")
    print(f"4-week change (%):      {row['Change_4W_Pct']:+.2f}%")
    print(f"12-week change (%):     {row['Change_12W_Pct']:+.2f}%")
    print(f"4-week volatility:      {row['Volatility_4W_Pct']:.2f}%")
    print(f"Decision:               {row['Decision']}")


print()
print("=" * 75)
print("DECISION INTELLIGENCE CREATED")
print("=" * 75)
print()
print(f"Output: {OUTPUT_FILE}")