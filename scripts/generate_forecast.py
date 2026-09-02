import pandas as pd
import joblib
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

DATA_DIR = BASE_DIR / "data" / "processed"
MODEL_DIR = BASE_DIR / "models"
OUTPUT_DIR = DATA_DIR

FEATURES = [
    "Truck", "Rail", "Barge", "Gulf_Vessel", "Pacific_Vessel",
    "Truck_lag_1w", "Truck_lag_2w", "Truck_lag_4w", "Truck_lag_12w",
    "Rail_lag_1w", "Rail_lag_2w", "Rail_lag_4w", "Rail_lag_12w",
    "Barge_lag_1w", "Barge_lag_2w", "Barge_lag_4w", "Barge_lag_12w",
    "Gulf_Vessel_lag_1w", "Gulf_Vessel_lag_2w",
    "Gulf_Vessel_lag_4w", "Gulf_Vessel_lag_12w",
    "Pacific_Vessel_lag_1w", "Pacific_Vessel_lag_2w",
    "Pacific_Vessel_lag_4w", "Pacific_Vessel_lag_12w",
    "US_Diesel_Price", "Gulf_Coast_Diesel_Price",
    "US_Diesel_Price_change_1w",
    "US_Diesel_Price_change_2w",
    "US_Diesel_Price_change_4w",
    "US_Diesel_Price_pct_change_1w",
    "US_Diesel_Price_pct_change_4w",
    "US_Diesel_Price_ma_4w",
    "US_Diesel_Price_ma_8w",
    "US_Diesel_Price_ma_12w",
    "US_Diesel_Price_volatility_4w",
    "US_Diesel_Price_volatility_8w",
    "Gulf_Coast_Diesel_Price_change_1w",
    "Gulf_Coast_Diesel_Price_change_2w",
    "Gulf_Coast_Diesel_Price_change_4w",
    "Gulf_Coast_Diesel_Price_pct_change_1w",
    "Gulf_Coast_Diesel_Price_pct_change_4w",
    "Gulf_Coast_Diesel_Price_ma_4w",
    "Gulf_Coast_Diesel_Price_ma_8w",
    "Gulf_Coast_Diesel_Price_ma_12w",
    "Gulf_Coast_Diesel_Price_volatility_4w",
    "Gulf_Coast_Diesel_Price_volatility_8w",
    "Gulf_Diesel_Spread",
    "Gulf_Diesel_Spread_change_1w",
    "Gulf_Diesel_Spread_change_4w",
]


def find_model(target):
    candidates = [
        MODEL_DIR / f"{target}_fuel_change_model.joblib",
        MODEL_DIR / f"{target}_change_model.joblib",
        MODEL_DIR / f"{target}_model.joblib",
    ]

    for path in candidates:
        if path.exists():
            return path

    return None


def forecast_target(dataset_file, target):
    df = pd.read_csv(dataset_file)
    df["Date"] = pd.to_datetime(df["Date"])
    df = df.sort_values("Date").reset_index(drop=True)

    latest = df.iloc[-1]

    missing_features = [f for f in FEATURES if f not in df.columns]

    if missing_features:
        raise ValueError(
            f"Missing features for {target}: {missing_features}"
        )

    model_path = find_model(target)

    if model_path is None:
        raise FileNotFoundError(
            f"No trained model found for {target} in {MODEL_DIR}"
        )

    model = joblib.load(model_path)

    X = latest[FEATURES].to_frame().T

    predicted_change = float(model.predict(X)[0])

    current_price = float(latest[target.replace("_target", "")])

    predicted_price = current_price + predicted_change

    return {
        "Target": target.replace("_target", ""),
        "Latest_Date": latest["Date"].strftime("%Y-%m-%d"),
        "Current_Price": current_price,
        "Predicted_Change": predicted_change,
        "Predicted_Next_Week_Price": predicted_price,
        "Model": model_path.name,
    }


print("=" * 65)
print("NEXT-WEEK FREIGHT FORECAST")
print("=" * 65)

results = []

targets = [
    (
        DATA_DIR / "gulf_fuel_ml_dataset.csv",
        "Gulf_target",
    ),
    (
        DATA_DIR / "pacific_fuel_ml_dataset.csv",
        "Pacific_target",
    ),
]

for dataset, target in targets:
    result = forecast_target(dataset, target)
    results.append(result)

    print()
    print("-" * 65)
    print(result["Target"])
    print("-" * 65)

    print(f"Latest observed date:       {result['Latest_Date']}")
    print(f"Current price:              {result['Current_Price']:.4f}")
    print(f"Predicted price change:     {result['Predicted_Change']:+.4f}")
    print(
        f"Predicted next-week price:  "
        f"{result['Predicted_Next_Week_Price']:.4f}"
    )
    print(f"Model:                      {result['Model']}")


output = pd.DataFrame(results)

output_file = OUTPUT_DIR / "next_week_forecast.csv"
output.to_csv(output_file, index=False)

print()
print("=" * 65)
print("FORECAST COMPLETE")
print("=" * 65)
print()
print(f"Output: {output_file}")