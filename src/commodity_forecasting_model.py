import os
import joblib
import pandas as pd

from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score


DATA_PATH = "data/demo_data.csv"
MODEL_PATH = "models/commodity_forecasting_models.pkl"

HORIZONS = [7, 15, 30]


def create_features(df):
    df = df.copy()

    df["date"] = pd.to_datetime(df["date"])
    df = df.sort_values("date").reset_index(drop=True)

    # Calendar features
    df["year"] = df["date"].dt.year
    df["month"] = df["date"].dt.month
    df["day"] = df["date"].dt.day
    df["day_of_week"] = df["date"].dt.dayofweek

    # Lag features
    for lag in [1, 2, 3, 7, 14, 30]:
        df[f"lag_{lag}"] = df["commodity_price"].shift(lag)

    # Rolling features
    shifted = df["commodity_price"].shift(1)

    for window in [7, 14, 30]:
        df[f"rolling_mean_{window}"] = shifted.rolling(window).mean()
        df[f"rolling_std_{window}"] = shifted.rolling(window).std()

    # Price momentum
    df["change_7"] = (
        df["commodity_price"].shift(1)
        - df["commodity_price"].shift(8)
    )

    df["change_30"] = (
        df["commodity_price"].shift(1)
        - df["commodity_price"].shift(31)
    )

    df["return_7"] = (
        df["commodity_price"].shift(1)
        / df["commodity_price"].shift(8)
        - 1
    )

    df["return_30"] = (
        df["commodity_price"].shift(1)
        / df["commodity_price"].shift(31)
        - 1
    )

    return df


def train_commodity_models():
    print("=" * 60)
    print("COMMODITY PRICE FORECASTING MODEL")
    print("=" * 60)

    df = pd.read_csv(DATA_PATH)

    df["date"] = pd.to_datetime(df["date"])

    # Keep only required columns
    df = df[["date", "commodity_price"]].copy()

    # Sort chronologically
    df = df.sort_values("date").reset_index(drop=True)

    print("\nHistorical data:")
    print("Rows:", len(df))
    print("Start:", df["date"].min().date())
    print("End:", df["date"].max().date())

    models = {}
    performance = {}

    for horizon in HORIZONS:

        print("\n" + "-" * 50)
        print(f"Training {horizon}-day commodity model")

        data = create_features(df)

        # Future target
        data["target"] = data["commodity_price"].shift(-horizon)

        feature_columns = [
            "year",
            "month",
            "day",
            "day_of_week",
            "lag_1",
            "lag_2",
            "lag_3",
            "lag_7",
            "lag_14",
            "lag_30",
            "rolling_mean_7",
            "rolling_std_7",
            "rolling_mean_14",
            "rolling_std_14",
            "rolling_mean_30",
            "rolling_std_30",
            "change_7",
            "change_30",
            "return_7",
            "return_30",
        ]

        data = data.dropna(
            subset=feature_columns + ["target"]
        ).reset_index(drop=True)

        X = data[feature_columns]
        y = data["target"]

        # Chronological split
        split_index = int(len(data) * 0.80)

        X_train = X.iloc[:split_index]
        X_test = X.iloc[split_index:]

        y_train = y.iloc[:split_index]
        y_test = y.iloc[split_index:]

        model = RandomForestRegressor(
            n_estimators=300,
            max_depth=15,
            min_samples_leaf=2,
            random_state=42,
            n_jobs=-1
        )

        model.fit(X_train, y_train)

        predictions = model.predict(X_test)

        mae = mean_absolute_error(y_test, predictions)
        rmse = mean_squared_error(
            y_test,
            predictions
        ) ** 0.5
        r2 = r2_score(y_test, predictions)

        print(f"MAE : {mae:.4f}")
        print(f"RMSE: {rmse:.4f}")
        print(f"R²  : {r2:.4f}")

        models[horizon] = model

        performance[horizon] = {
            "MAE": mae,
            "RMSE": rmse,
            "R2": r2
        }

    os.makedirs("models", exist_ok=True)

    artifact = {
        "models": models,
        "performance": performance,
        "features": feature_columns,
        "horizons": HORIZONS
    }

    joblib.dump(artifact, MODEL_PATH)

    print("\n" + "=" * 60)
    print("MODEL SAVED")
    print("=" * 60)
    print(MODEL_PATH)

    return artifact


def forecast_commodity_prices():
    """
    Forecast commodity price using the latest available
    historical demo data.
    """

    artifact = joblib.load(MODEL_PATH)

    models = artifact["models"]
    feature_columns = artifact["features"]

    df = pd.read_csv(DATA_PATH)

    df["date"] = pd.to_datetime(df["date"])

    df = df[
        ["date", "commodity_price"]
    ].sort_values("date").reset_index(drop=True)

    data = create_features(df)

    latest = data.iloc[-1]

    X_latest = pd.DataFrame(
        [[latest[col] for col in feature_columns]],
        columns=feature_columns
    )

    forecasts = {}

    for horizon in HORIZONS:

        model = models[horizon]

        prediction = model.predict(X_latest)[0]

        forecasts[f"{horizon}_day"] = round(
            float(prediction),
            2
        )

    current_price = float(
        df["commodity_price"].iloc[-1]
    )

    return {
        "current_commodity_price": round(
            current_price,
            2
        ),
        "forecast": forecasts
    }


if __name__ == "__main__":

    train_commodity_models()

    print("\n" + "=" * 60)
    print("COMMODITY FORECAST TEST")
    print("=" * 60)

    result = forecast_commodity_prices()

    print("\nCurrent commodity price:")
    print(result["current_commodity_price"])

    print("\nForecast:")
    print("7-day :", result["forecast"]["7_day"])
    print("15-day:", result["forecast"]["15_day"])
    print("30-day:", result["forecast"]["30_day"])