import os
import joblib
import numpy as np
import pandas as pd

from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder


# ============================================================
# CONFIGURATION
# ============================================================

DATA_FILE = "data/demo_data.csv"
MODEL_FILE = "models/freight_forecasting_models.pkl"

HORIZONS = [7, 15, 30]

# Core features available for every destination
BASE_FEATURES = [
    "origin_port",
    "destination_port",
    "cargo_type",
    "bdi",
    "oil_price",
    "commodity_price",
    "commodity_demand",
    "weather_disruption",
    "usd_index",
    "year",
    "month",
    "day",
]

# Optional destination-specific feature
CONGESTION_FEATURE = "port_congestion"


# ============================================================
# LOAD DATA
# ============================================================

def load_data():
    if not os.path.exists(DATA_FILE):
        raise FileNotFoundError(
            f"Freight dataset not found: {DATA_FILE}"
        )

    df = pd.read_csv(DATA_FILE)

    if df.empty:
        raise ValueError("Freight dataset is empty.")

    required_columns = [
        "date",
        "origin_port",
        "destination_port",
        "cargo_type",
        "freight_rate",
        "bdi",
        "oil_price",
        "commodity_price",
        "commodity_demand",
        "weather_disruption",
        "usd_index",
    ]

    missing = [
        col for col in required_columns
        if col not in df.columns
    ]

    if missing:
        raise ValueError(
            f"Missing required columns: {missing}"
        )

    df["date"] = pd.to_datetime(
        df["date"],
        errors="coerce"
    )

    numeric_columns = [
        "freight_rate",
        "bdi",
        "oil_price",
        "commodity_price",
        "commodity_demand",
        "weather_disruption",
        "usd_index",
    ]

    # Congestion is optional.
    if CONGESTION_FEATURE in df.columns:
        numeric_columns.append(CONGESTION_FEATURE)

    for col in numeric_columns:
        df[col] = pd.to_numeric(
            df[col],
            errors="coerce"
        )

    df = df.dropna(
        subset=[
            "date",
            "origin_port",
            "destination_port",
            "cargo_type",
            "freight_rate",
        ]
    )

    df = df.sort_values("date").reset_index(drop=True)

    if len(df) < 100:
        raise ValueError(
            f"Only {len(df)} rows available. "
            "At least 100 rows are recommended."
        )

    return df


# ============================================================
# CREATE DATE FEATURES
# ============================================================

def add_date_features(df):
    data = df.copy()

    data["year"] = data["date"].dt.year
    data["month"] = data["date"].dt.month
    data["day"] = data["date"].dt.day

    return data


# ============================================================
# CREATE HORIZON TARGET
#
# IMPORTANT:
# Target is matched using the SAME:
#   origin + destination + cargo
#
# This avoids accidentally learning from a different route.
# ============================================================

def create_horizon_dataset(df, horizon):
    current = df.copy()

    future = df[
        [
            "date",
            "origin_port",
            "destination_port",
            "cargo_type",
            "freight_rate",
        ]
    ].copy()

    future["date"] = (
        future["date"]
        - pd.Timedelta(days=horizon)
    )

    future = future.rename(
        columns={
            "freight_rate":
                f"target_freight_{horizon}d"
        }
    )

    merged = current.merge(
        future,
        on=[
            "date",
            "origin_port",
            "destination_port",
            "cargo_type",
        ],
        how="inner",
    )

    return merged


# ============================================================
# CHECK CONGESTION DATA
# ============================================================

def congestion_signal_available(df):
    if CONGESTION_FEATURE not in df.columns:
        return False

    values = pd.to_numeric(
        df[CONGESTION_FEATURE],
        errors="coerce"
    ).dropna()

    if len(values) < 20:
        return False

    # A constant column contains no usable signal.
    if values.nunique() <= 1:
        return False

    return True


# ============================================================
# MODEL PIPELINE
# ============================================================

def build_pipeline(feature_columns):
    categorical_features = [
        "origin_port",
        "destination_port",
        "cargo_type",
    ]

    numeric_features = [
        col
        for col in feature_columns
        if col not in categorical_features
    ]

    preprocessor = ColumnTransformer(
        transformers=[
            (
                "categorical",
                OneHotEncoder(
                    handle_unknown="ignore"
                ),
                categorical_features,
            ),
            (
                "numeric",
                "passthrough",
                numeric_features,
            ),
        ],
        remainder="drop",
    )

    model = RandomForestRegressor(
        n_estimators=300,
        max_depth=15,
        min_samples_leaf=2,
        random_state=42,
        n_jobs=-1,
    )

    return Pipeline(
        steps=[
            ("preprocessor", preprocessor),
            ("model", model),
        ]
    )


# ============================================================
# TRAIN ONE MODEL
# ============================================================

def train_one_model(
    dataset,
    horizon,
    feature_columns,
    model_name,
):
    target_column = (
        f"target_freight_{horizon}d"
    )

    data = dataset.dropna(
        subset=[target_column]
    ).copy()

    if len(data) < 50:
        raise ValueError(
            f"{model_name}: only {len(data)} "
            f"usable rows for {horizon}-day horizon."
        )

    data = data.sort_values("date")

    X = data[feature_columns]
    y = data[target_column]

    # Chronological split.
    split_index = int(
        len(data) * 0.80
    )

    X_train = X.iloc[:split_index]
    X_test = X.iloc[split_index:]

    y_train = y.iloc[:split_index]
    y_test = y.iloc[split_index:]

    if len(X_test) == 0:
        raise ValueError(
            f"{model_name}: test set is empty."
        )

    pipeline = build_pipeline(
        feature_columns
    )

    pipeline.fit(
        X_train,
        y_train
    )

    predictions = pipeline.predict(
        X_test
    )

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
        "mae": round(float(mae), 4),
        "rmse": round(float(rmse), 4),
        "r2": round(float(r2), 4),
        "train_rows": len(X_train),
        "test_rows": len(X_test),
    }

    print(
        f"\n{model_name} | {horizon}-day"
    )
    print(
        f"Train rows : {len(X_train)}"
    )
    print(
        f"Test rows  : {len(X_test)}"
    )
    print(
        f"MAE        : {performance['mae']}"
    )
    print(
        f"RMSE       : {performance['rmse']}"
    )
    print(
        f"R²         : {performance['r2']}"
    )

    return {
        "model": pipeline,
        "features": feature_columns,
        "performance": performance,
        "model_type": model_name,
        "horizon": horizon,
    }


# ============================================================
# TRAIN ALL FREIGHT MODELS
#
# For every horizon we train:
#
# 1. BASE MODEL
#    Works for ANY destination.
#
# 2. CONGESTION MODEL
#    Used only when destination-specific congestion
#    history is actually available.
#
# This prevents non-Paradip ports from receiving fake
# congestion values.
# ============================================================

def train_all_models():
    df = load_data()
    df = add_date_features(df)

    congestion_available = (
        congestion_signal_available(df)
    )

    print("\n" + "=" * 70)
    print("FREIGHT FORECASTING MODEL TRAINING")
    print("=" * 70)

    print(
        f"\nDataset rows: {len(df)}"
    )

    print(
        "Routes:",
        df[
            [
                "origin_port",
                "destination_port",
            ]
        ]
        .drop_duplicates()
        .shape[0],
    )

    print(
        "Cargo types:",
        df["cargo_type"]
        .nunique()
    )

    print(
        "\nCongestion column:",
        CONGESTION_FEATURE
        in df.columns
    )

    print(
        "Usable congestion signal:",
        congestion_available
    )

    all_models = {
        "base": {},
        "congestion": {},
    }

    for horizon in HORIZONS:

        print(
            "\n" + "-" * 70
        )
        print(
            f"BUILDING {horizon}-DAY TARGET"
        )
        print(
            "-" * 70
        )

        horizon_data = create_horizon_dataset(
            df,
            horizon
        )

        if horizon_data.empty:
            print(
                f"No target rows for {horizon}-day."
            )
            continue

        # --------------------------------------------------------
        # BASE MODEL
        # --------------------------------------------------------

        try:
            result = train_one_model(
                horizon_data,
                horizon,
                BASE_FEATURES,
                "base",
            )

            all_models["base"][horizon] = result

        except Exception as error:
            print(
                f"Could not train base "
                f"{horizon}-day model: {error}"
            )

        # --------------------------------------------------------
        # CONGESTION MODEL
        #
        # IMPORTANT:
        # We only train it when the freight dataset itself
        # contains a real, varying congestion feature.
        #
        # The current Paradip congestion history is separate
        # from demo freight history, so it cannot legitimately
        # be merged into this model until overlapping historical
        # freight + congestion observations are available.
        # --------------------------------------------------------

        if congestion_available:

            congestion_features = (
                BASE_FEATURES
                + [CONGESTION_FEATURE]
            )

            try:
                result = train_one_model(
                    horizon_data,
                    horizon,
                    congestion_features,
                    "congestion",
                )

                all_models[
                    "congestion"
                ][horizon] = result

            except Exception as error:
                print(
                    f"Could not train congestion "
                    f"{horizon}-day model: {error}"
                )

        else:
            print(
                f"\nSkipping congestion model "
                f"for {horizon}-day."
            )
            print(
                "Reason: no valid historical "
                "congestion signal is aligned "
                "with the freight dataset."
            )

    if not all_models["base"]:
        raise RuntimeError(
            "No base freight models were trained."
        )

    return all_models


# ============================================================
# SAVE MODELS
# ============================================================

def save_models(all_models):
    os.makedirs(
        "models",
        exist_ok=True
    )

    package = {
        "models": all_models,
        "horizons": HORIZONS,
        "base_features": BASE_FEATURES,
        "optional_features": [
            CONGESTION_FEATURE
        ],
        "congestion_logic": (
            "Use congestion model only when "
            "destination-specific congestion "
            "data is available. Otherwise use "
            "base model."
        ),
        "data_source": DATA_FILE,
        "target": "future_freight_rate",
    }

    joblib.dump(
        package,
        MODEL_FILE
    )

    print(
        "\n" + "=" * 70
    )
    print("MODELS SAVED")
    print("=" * 70)

    print(
        f"File: {MODEL_FILE}"
    )

    print(
        "Base horizons:",
        list(all_models["base"].keys())
    )

    print(
        "Congestion horizons:",
        list(
            all_models["congestion"].keys()
        )
    )


# ============================================================
# LOAD MODELS
# ============================================================

def load_models():
    if not os.path.exists(
        MODEL_FILE
    ):
        raise FileNotFoundError(
            f"Model file not found: {MODEL_FILE}"
        )

    return joblib.load(
        MODEL_FILE
    )


# ============================================================
# PREDICT WITH OPTIONAL CONGESTION
#
# destination_has_congestion:
#     True  -> congestion model
#     False -> base model
#
# If congestion is unavailable, it is NOT replaced with 0.
# The base model is used instead.
# ============================================================

def predict_freight(
    input_data,
    horizon,
    destination_has_congestion=False,
):
    package = load_models()

    if destination_has_congestion:
        model_group = package[
            "models"
        ]["congestion"]

        if horizon not in model_group:
            raise ValueError(
                f"No congestion-enabled "
                f"{horizon}-day model available."
            )

        model_info = model_group[
            horizon
        ]

    else:
        model_group = package[
            "models"
        ]["base"]

        if horizon not in model_group:
            raise ValueError(
                f"No base {horizon}-day "
                f"freight model available."
            )

        model_info = model_group[
            horizon
        ]

    features = model_info[
        "features"
    ]

    row = pd.DataFrame(
        [input_data]
    )

    missing_features = [
        feature
        for feature in features
        if feature not in row.columns
    ]

    if missing_features:
        raise ValueError(
            f"Missing model inputs: "
            f"{missing_features}"
        )

    prediction = model_info[
        "model"
    ].predict(
        row[features]
    )[0]

    return float(prediction)


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    models = train_all_models()

    save_models(
        models
    )

    print(
        "\nTraining completed successfully."
    )
