import os
import pandas as pd
import joblib

from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error


MODEL_DIR = "models"
MODEL_PATH = os.path.join(
    MODEL_DIR,
    "oil_forecasting_models.pkl"
)

HORIZONS = [7, 15, 30]

LAGS = [1, 2, 3, 7, 14, 30]

ROLLING_WINDOWS = [7, 14, 30]


def prepare_calendar_data(df):
    """
    Convert EIA trading-day data into a continuous
    calendar-day time series.
    """

    data = df.copy()

    data["date"] = pd.to_datetime(data["date"])

    data = (
        data
        .sort_values("date")
        .drop_duplicates("date")
        .set_index("date")
    )

    full_dates = pd.date_range(
        start=data.index.min(),
        end=data.index.max(),
        freq="D"
    )

    data = data.reindex(full_dates)

    data.index.name = "date"

    # Weekend/holiday:
    # use latest available market price
    data["oil_price"] = data["oil_price"].ffill()

    data = data.reset_index()

    return data


def create_features(df):
    """
    Create time-series features.
    """

    data = df.copy()

    # Calendar features
    data["year"] = data["date"].dt.year
    data["month"] = data["date"].dt.month
    data["day"] = data["date"].dt.day
    data["day_of_week"] = data["date"].dt.dayofweek

    # Lag features
    for lag in LAGS:
        data[f"lag_{lag}"] = (
            data["oil_price"].shift(lag)
        )

    # Rolling statistics
    for window in ROLLING_WINDOWS:

        data[f"rolling_mean_{window}"] = (
            data["oil_price"]
            .rolling(window)
            .mean()
        )

        data[f"rolling_std_{window}"] = (
            data["oil_price"]
            .rolling(window)
            .std()
        )

    # Price momentum
    data["price_change_7"] = (
        data["oil_price"]
        - data["oil_price"].shift(7)
    )

    data["price_change_30"] = (
        data["oil_price"]
        - data["oil_price"].shift(30)
    )

    data["return_7"] = (
        data["oil_price"]
        / data["oil_price"].shift(7)
        - 1
    )

    data["return_30"] = (
        data["oil_price"]
        / data["oil_price"].shift(30)
        - 1
    )

    return data


def get_feature_columns():

    feature_columns = [
        "year",
        "month",
        "day",
        "day_of_week"
    ]

    feature_columns += [
        f"lag_{lag}"
        for lag in LAGS
    ]

    for window in ROLLING_WINDOWS:

        feature_columns.append(
            f"rolling_mean_{window}"
        )

        feature_columns.append(
            f"rolling_std_{window}"
        )

    feature_columns += [
        "price_change_7",
        "price_change_30",
        "return_7",
        "return_30"
    ]

    return feature_columns


def train_models():

    print("==========================================")
    print("       OIL FORECASTING MODEL")
    print("==========================================")

    from src.oil_price_provider import (
        get_historical_oil_prices
    )

    # Get real EIA historical data
    df = get_historical_oil_prices()

    print("\nRaw EIA data:")
    print("Rows:", len(df))

    print(
        "Date range:",
        df["date"].min().date(),
        "to",
        df["date"].max().date()
    )

    # Convert to calendar-day data
    data = prepare_calendar_data(df)

    print("\nCalendar-day dataset:")
    print("Rows:", len(data))

    # Create features
    data = create_features(data)

    feature_columns = get_feature_columns()

    models = {}

    # Train separate model for each horizon
    for horizon in HORIZONS:

        print("\n------------------------------------------")
        print(f"Training {horizon}-day model")
        print("------------------------------------------")

        temp = data.copy()

        # Future target
        temp["target"] = (
            temp["oil_price"]
            .shift(-horizon)
        )

        temp = temp.dropna().reset_index(drop=True)

        X = temp[feature_columns]
        y = temp["target"]

        # Chronological split
        split_index = int(len(temp) * 0.80)

        X_train = X.iloc[:split_index]
        X_test = X.iloc[split_index:]

        y_train = y.iloc[:split_index]
        y_test = y.iloc[split_index:]

        print("Training rows:", len(X_train))
        print("Testing rows :", len(X_test))

        # Random Forest
        model = RandomForestRegressor(
            n_estimators=300,
            max_depth=15,
            min_samples_leaf=2,
            random_state=42,
            n_jobs=-1
        )

        model.fit(X_train, y_train)

        # Test predictions
        predictions = model.predict(X_test)

        mae = mean_absolute_error(
            y_test,
            predictions
        )

        mse = mean_squared_error(
            y_test,
            predictions
        )

        rmse = mse ** 0.5

        print("\nPerformance:")
        print("MAE :", round(mae, 3))
        print("RMSE:", round(rmse, 3))

        models[horizon] = model

    # Save models
    os.makedirs(
        MODEL_DIR,
        exist_ok=True
    )

    model_package = {
        "models": models,
        "feature_columns": feature_columns,
        "horizons": HORIZONS,
        "lags": LAGS,
        "rolling_windows": ROLLING_WINDOWS
    }

    joblib.dump(
        model_package,
        MODEL_PATH
    )

    print("\n==========================================")
    print("Oil forecasting models saved!")
    print("Location:", MODEL_PATH)
    print("==========================================")


def forecast_oil_prices():

    """
    Generate current and future oil price forecasts.
    """

    # Load trained models
    package = joblib.load(
        MODEL_PATH
    )

    models = package["models"]

    feature_columns = package[
        "feature_columns"
    ]

    # Get latest real EIA data
    from src.oil_price_provider import (
        get_historical_oil_prices
    )

    df = get_historical_oil_prices()

    # Prepare calendar data
    data = prepare_calendar_data(df)

    # Create latest features
    data = create_features(data)

    latest_row = data.iloc[[-1]]

    forecasts = {}

    for horizon in HORIZONS:

        model = models[horizon]

        X_latest = latest_row[
            feature_columns
        ]

        prediction = model.predict(
            X_latest
        )[0]

        forecasts[
            f"{horizon}_day"
        ] = round(
            float(prediction),
            2
        )

    current_price = float(
        data["oil_price"].iloc[-1]
    )

    return {
        "current_oil_price": round(
            current_price,
            2
        ),
        "forecast": forecasts
    }


if __name__ == "__main__":

    # Train models
    train_models()

    # Generate future forecasts
    result = forecast_oil_prices()

    print("\n==========================================")
    print("          OIL PRICE FORECAST")
    print("==========================================")

    print(
        "Current WTI:",
        result["current_oil_price"],
        "USD/barrel"
    )

    print(
        "7-day forecast:",
        result["forecast"]["7_day"],
        "USD/barrel"
    )

    print(
        "15-day forecast:",
        result["forecast"]["15_day"],
        "USD/barrel"
    )

    print(
        "30-day forecast:",
        result["forecast"]["30_day"],
        "USD/barrel"
    )

    print("\n==========================================")
    print("             COMPLETE")
    print("==========================================")