import pandas as pd
import joblib
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

DATA_DIR = BASE_DIR / "data" / "processed"
MODEL_DIR = BASE_DIR / "models"
OUTPUT_DIR = DATA_DIR


MODEL_ERRORS = {
    "Gulf_Vessel": {
        "mae": 2.1935,
        "rmse": 2.9340,
    },
    "Pacific_Vessel": {
        "mae": 2.1142,
        "rmse": 2.8350,
    },
}


def classify_signal(change_pct):
    if change_pct >= 5:
        return "Strong Increase"
    elif change_pct >= 1:
        return "Increase"
    elif change_pct <= -5:
        return "Strong Decrease"
    elif change_pct <= -1:
        return "Decrease"
    else:
        return "Stable"


def classify_risk(predicted_change, vessel_column):
    error = MODEL_ERRORS[vessel_column]["mae"]
    change_size = abs(predicted_change)

    if change_size >= error * 2:
        return "Low Risk"
    elif change_size >= error:
        return "Medium Risk"
    else:
        return "High Risk"


def generate_recommendation(direction, signal, risk):
    if risk == "High Risk":
        return "High Uncertainty - Monitor"

    if signal == "Strong Increase":
        return "Prepare for Higher Freight Cost"

    if signal == "Increase":
        return "Watch for Rising Freight Cost"

    if signal == "Strong Decrease":
        return "Potential Freight Cost Saving"

    if signal == "Decrease":
        return "Watch for Falling Freight Cost"

    return "Hold / Monitor"


def forecast_target(
    dataset_file,
    target,
    model_filename,
    vessel_column,
):
    df = pd.read_csv(dataset_file)

    df["Date"] = pd.to_datetime(df["Date"])
    df = df.sort_values("Date").reset_index(drop=True)

    latest = df.iloc[-1]

    model_path = MODEL_DIR / model_filename

    if not model_path.exists():
        raise FileNotFoundError(
            f"Model not found: {model_path}"
        )

    artifact = joblib.load(model_path)

    model = artifact["model"]
    features = artifact["features"]

    missing_features = [
        feature for feature in features
        if feature not in df.columns
    ]

    if missing_features:
        raise ValueError(
            f"Missing features for {target}: {missing_features}"
        )

    X = latest[features].to_frame().T

    predicted_change = float(model.predict(X)[0])

    current_price = float(latest[vessel_column])

    predicted_price = current_price + predicted_change

    predicted_change_pct = (
        predicted_change / current_price
    ) * 100

    if predicted_change > 0:
        direction = "Increase"
    elif predicted_change < 0:
        direction = "Decrease"
    else:
        direction = "Stable"

    signal = classify_signal(predicted_change_pct)

    risk = classify_risk(
        predicted_change,
        vessel_column,
    )

    model_mae = MODEL_ERRORS[vessel_column]["mae"]
    model_rmse = MODEL_ERRORS[vessel_column]["rmse"]

    lower_bound = predicted_price - model_rmse
    upper_bound = predicted_price + model_rmse

    recommendation = generate_recommendation(
        direction,
        signal,
        risk,
    )

    return {
        "Target": target,
        "Latest_Date": latest["Date"].strftime("%Y-%m-%d"),
        "Current_Price": current_price,
        "Predicted_Change": predicted_change,
        "Predicted_Change_Pct": predicted_change_pct,
        "Predicted_Next_Week_Price": predicted_price,
        "Forecast_Lower_Bound": lower_bound,
        "Forecast_Upper_Bound": upper_bound,
        "Direction": direction,
        "Signal": signal,
        "Risk": risk,
        "Recommendation": recommendation,
        "Historical_MAE": model_mae,
        "Historical_RMSE": model_rmse,
        "Model": model_path.name,
    }


print("=" * 75)
print("NEXT-WEEK FREIGHT FORECAST")
print("=" * 75)

results = []

results.append(
    forecast_target(
        DATA_DIR / "gulf_fuel_ml_dataset.csv",
        "Gulf_Vessel",
        "gulf_fuel_change_model.joblib",
        "Gulf_Vessel",
    )
)

results.append(
    forecast_target(
        DATA_DIR / "pacific_fuel_ml_dataset.csv",
        "Pacific_Vessel",
        "pacific_fuel_change_model.joblib",
        "Pacific_Vessel",
    )
)


for result in results:
    print()
    print("-" * 75)
    print(result["Target"])
    print("-" * 75)

    print(
        f"Latest observed date:        "
        f"{result['Latest_Date']}"
    )

    print(
        f"Current price:               "
        f"{result['Current_Price']:.4f}"
    )

    print(
        f"Predicted price change:      "
        f"{result['Predicted_Change']:+.4f}"
    )

    print(
        f"Predicted change (%):        "
        f"{result['Predicted_Change_Pct']:+.2f}%"
    )

    print(
        f"Predicted next-week price:   "
        f"{result['Predicted_Next_Week_Price']:.4f}"
    )

    print(
        f"Forecast range:              "
        f"{result['Forecast_Lower_Bound']:.4f} - "
        f"{result['Forecast_Upper_Bound']:.4f}"
    )

    print(
        f"Direction:                   "
        f"{result['Direction']}"
    )

    print(
        f"Signal:                      "
        f"{result['Signal']}"
    )

    print(
        f"Risk:                        "
        f"{result['Risk']}"
    )

    print(
        f"Recommendation:             "
        f"{result['Recommendation']}"
    )

    print(
        f"Historical MAE:              "
        f"{result['Historical_MAE']:.4f}"
    )

    print(
        f"Historical RMSE:             "
        f"{result['Historical_RMSE']:.4f}"
    )

    print(
        f"Model:                       "
        f"{result['Model']}"
    )


output = pd.DataFrame(results)

output_file = OUTPUT_DIR / "next_week_forecast.csv"

output.to_csv(
    output_file,
    index=False,
)

print()
print("=" * 75)
print("FORECAST COMPLETE")
print("=" * 75)
print()
print(f"Output: {output_file}")