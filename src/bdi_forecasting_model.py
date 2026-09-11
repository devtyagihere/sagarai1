import os
import joblib
import numpy as np
import pandas as pd

from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error


from src.bdi_provider import get_historical_bdi


# ============================================================
# CONFIGURATION
# ============================================================

MODEL_PATH = "models/bdi_forecasting_model.pkl"

LAGS = [
    1,
    2,
    3,
    5,
    7
]

ROLLING_WINDOWS = [
    3,
    7
]


# ============================================================
# CREATE FEATURES
# ============================================================

def create_features(df):

    data = df.copy()

    data = data.sort_values(
        "date"
    ).reset_index(drop=True)


    # --------------------------------------------------------
    # LAG FEATURES
    # --------------------------------------------------------

    for lag in LAGS:

        data[f"lag_{lag}"] = (
            data["bdi"].shift(lag)
        )


    # --------------------------------------------------------
    # ROLLING FEATURES
    # --------------------------------------------------------

    for window in ROLLING_WINDOWS:

        data[f"rolling_mean_{window}"] = (
            data["bdi"]
            .shift(1)
            .rolling(window)
            .mean()
        )

        data[f"rolling_std_{window}"] = (
            data["bdi"]
            .shift(1)
            .rolling(window)
            .std()
        )


    # --------------------------------------------------------
    # MOMENTUM
    # --------------------------------------------------------

    data["change_1"] = (
        data["bdi"].shift(1)
        -
        data["bdi"].shift(2)
    )

    data["change_3"] = (
        data["bdi"].shift(1)
        -
        data["bdi"].shift(4)
    )


    # --------------------------------------------------------
    # PERCENTAGE RETURNS
    # --------------------------------------------------------

    data["return_1"] = (
        data["bdi"].shift(1)
        .pct_change()
    )

    data["return_3"] = (
        data["bdi"].shift(3)
        .pct_change()
    )


    # --------------------------------------------------------
    # CALENDAR FEATURES
    # --------------------------------------------------------

    data["day_of_week"] = (
        data["date"].dt.dayofweek
    )

    data["day_of_month"] = (
        data["date"].dt.day
    )


    return data


# ============================================================
# FEATURE COLUMN LIST
# ============================================================

FEATURE_COLUMNS = [

    "lag_1",
    "lag_2",
    "lag_3",
    "lag_5",
    "lag_7",

    "rolling_mean_3",
    "rolling_std_3",

    "rolling_mean_7",
    "rolling_std_7",

    "change_1",
    "change_3",

    "return_1",
    "return_3",

    "day_of_week",
    "day_of_month"
]


# ============================================================
# LOAD AND CLEAN BDI HISTORY
# ============================================================

def load_bdi_history():

    df = get_historical_bdi()

    if df is None or df.empty:

        raise ValueError(
            "No historical BDI data available."
        )


    df = df.copy()


    # --------------------------------------------------------
    # DATE CONVERSION
    # --------------------------------------------------------

    df["date"] = pd.to_datetime(
        df["date"],
        errors="coerce"
    )


    df["bdi"] = pd.to_numeric(
        df["bdi"],
        errors="coerce"
    )


    df = df.dropna(
        subset=[
            "date",
            "bdi"
        ]
    )


    # --------------------------------------------------------
    # REMOVE TIME COMPONENT
    # --------------------------------------------------------

    df["date"] = (
        df["date"]
        .dt.normalize()
    )


    # --------------------------------------------------------
    # ONE VALUE PER DAY
    # --------------------------------------------------------

    df = (
        df
        .groupby("date", as_index=False)["bdi"]
        .last()
    )


    df = (
        df
        .sort_values("date")
        .reset_index(drop=True)
    )


    return df


# ============================================================
# TRAIN BDI MODEL
# ============================================================

def train_bdi_model():

    print("=" * 60)
    print("BDI FORECASTING MODEL TRAINING")
    print("=" * 60)


    # --------------------------------------------------------
    # LOAD DATA
    # --------------------------------------------------------

    df = load_bdi_history()


    print("\nHistorical BDI data loaded.")

    print(
        "Rows:",
        len(df)
    )

    print(
        "Start:",
        df["date"].min().date()
    )

    print(
        "End:",
        df["date"].max().date()
    )


    # --------------------------------------------------------
    # DATA REQUIREMENT
    # --------------------------------------------------------

    minimum_rows = 15

    if len(df) < minimum_rows:

        raise ValueError(
            f"At least {minimum_rows} BDI observations "
            f"are required. Only {len(df)} found."
        )


    # --------------------------------------------------------
    # CREATE FEATURES
    # --------------------------------------------------------

    feature_data = create_features(
        df
    )


    feature_data = feature_data.dropna(
        subset=FEATURE_COLUMNS + ["bdi"]
    )


    if len(feature_data) < 8:

        raise ValueError(
            "Not enough usable rows after feature creation."
        )


    X = feature_data[
        FEATURE_COLUMNS
    ]

    y = feature_data[
        "bdi"
    ]


    # ========================================================
    # CHRONOLOGICAL TRAIN / TEST SPLIT
    # ========================================================

    split_index = int(
        len(feature_data) * 0.80
    )


    X_train = X.iloc[
        :split_index
    ]

    X_test = X.iloc[
        split_index:
    ]


    y_train = y.iloc[
        :split_index
    ]

    y_test = y.iloc[
        split_index:
    ]


    print(
        "\nTraining rows:",
        len(X_train)
    )

    print(
        "Testing rows:",
        len(X_test)
    )


    # ========================================================
    # RANDOM FOREST
    # ========================================================

    model = RandomForestRegressor(

        n_estimators=300,

        max_depth=8,

        min_samples_leaf=2,

        random_state=42,

        n_jobs=-1
    )


    print(
        "\nTraining Random Forest..."
    )


    model.fit(
        X_train,
        y_train
    )


    print(
        "Model trained successfully!"
    )


    # ========================================================
    # TEST PERFORMANCE
    # ========================================================

    y_pred = model.predict(
        X_test
    )


    mae = mean_absolute_error(
        y_test,
        y_pred
    )


    rmse = np.sqrt(
        mean_squared_error(
            y_test,
            y_pred
        )
    )


    print(
        "\n========== MODEL PERFORMANCE =========="
    )


    print(
        "MAE :",
        round(mae, 2)
    )


    print(
        "RMSE:",
        round(rmse, 2)
    )


    # ========================================================
    # SAMPLE PREDICTIONS
    # ========================================================

    results = pd.DataFrame({

        "Date":
            feature_data.iloc[
                split_index:
            ]["date"].values,

        "Actual BDI":
            y_test.values,

        "Predicted BDI":
            y_pred

    })


    print(
        "\n========== SAMPLE PREDICTIONS =========="
    )

    print(
        results.to_string(
            index=False
        )
    )


    # ========================================================
    # SAVE MODEL
    # ========================================================

    os.makedirs(
        "models",
        exist_ok=True
    )


    model_package = {

        "model":
            model,

        "features":
            FEATURE_COLUMNS,

        "lags":
            LAGS,

        "rolling_windows":
            ROLLING_WINDOWS,

        "training_rows":
            len(X_train),

        "testing_rows":
            len(X_test),

        "mae":
            float(mae),

        "rmse":
            float(rmse),

        "last_training_date":
            df["date"].max().strftime(
                "%Y-%m-%d"
            )
    }


    joblib.dump(
        model_package,
        MODEL_PATH
    )


    print(
        "\nModel saved successfully!"
    )

    print(
        "Location:",
        MODEL_PATH
    )


    print(
        "\n========== TRAINING COMPLETE =========="
    )


    return model_package


# ============================================================
# RECURSIVE FORECAST
# ============================================================

def forecast_bdi(
    forecast_days=30
):

    # --------------------------------------------------------
    # LOAD MODEL
    # --------------------------------------------------------

    if not os.path.exists(
        MODEL_PATH
    ):

        print(
            "BDI model not found."
        )

        print(
            "Training model first..."
        )

        train_bdi_model()


    model_package = joblib.load(
        MODEL_PATH
    )


    model = model_package[
        "model"
    ]


    # --------------------------------------------------------
    # LOAD LATEST HISTORY
    # --------------------------------------------------------

    history = load_bdi_history()


    if len(history) < 8:

        raise ValueError(
            "Not enough BDI history for forecasting."
        )


    # --------------------------------------------------------
    # WORKING SERIES
    # --------------------------------------------------------

    values = list(
        history["bdi"].astype(float)
    )


    last_date = (
        history["date"].max()
    )


    forecasts = []


    # ========================================================
    # RECURSIVE FORECASTING
    # ========================================================

    for step in range(
        1,
        forecast_days + 1
    ):


        # ----------------------------------------------------
        # TEMPORARY DATAFRAME
        # ----------------------------------------------------

        temp_dates = pd.date_range(

            start=(
                last_date
                -
                pd.Timedelta(
                    days=len(values) - 1
                )
            ),

            periods=len(values),

            freq="D"
        )


        temp_df = pd.DataFrame({

            "date":
                temp_dates,

            "bdi":
                values
        })


        # ----------------------------------------------------
        # CREATE FEATURES
        # ----------------------------------------------------

        temp_features = create_features(
            temp_df
        )


        latest = temp_features.iloc[
            -1
        ]


        # ----------------------------------------------------
        # FEATURE VECTOR
        # ----------------------------------------------------

        X_future = pd.DataFrame([{

            feature:
                latest[feature]

            for feature in FEATURE_COLUMNS
        }])


        # ----------------------------------------------------
        # PREDICT NEXT BDI
        # ----------------------------------------------------

        predicted_bdi = float(
            model.predict(
                X_future
            )[0]
        )


        # ----------------------------------------------------
        # SANITY CHECK
        # ----------------------------------------------------

        if predicted_bdi < 0:

            predicted_bdi = 0.0


        # ----------------------------------------------------
        # NEXT DATE
        # ----------------------------------------------------

        forecast_date = (
            last_date
            +
            pd.Timedelta(
                days=step
            )
        )


        forecasts.append({

            "date":
                forecast_date.strftime(
                    "%Y-%m-%d"
                ),

            "predicted_bdi":
                round(
                    predicted_bdi,
                    2
                )
        })


        # ----------------------------------------------------
        # ADD PREDICTION TO SERIES
        # ----------------------------------------------------

        values.append(
            predicted_bdi
        )


    # ========================================================
    # SELECT KEY HORIZONS
    # ========================================================

    result = {

        "current_bdi":
            float(
                history["bdi"].iloc[-1]
            ),

        "last_historical_date":
            history["date"].iloc[-1]
            .strftime("%Y-%m-%d"),

        "forecast": {

            "7_day":
                forecasts[6]["predicted_bdi"]
                if forecast_days >= 7
                else None,

            "15_day":
                forecasts[14]["predicted_bdi"]
                if forecast_days >= 15
                else None,

            "30_day":
                forecasts[29]["predicted_bdi"]
                if forecast_days >= 30
                else None
        },

        "daily_forecast":
            forecasts
    }


    return result


# ============================================================
# DIRECT TEST
# ============================================================

if __name__ == "__main__":

    print(
        "\nStarting BDI forecasting system..."
    )


    # --------------------------------------------------------
    # TRAIN
    # --------------------------------------------------------

    try:

        train_bdi_model()

    except Exception as error:

        print(
            "\nTraining failed:"
        )

        print(error)

        raise SystemExit(1)


    # --------------------------------------------------------
    # FORECAST
    # --------------------------------------------------------

    print(
        "\n"
        + "=" * 60
    )

    print(
        "BDI FUTURE FORECAST"
    )

    print(
        "=" * 60
    )


    try:

        result = forecast_bdi(
            forecast_days=30
        )


        print(
            "\nCurrent BDI:",
            result["current_bdi"]
        )


        print(
            "Historical date:",
            result["last_historical_date"]
        )


        print(
            "\n7-Day BDI:",
            result["forecast"]["7_day"]
        )


        print(
            "15-Day BDI:",
            result["forecast"]["15_day"]
        )


        print(
            "30-Day BDI:",
            result["forecast"]["30_day"]
        )


        print(
            "\n========== DAILY FORECAST =========="
        )


        for item in result[
            "daily_forecast"
        ]:

            print(
                item["date"],
                "→",
                item["predicted_bdi"]
            )


    except Exception as error:

        print(
            "\nForecasting failed:"
        )

        print(error)