import os
import joblib
import numpy as np
import pandas as pd

from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import (
    mean_absolute_error,
    mean_squared_error,
    r2_score
)


# ============================================================
# CONFIGURATION
# ============================================================

DATA_FILE = "data/port_congestion_history.csv"

MODEL_FILE = (
    "models/port_congestion_forecasting_model.pkl"
)

PORT_NAME = "Paradip"

HORIZONS = [7, 15, 30]

LAGS = [
    1,
    2,
    3,
    5,
    7,
    14,
    21,
    30
]

ROLLING_WINDOWS = [
    3,
    7,
    14,
    30
]


# ============================================================
# LOAD DATA
# ============================================================

def load_congestion_data(
    port_name=PORT_NAME
):

    if not os.path.exists(DATA_FILE):

        raise FileNotFoundError(
            f"Congestion data not found: {DATA_FILE}"
        )

    df = pd.read_csv(
        DATA_FILE
    )

    if df.empty:

        raise ValueError(
            "Congestion dataset is empty."
        )

    required_columns = [
        "date",
        "port",
        "berthed_vessels",
        "waiting_vessels",
        "congestion_score"
    ]

    missing_columns = [
        column
        for column in required_columns
        if column not in df.columns
    ]

    if missing_columns:

        raise ValueError(
            f"Missing columns: {missing_columns}"
        )

    # --------------------------------------------------------
    # Date
    # --------------------------------------------------------

    df["date"] = pd.to_datetime(
        df["date"],
        errors="coerce"
    )

    # --------------------------------------------------------
    # Numeric columns
    # --------------------------------------------------------

    numeric_columns = [
        "berthed_vessels",
        "waiting_vessels",
        "congestion_score"
    ]

    for column in numeric_columns:

        df[column] = pd.to_numeric(
            df[column],
            errors="coerce"
        )

    # --------------------------------------------------------
    # Remove invalid rows
    # --------------------------------------------------------

    df = df.dropna(
        subset=[
            "date",
            "berthed_vessels",
            "waiting_vessels",
            "congestion_score"
        ]
    )

    # --------------------------------------------------------
    # Select port
    # --------------------------------------------------------

    df = df[
        df["port"].astype(str).str.strip().str.lower()
        == port_name.lower()
    ]

    if df.empty:

        raise ValueError(
            f"No data found for port: {port_name}"
        )

    # --------------------------------------------------------
    # Sort
    # --------------------------------------------------------

    df = (
        df
        .sort_values("date")
        .drop_duplicates(
            subset=["date"],
            keep="last"
        )
        .reset_index(drop=True)
    )

    # --------------------------------------------------------
    # Basic validation
    # --------------------------------------------------------

    if len(df) < 40:

        raise ValueError(
            f"Only {len(df)} historical rows available "
            f"for {port_name}. "
            f"At least 40 rows are required."
        )

    return df


# ============================================================
# CHECK DATE CONTINUITY
# ============================================================

def check_date_continuity(df):

    dates = (
        df["date"]
        .sort_values()
        .reset_index(drop=True)
    )

    expected_dates = pd.date_range(
        start=dates.min(),
        end=dates.max(),
        freq="D"
    )

    missing_dates = (
        expected_dates
        .difference(dates)
    )

    print(
        "\nDate continuity check:"
    )

    print(
        f"Expected dates: {len(expected_dates)}"
    )

    print(
        f"Available reports: {len(dates)}"
    )

    print(
        f"Missing dates: {len(missing_dates)}"
    )

    if len(missing_dates) > 0:

        print(
            "Missing date(s):"
        )

        for date in missing_dates:

            print(
                f"  {date.strftime('%Y-%m-%d')}"
            )

    else:

        print(
            "No missing dates."
        )

    return missing_dates


# ============================================================
# CREATE FEATURES
# ============================================================

def create_features(df):

    data = df.copy()

    data = (
        data
        .sort_values("date")
        .reset_index(drop=True)
    )

    # ========================================================
    # CALENDAR FEATURES
    # ========================================================

    data["year"] = (
        data["date"].dt.year
    )

    data["month"] = (
        data["date"].dt.month
    )

    data["day"] = (
        data["date"].dt.day
    )

    data["day_of_week"] = (
        data["date"].dt.dayofweek
    )

    data["day_of_year"] = (
        data["date"].dt.dayofyear
    )

    # ========================================================
    # LAG FEATURES
    # ========================================================

    for lag in LAGS:

        data[
            f"congestion_lag_{lag}"
        ] = (
            data["congestion_score"]
            .shift(lag)
        )

        data[
            f"waiting_lag_{lag}"
        ] = (
            data["waiting_vessels"]
            .shift(lag)
        )

        data[
            f"berthed_lag_{lag}"
        ] = (
            data["berthed_vessels"]
            .shift(lag)
        )

    # ========================================================
    # ROLLING FEATURES
    # ========================================================

    shifted_score = (
        data["congestion_score"]
        .shift(1)
    )

    shifted_waiting = (
        data["waiting_vessels"]
        .shift(1)
    )

    shifted_berthed = (
        data["berthed_vessels"]
        .shift(1)
    )

    for window in ROLLING_WINDOWS:

        data[
            f"rolling_score_mean_{window}"
        ] = (
            shifted_score
            .rolling(window)
            .mean()
        )

        data[
            f"rolling_score_std_{window}"
        ] = (
            shifted_score
            .rolling(window)
            .std()
        )

        data[
            f"rolling_waiting_mean_{window}"
        ] = (
            shifted_waiting
            .rolling(window)
            .mean()
        )

        data[
            f"rolling_waiting_std_{window}"
        ] = (
            shifted_waiting
            .rolling(window)
            .std()
        )

        data[
            f"rolling_berthed_mean_{window}"
        ] = (
            shifted_berthed
            .rolling(window)
            .mean()
        )

        data[
            f"rolling_berthed_std_{window}"
        ] = (
            shifted_berthed
            .rolling(window)
            .std()
        )

    # ========================================================
    # CHANGE FEATURES
    # ========================================================

    data["score_change_1"] = (
        data["congestion_score"]
        -
        data["congestion_score"].shift(1)
    )

    data["score_change_3"] = (
        data["congestion_score"]
        -
        data["congestion_score"].shift(3)
    )

    data["waiting_change_1"] = (
        data["waiting_vessels"]
        -
        data["waiting_vessels"].shift(1)
    )

    data["waiting_change_3"] = (
        data["waiting_vessels"]
        -
        data["waiting_vessels"].shift(3)
    )

    data["berthed_change_1"] = (
        data["berthed_vessels"]
        -
        data["berthed_vessels"].shift(1)
    )

    data["berthed_change_3"] = (
        data["berthed_vessels"]
        -
        data["berthed_vessels"].shift(3)
    )

    # ========================================================
    # RETURN FEATURES
    # ========================================================

    previous_score = (
        data["congestion_score"]
        .shift(1)
    )

    data["score_return_1"] = (
        (
            data["congestion_score"]
            -
            previous_score
        )
        /
        previous_score.replace(
            0,
            np.nan
        )
    )

    previous_score_3 = (
        data["congestion_score"]
        .shift(3)
    )

    data["score_return_3"] = (
        (
            data["congestion_score"]
            -
            previous_score_3
        )
        /
        previous_score_3.replace(
            0,
            np.nan
        )
    )

    # ========================================================
    # WAITING / BERTHED RATIO
    # ========================================================

    data["waiting_berthed_ratio"] = (
        data["waiting_vessels"]
        /
        data["berthed_vessels"].replace(
            0,
            np.nan
        )
    )

    # ========================================================
    # CLEAN
    # ========================================================

    data = data.replace(
        [np.inf, -np.inf],
        np.nan
    )

    data = data.dropna(
        subset=[
            column
            for column in data.columns
            if column != "date"
        ]
    )

    data = (
        data
        .reset_index(drop=True)
    )

    return data


# ============================================================
# CREATE FUTURE TARGET
# ============================================================

def create_target(
    df,
    horizon
):

    target = df[
        [
            "date",
            "congestion_score"
        ]
    ].copy()

    # --------------------------------------------------------
    # For row at date T,
    # target is congestion at T + horizon days.
    #
    # We create target_date = actual future date
    # and merge on dates.
    # --------------------------------------------------------

    target["target_date"] = (
        target["date"]
        -
        pd.Timedelta(
            days=horizon
        )
    )

    target = target.rename(
        columns={
            "congestion_score":
                f"target_{horizon}"
        }
    )

    return target[
        [
            "target_date",
            f"target_{horizon}"
        ]
    ]


# ============================================================
# BUILD TRAINING DATA
# ============================================================

def build_training_data(
    df,
    horizon
):

    features = create_features(
        df
    )

    target = create_target(
        df,
        horizon
    )

    data = features.merge(
        target,
        left_on="date",
        right_on="target_date",
        how="left"
    )

    data = data.drop(
        columns=[
            "target_date"
        ]
    )

    target_column = (
        f"target_{horizon}"
    )

    data = data.dropna(
        subset=[
            target_column
        ]
    )

    return data


# ============================================================
# GET FEATURE COLUMNS
# ============================================================

def get_feature_columns():

    feature_columns = [

        # Calendar
        "year",
        "month",
        "day",
        "day_of_week",
        "day_of_year",

        # Change
        "score_change_1",
        "score_change_3",

        "waiting_change_1",
        "waiting_change_3",

        "berthed_change_1",
        "berthed_change_3",

        # Returns
        "score_return_1",
        "score_return_3",

        # Ratio
        "waiting_berthed_ratio"
    ]

    # --------------------------------------------------------
    # Lag features
    # --------------------------------------------------------

    for lag in LAGS:

        feature_columns.extend(
            [
                f"congestion_lag_{lag}",
                f"waiting_lag_{lag}",
                f"berthed_lag_{lag}"
            ]
        )

    # --------------------------------------------------------
    # Rolling features
    # --------------------------------------------------------

    for window in ROLLING_WINDOWS:

        feature_columns.extend(
            [
                f"rolling_score_mean_{window}",
                f"rolling_score_std_{window}",

                f"rolling_waiting_mean_{window}",
                f"rolling_waiting_std_{window}",

                f"rolling_berthed_mean_{window}",
                f"rolling_berthed_std_{window}"
            ]
        )

    return feature_columns


# ============================================================
# TRAIN ONE MODEL
# ============================================================

def train_model(
    df,
    horizon
):

    data = build_training_data(
        df,
        horizon
    )

    # Allow the 30-day model to train on the currently
    # available 24 usable rows.
    # This is intentionally a low-data/demo-stage model.
    MINIMUM_ROWS = 20

    if len(data) < MINIMUM_ROWS:

        raise ValueError(
            f"Not enough training rows for "
            f"{horizon}-day model. "
            f"Available: {len(data)}. "
            f"Minimum required: {MINIMUM_ROWS}"
        )

    target_column = (
        f"target_{horizon}"
    )

    feature_columns = (
        get_feature_columns()
    )

    X = data[
        feature_columns
    ]

    y = data[
        target_column
    ]

    # ========================================================
    # CHRONOLOGICAL TRAIN / TEST SPLIT
    # ========================================================

    split_index = int(
        len(data) * 0.80
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
        f"\n{'-' * 60}"
    )

    print(
        f"Training {horizon}-day congestion model"
    )

    print(
        f"Training rows: {len(X_train)}"
    )

    print(
        f"Testing rows: {len(X_test)}"
    )

    # ========================================================
    # RANDOM FOREST
    # ========================================================

    model = RandomForestRegressor(

        n_estimators=300,

        max_depth=10,

        min_samples_leaf=2,

        random_state=42,

        n_jobs=-1
    )

    model.fit(
        X_train,
        y_train
    )

    # ========================================================
    # PREDICTION
    # ========================================================

    predictions = model.predict(
        X_test
    )

    # ========================================================
    # METRICS
    # ========================================================

    mae = mean_absolute_error(
        y_test,
        predictions
    )

    rmse = np.sqrt(
        mean_squared_error(
            y_test,
            predictions
        )
    )

    r2 = r2_score(
        y_test,
        predictions
    )

    performance = {

        "mae":
            round(
                float(mae),
                4
            ),

        "rmse":
            round(
                float(rmse),
                4
            ),

        "r2":
            round(
                float(r2),
                4
            ),

        "train_rows":
            len(X_train),

        "test_rows":
            len(X_test)
    }

    # ========================================================
    # FEATURE IMPORTANCE
    # ========================================================

    importance = pd.DataFrame({

        "feature":
            feature_columns,

        "importance":
            model.feature_importances_
    })

    importance = (
        importance
        .sort_values(
            "importance",
            ascending=False
        )
        .reset_index(
            drop=True
        )
    )

    print(
        f"\nPerformance:"
    )

    print(
        f"MAE  : {performance['mae']}"
    )

    print(
        f"RMSE : {performance['rmse']}"
    )

    print(
        f"R²   : {performance['r2']}"
    )

    print(
        "\nTop features:"
    )

    print(
        importance
        .head(10)
        .to_string(
            index=False
        )
    )

    return {

        "model":
            model,

        "features":
            feature_columns,

        "performance":
            performance,

        "feature_importance":
            importance
            .head(20)
            .to_dict(
                orient="records"
            )
    }


# ============================================================
# TRAIN ALL HORIZONS
# ============================================================

def train_all_models(
    port_name=PORT_NAME
):

    print(
        "\n" + "=" * 70
    )

    print(
        "PARADIP PORT CONGESTION FORECASTING"
    )

    print(
        "=" * 70
    )

    # ========================================================
    # LOAD DATA
    # ========================================================

    df = load_congestion_data(
        port_name
    )

    print(
        f"\nPort: {port_name}"
    )

    print(
        f"Historical rows: {len(df)}"
    )

    print(
        f"Start date: "
        f"{df['date'].min().strftime('%Y-%m-%d')}"
    )

    print(
        f"End date: "
        f"{df['date'].max().strftime('%Y-%m-%d')}"
    )

    # ========================================================
    # DATE CHECK
    # ========================================================

    check_date_continuity(
        df
    )

    # ========================================================
    # TRAIN
    # ========================================================

    all_models = {}

    for horizon in HORIZONS:

        try:

            result = train_model(
                df,
                horizon
            )

            all_models[
                horizon
            ] = result

        except Exception as error:

            print(
                f"\nCould not train "
                f"{horizon}-day model:"
            )

            print(
                error
            )

    if not all_models:

        raise RuntimeError(
            "No congestion models were trained."
        )

    return all_models


# ============================================================
# SAVE MODELS
# ============================================================

def save_models(
    all_models,
    port_name=PORT_NAME
):

    os.makedirs(
        "models",
        exist_ok=True
    )

    package = {

        "models":
            all_models,

        "horizons":
            list(
                all_models.keys()
            ),

        "port":
            port_name,

        "target":
            "future_port_congestion_score",

        "data_source":
            DATA_FILE
    }

    joblib.dump(
        package,
        MODEL_FILE
    )

    print(
        "\n" + "=" * 70
    )

    print(
        "MODEL SAVED"
    )

    print(
        "=" * 70
    )

    print(
        f"File: {MODEL_FILE}"
    )

    print(
        f"Port: {port_name}"
    )

    print(
        f"Horizons: "
        f"{list(all_models.keys())}"
    )


# ============================================================
# CONGESTION LEVEL
# ============================================================

def get_congestion_level(
    score
):

    if score < 10:

        return "Low"

    elif score < 25:

        return "Moderate"

    elif score < 40:

        return "High"

    else:

        return "Severe"


# ============================================================
# FORECAST CONGESTION
# ============================================================

def forecast_congestion(
    port_name=PORT_NAME
):

    if not os.path.exists(
        MODEL_FILE
    ):

        raise FileNotFoundError(
            f"Model file not found: "
            f"{MODEL_FILE}"
        )

    package = joblib.load(
        MODEL_FILE
    )

    df = load_congestion_data(
        port_name
    )

    features = create_features(
        df
    )

    if features.empty:

        raise ValueError(
            "Could not create latest features."
        )

    latest = features.iloc[
        -1:
    ]

    latest_date = (
        df["date"].iloc[-1]
    )

    current_score = float(
        df[
            "congestion_score"
        ].iloc[-1]
    )

    forecasts = {}

    # ========================================================
    # FORECAST EACH HORIZON
    # ========================================================

    for horizon in package[
        "horizons"
    ]:

        model_info = package[
            "models"
        ][horizon]

        model = model_info[
            "model"
        ]

        feature_columns = (
            model_info["features"]
        )

        X = latest[
            feature_columns
        ]

        prediction = model.predict(
            X
        )[0]

        # Keep score between 0 and 100
        prediction = max(
            0,
            min(
                100,
                float(prediction)
            )
        )

        future_date = (
            latest_date
            +
            pd.Timedelta(
                days=horizon
            )
        )

        forecasts[
            f"{horizon}_day"
        ] = {

            "date":
                future_date.strftime(
                    "%Y-%m-%d"
                ),

            "score":
                round(
                    prediction,
                    2
                ),

            "level":
                get_congestion_level(
                    prediction
                )
        }

    return {

        "port":
            port_name,

        "reference_date":
            latest_date.strftime(
                "%Y-%m-%d"
            ),

        "current_congestion":
            round(
                current_score,
                2
            ),

        "current_level":
            get_congestion_level(
                current_score
            ),

        "forecast":
            forecasts,

        "history_rows":
            len(df)
    }


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    try:

        # ----------------------------------------------------
        # Train
        # ----------------------------------------------------

        models = train_all_models(
            PORT_NAME
        )

        # ----------------------------------------------------
        # Save
        # ----------------------------------------------------

        save_models(
            models,
            PORT_NAME
        )

        # ----------------------------------------------------
        # Forecast
        # ----------------------------------------------------

        print(
            "\n" + "=" * 70
        )

        print(
            "FUTURE PARADIP CONGESTION FORECAST"
        )

        print(
            "=" * 70
        )

        forecast = forecast_congestion(
            PORT_NAME
        )

        print(
            f"\nPort: "
            f"{forecast['port']}"
        )

        print(
            f"Reference date: "
            f"{forecast['reference_date']}"
        )

        print(
            f"Current congestion: "
            f"{forecast['current_congestion']}"
        )

        print(
            f"Current level: "
            f"{forecast['current_level']}"
        )

        for horizon, result in (
            forecast["forecast"]
            .items()
        ):

            print(
                f"\n{horizon}:"
            )

            print(
                f"  Date  : "
                f"{result['date']}"
            )

            print(
                f"  Score : "
                f"{result['score']}"
            )

            print(
                f"  Level : "
                f"{result['level']}"
            )

    except Exception as error:

        print(
            "\nERROR:"
        )

        print(
            error
        )