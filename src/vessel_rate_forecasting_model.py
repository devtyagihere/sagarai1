"""
KOBC Vessel Rate Forecasting Model - Multivariate Version

TARGET:
    KOBC vessel-class benchmark rate (USD/day)

VESSELS:
    Capesize, Panamax, Supramax

HORIZONS:
    7, 15, 30 KOBC market observations ahead

IMPORTANT:
    - KOBC is a business-day market series.
    - Horizons are market observations, not calendar days.
    - KOBC is a vessel-class time-charter benchmark, NOT a
      route-specific voyage rate.
    - During the current demo phase, historical BDI/oil/commodity
      inputs can come from data/demo_data.csv. Those values must be
      replaced by aligned real historical market data before claiming
      production performance.
"""

from pathlib import Path
import warnings

import joblib
import numpy as np
import pandas as pd

from sklearn.ensemble import RandomForestRegressor, ExtraTreesRegressor, HistGradientBoostingRegressor
from sklearn.linear_model import Ridge
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score


# ============================================================
# CONFIG
# ============================================================

VESSEL_DATA_FILE = Path("data/kobc_vessel_rates.csv")
DEMO_MARKET_FILE = Path("data/demo_data.csv")

# Optional real historical market files.
# If these exist, they are preferred over demo_data.csv.
BDI_HISTORY_FILE = Path("data/bdi_history.csv")
OIL_HISTORY_FILE = Path("data/oil_history.csv")
COMMODITY_HISTORY_FILE = Path("data/commodity_history.csv")

MODEL_FILE = Path(
    "models/kobc_vessel_rate_forecasting_models.pkl"
)

VESSELS = ["Capesize", "Panamax", "Supramax"]
HORIZONS = [7, 15, 30]

LAGS = [1, 2, 3, 5, 7, 10, 14, 21, 30, 45, 60]
ROLLING_WINDOWS = [3, 5, 7, 14, 21, 30, 45, 60]

MIN_ROWS = 120


# ============================================================
# SAFE NUMERIC
# ============================================================

def numeric(series):
    return pd.to_numeric(series, errors="coerce")


# ============================================================
# LOAD KOBC
# ============================================================

def load_vessel_data():
    if not VESSEL_DATA_FILE.exists():
        raise FileNotFoundError(
            f"{VESSEL_DATA_FILE} not found.\n"
            "Create it from official KOBC historical data."
        )

    df = pd.read_csv(VESSEL_DATA_FILE)

    required = ["date"] + VESSELS
    missing = [c for c in required if c not in df.columns]

    if missing:
        raise ValueError(
            f"Missing KOBC columns: {missing}"
        )

    df["date"] = pd.to_datetime(
        df["date"],
        errors="coerce"
    )

    for vessel in VESSELS:
        df[vessel] = numeric(df[vessel])

    df = (
        df.dropna(subset=["date"])
        .sort_values("date")
        .drop_duplicates("date")
        .reset_index(drop=True)
    )

    if len(df) < MIN_ROWS:
        raise ValueError(
            f"Only {len(df)} KOBC rows available. "
            f"At least {MIN_ROWS} are required."
        )

    return df


# ============================================================
# LOAD EXOGENOUS MARKET DATA
# ============================================================

def load_market_data(vessel_dates):
    """
    Preferred order:
        1. real historical BDI/oil/commodity files
        2. demo_data.csv for current development/testing

    Expected real files:

        bdi_history.csv
            date,bdi

        oil_history.csv
            date,oil_price

        commodity_history.csv
            date,commodity_price

    For demo_data.csv the existing columns are used.
    """

    base = pd.DataFrame({"date": vessel_dates})

    # --------------------------------------------------------
    # BDI
    # --------------------------------------------------------

    if BDI_HISTORY_FILE.exists():
        bdi = pd.read_csv(BDI_HISTORY_FILE)

        if "date" not in bdi.columns or "bdi" not in bdi.columns:
            raise ValueError(
                f"{BDI_HISTORY_FILE} must contain date,bdi"
            )

        bdi["date"] = pd.to_datetime(
            bdi["date"], errors="coerce"
        )
        bdi["bdi"] = numeric(bdi["bdi"])

        bdi = (
            bdi[["date", "bdi"]]
            .dropna()
            .drop_duplicates("date")
            .sort_values("date")
        )

        base = base.merge(
            bdi,
            on="date",
            how="left"
        )

        bdi_source = "real_historical_file"

    # --------------------------------------------------------
    # OIL
    # --------------------------------------------------------

    else:
        bdi_source = None

    if OIL_HISTORY_FILE.exists():
        oil = pd.read_csv(OIL_HISTORY_FILE)

        if (
            "date" not in oil.columns
            or "oil_price" not in oil.columns
        ):
            raise ValueError(
                f"{OIL_HISTORY_FILE} must contain "
                "date,oil_price"
            )

        oil["date"] = pd.to_datetime(
            oil["date"], errors="coerce"
        )
        oil["oil_price"] = numeric(
            oil["oil_price"]
        )

        oil = (
            oil[["date", "oil_price"]]
            .dropna()
            .drop_duplicates("date")
            .sort_values("date")
        )

        base = base.merge(
            oil,
            on="date",
            how="left"
        )

        oil_source = "real_historical_file"

    else:
        oil_source = None

    # --------------------------------------------------------
    # COMMODITY
    # --------------------------------------------------------

    if COMMODITY_HISTORY_FILE.exists():
        commodity = pd.read_csv(
            COMMODITY_HISTORY_FILE
        )

        if (
            "date" not in commodity.columns
            or "commodity_price" not in commodity.columns
        ):
            raise ValueError(
                f"{COMMODITY_HISTORY_FILE} must contain "
                "date,commodity_price"
            )

        commodity["date"] = pd.to_datetime(
            commodity["date"],
            errors="coerce"
        )
        commodity["commodity_price"] = numeric(
            commodity["commodity_price"]
        )

        commodity = (
            commodity[
                ["date", "commodity_price"]
            ]
            .dropna()
            .drop_duplicates("date")
            .sort_values("date")
        )

        base = base.merge(
            commodity,
            on="date",
            how="left"
        )

        commodity_source = "real_historical_file"

    else:
        commodity_source = None

    # --------------------------------------------------------
    # Demo fallback
    # --------------------------------------------------------

    if (
        bdi_source is None
        or oil_source is None
        or commodity_source is None
    ):
        if not DEMO_MARKET_FILE.exists():
            raise FileNotFoundError(
                "Real historical market files are missing and "
                "data/demo_data.csv was not found."
            )

        demo = pd.read_csv(DEMO_MARKET_FILE)

        required_demo = [
            "date",
            "bdi",
            "oil_price",
            "commodity_price",
        ]

        missing = [
            c for c in required_demo
            if c not in demo.columns
        ]

        if missing:
            raise ValueError(
                f"demo_data.csv missing columns: {missing}"
            )

        demo["date"] = pd.to_datetime(
            demo["date"],
            errors="coerce"
        )

        for col in [
            "bdi",
            "oil_price",
            "commodity_price",
        ]:
            demo[col] = numeric(demo[col])

        demo = (
            demo[
                [
                    "date",
                    "bdi",
                    "oil_price",
                    "commodity_price",
                ]
            ]
            .dropna(subset=["date"])
            .sort_values("date")
            .groupby("date", as_index=False)
            .mean()
        )

        # Fill only missing market columns from demo.
        # We never overwrite real historical values.
        for col in [
            "bdi",
            "oil_price",
            "commodity_price",
        ]:
            if col not in base.columns:
                base = base.merge(
                    demo[["date", col]],
                    on="date",
                    how="left"
                )
            else:
                fallback = demo[
                    ["date", col]
                ].rename(
                    columns={col: f"{col}_demo"}
                )

                base = base.merge(
                    fallback,
                    on="date",
                    how="left"
                )

                base[col] = base[col].fillna(
                    base[f"{col}_demo"]
                )

                base = base.drop(
                    columns=[f"{col}_demo"]
                )

    return base.sort_values("date").reset_index(
        drop=True
    )


# ============================================================
# BUILD MULTIVARIATE DATASET
# ============================================================

def build_dataset():
    df = load_vessel_data()

    market = load_market_data(
        df["date"]
    )

    df = df.merge(
        market,
        on="date",
        how="left"
    )

    market_columns = [
        "bdi",
        "oil_price",
        "commodity_price",
    ]

    # During the demo phase, demo_data.csv supplies the
    # historical market covariates. No random values are created.
    # When real historical files exist, load_market_data()
    # prefers them automatically.

    for col in market_columns:
        coverage = df[col].notna().mean()

        if coverage < 0.10:
            raise ValueError(
                f"Insufficient historical coverage for {col}. "
                "There is not enough overlap between the KOBC "
                "dates and the available market history."
            )

        # Only carry forward/backward real observations.
        # This is useful because commodity data can be lower
        # frequency than the daily KOBC series.
        df[col] = (
            df[col]
            .ffill()
            .bfill()
        )

    return (
        df
        .sort_values("date")
        .reset_index(drop=True)
    )


# ============================================================
# FEATURES
# ============================================================

def create_features(df, vessel):
    out = df[
        ["date", vessel, "bdi", "oil_price", "commodity_price"]
    ].copy()

    out = out.rename(
        columns={vessel: "value"}
    )

    # --------------------------------------------------------
    # Calendar
    # --------------------------------------------------------

    out["year"] = out["date"].dt.year
    out["month"] = out["date"].dt.month
    out["quarter"] = out["date"].dt.quarter
    out["day_of_week"] = out["date"].dt.dayofweek
    out["day_of_year"] = out["date"].dt.dayofyear
    out["week_of_year"] = (
        out["date"].dt.isocalendar().week.astype(int)
    )

    out["month_sin"] = np.sin(
        2 * np.pi * out["month"] / 12
    )
    out["month_cos"] = np.cos(
        2 * np.pi * out["month"] / 12
    )

    out["dow_sin"] = np.sin(
        2 * np.pi * out["day_of_week"] / 7
    )
    out["dow_cos"] = np.cos(
        2 * np.pi * out["day_of_week"] / 7
    )

    # --------------------------------------------------------
    # Vessel-rate lags
    # --------------------------------------------------------

    for lag in LAGS:
        out[f"rate_lag_{lag}"] = (
            out["value"].shift(lag)
        )

    shifted_rate = out["value"].shift(1)

    for window in ROLLING_WINDOWS:
        out[f"rate_mean_{window}"] = (
            shifted_rate.rolling(window).mean()
        )

        out[f"rate_std_{window}"] = (
            shifted_rate.rolling(window).std()
        )

        out[f"rate_min_{window}"] = (
            shifted_rate.rolling(window).min()
        )

        out[f"rate_max_{window}"] = (
            shifted_rate.rolling(window).max()
        )

    for period in [1, 3, 5, 7, 14, 30]:
        previous = out["value"].shift(
            period + 1
        )

        out[f"rate_change_{period}"] = (
            shifted_rate - previous
        )

        out[f"rate_return_{period}"] = (
            shifted_rate / previous - 1
        )

    # --------------------------------------------------------
    # BDI / oil / commodity history
    # ONLY PAST VALUES are used.
    # --------------------------------------------------------

    exogenous = [
        "bdi",
        "oil_price",
        "commodity_price",
    ]

    for column in exogenous:
        shifted = out[column].shift(1)

        for lag in [
            1, 2, 3, 5, 7, 14, 30
        ]:
            out[
                f"{column}_lag_{lag}"
            ] = out[column].shift(lag + 1)

        for window in [3, 7, 14, 30]:
            out[
                f"{column}_mean_{window}"
            ] = shifted.rolling(window).mean()

            out[
                f"{column}_std_{window}"
            ] = shifted.rolling(window).std()

        for period in [1, 3, 7, 14, 30]:
            previous = out[column].shift(
                period + 1
            )

            out[
                f"{column}_change_{period}"
            ] = shifted - previous

            out[
                f"{column}_return_{period}"
            ] = shifted / previous - 1

    # --------------------------------------------------------
    # Cross-market ratios / relationships
    # --------------------------------------------------------

    out["bdi_per_oil"] = (
        out["bdi"].shift(1)
        / out["oil_price"].shift(1)
    )

    out["bdi_per_commodity"] = (
        out["bdi"].shift(1)
        / out["commodity_price"].shift(1)
    )

    out["oil_commodity_ratio"] = (
        out["oil_price"].shift(1)
        / out["commodity_price"].shift(1)
    )

    out["rate_bdi_ratio"] = (
        out["value"].shift(1)
        / out["bdi"].shift(1)
    )

    out["rate_oil_ratio"] = (
        out["value"].shift(1)
        / out["oil_price"].shift(1)
    )

    out["rate_commodity_ratio"] = (
        out["value"].shift(1)
        / out["commodity_price"].shift(1)
    )

    out = out.replace(
        [np.inf, -np.inf],
        np.nan
    )

    return out


# ============================================================
# TARGET
# ============================================================

def create_target(df, vessel, horizon):
    """
    Predict the H-observation-ahead RATE CHANGE rather than
    the absolute rate level.

    This makes the ML task more useful for a market series where
    persistence is a strong baseline: the model learns the
    expected movement away from today's rate, while the final
    forecast is current_rate + predicted_change.
    """

    future_rate = df[vessel].shift(-horizon)
    current_rate = df[vessel]

    target = future_rate - current_rate

    return target


# ============================================================
# BUILD TRAINING TABLE
# ============================================================

def build_training_data(df, vessel, horizon):
    features = create_features(
        df,
        vessel
    )

    features["target_value"] = create_target(
        df,
        vessel,
        horizon
    )

    feature_columns = [
        c for c in features.columns
        if c not in {
            "date",
            "value",
            "target_value",
        }
    ]

    clean = features.dropna(
        subset=feature_columns + ["target_value"]
    ).copy()

    return clean, feature_columns


# ============================================================
# BASELINES
# ============================================================

def baseline_metrics(test):
    actual = test["target_value"].values

    # Because target_value is future_rate - current_rate,
    # persistence corresponds to predicting zero change.
    persistence = np.zeros(len(test), dtype=float)

    # A recent-trend baseline: use the latest observed movement
    # as the expected future movement.
    recent_mean = (
        test["rate_mean_7"].values
        - test["value"].values
    )

    result = {}

    for name, pred in [
        ("persistence", persistence),
        ("recent_mean_7", recent_mean),
    ]:
        result[name] = {
            "mae": float(
                mean_absolute_error(
                    actual,
                    pred
                )
            ),
            "rmse": float(
                np.sqrt(
                    mean_squared_error(
                        actual,
                        pred
                    )
                )
            ),
            "r2": float(
                r2_score(
                    actual,
                    pred
                )
            ),
        }

    return result


# ============================================================
# TRAIN ONE MODEL
# ============================================================

def train_one_model(df, vessel, horizon):
    data, feature_columns = build_training_data(
        df,
        vessel,
        horizon
    )

    if len(data) < 120:
        raise ValueError(
            f"{vessel} {horizon}-obs has only "
            f"{len(data)} usable rows."
        )

    # Chronological split.
    split = int(
        len(data) * 0.80
    )

    train = data.iloc[:split].copy()
    test = data.iloc[split:].copy()

    X_train = train[feature_columns]
    y_train = train["target_value"]

    X_test = test[feature_columns]
    y_test = test["target_value"]

    # --------------------------------------------------------
    # Random Forest
    # --------------------------------------------------------

    rf = RandomForestRegressor(
        n_estimators=600,
        max_depth=12,
        min_samples_leaf=4,
        max_features=0.65,
        random_state=42,
        n_jobs=-1,
    )

    rf.fit(
        X_train,
        y_train
    )

    rf_pred = rf.predict(
        X_test
    )

    # --------------------------------------------------------
    # Extra Trees
    # --------------------------------------------------------

    et = ExtraTreesRegressor(
        n_estimators=500,
        max_depth=12,
        min_samples_leaf=4,
        max_features=0.65,
        random_state=42,
        n_jobs=-1,
    )

    et.fit(
        X_train,
        y_train
    )

    et_pred = et.predict(
        X_test
    )

    # --------------------------------------------------------
    # Ridge
    # --------------------------------------------------------

    ridge = Pipeline([
        (
            "scaler",
            StandardScaler()
        ),
        (
            "ridge",
            Ridge(alpha=20.0)
        ),
    ])

    ridge.fit(
        X_train,
        y_train
    )

    ridge_pred = ridge.predict(
        X_test
    )

    # --------------------------------------------------------
    # Ensemble
    # --------------------------------------------------------

    ensemble_pred = (
        0.50 * rf_pred
        + 0.30 * et_pred
        + 0.20 * ridge_pred
    )

    # --------------------------------------------------------
    # Metrics
    # --------------------------------------------------------

    ml_mae = mean_absolute_error(
        y_test,
        ensemble_pred
    )

    ml_rmse = np.sqrt(
        mean_squared_error(
            y_test,
            ensemble_pred
        )
    )

    ml_r2 = r2_score(
        y_test,
        ensemble_pred
    )

    baselines = baseline_metrics(
        test
    )

    persistence_mae = (
        baselines["persistence"]["mae"]
    )

    improvement = (
        (persistence_mae - ml_mae)
        / persistence_mae
        * 100
    )

    # --------------------------------------------------------
    # Honest selection
    # --------------------------------------------------------

    if ml_mae < persistence_mae:
        selected_method = "multivariate_ensemble"
    else:
        selected_method = "persistence"

    print(
        f"{vessel:10s} | "
        f"{horizon:2d}-obs | "
        f"train={len(train):3d} | "
        f"test={len(test):3d} | "
        f"ML MAE={ml_mae:,.2f} | "
        f"Persistence MAE={persistence_mae:,.2f} | "
        f"R2={ml_r2:.4f} | "
        f"ML vs persistence={improvement:+.1f}% | "
        f"SELECT={selected_method}"
    )

    return {
        "rf_model": rf,
        "extra_trees_model": et,
        "ridge_model": ridge,

        "blend_weights": {
            "random_forest": 0.50,
            "extra_trees": 0.30,
            "ridge": 0.20,
        },

        "selected_method": selected_method,

        "features": feature_columns,

        "metrics": {
            "mae": float(ml_mae),
            "rmse": float(ml_rmse),
            "r2": float(ml_r2),

            "persistence_mae": float(
                baselines["persistence"]["mae"]
            ),
            "persistence_rmse": float(
                baselines["persistence"]["rmse"]
            ),
            "persistence_r2": float(
                baselines["persistence"]["r2"]
            ),

            "recent_mean_7_mae": float(
                baselines["recent_mean_7"]["mae"]
            ),

            "improvement_vs_persistence_percent":
                float(improvement),

            "train_rows": len(train),
            "test_rows": len(test),
        },

        "vessel": vessel,
        "horizon": horizon,
        "horizon_type": "market_observations",
    }


# ============================================================
# TRAIN ALL
# ============================================================

def train_all_models():
    df = build_dataset()

    print("=" * 75)
    print(
        "KOBC MULTIVARIATE VESSEL-RATE FORECASTING"
    )
    print("=" * 75)

    print(
        f"Historical KOBC rows : {len(df)}"
    )

    print(
        f"Date range            : "
        f"{df['date'].min().date()} → "
        f"{df['date'].max().date()}"
    )

    print(
        "Horizon type          : MARKET OBSERVATIONS"
    )

    print(
        "Market features       : "
        "BDI + Oil + Commodity + KOBC history"
    )

    # Determine whether demo fallback was used.
    demo_used = (
        not BDI_HISTORY_FILE.exists()
        or not OIL_HISTORY_FILE.exists()
        or not COMMODITY_HISTORY_FILE.exists()
    )

    if demo_used:
        print(
            "WARNING: Demo BDI/oil/commodity history is being "
            "used for DEVELOPMENT/TESTING only."
        )
        print(
            "KOBC target remains official historical data."
        )
        print(
            "Replace demo market history with aligned real "
            "historical market data before production."
        )
    else:
        print(
            "Market data mode      : REAL HISTORICAL FILES"
        )

    models = {}

    for vessel in VESSELS:
        models[vessel] = {}

        for horizon in HORIZONS:
            try:
                models[vessel][horizon] = (
                    train_one_model(
                        df,
                        vessel,
                        horizon
                    )
                )

            except Exception as exc:
                print(
                    f"WARNING: {vessel} "
                    f"{horizon}-obs failed: {exc}"
                )

    if not any(
        models[vessel]
        for vessel in VESSELS
    ):
        raise RuntimeError(
            "No vessel model was trained."
        )

    package = {
        "models": models,

        "vessels": VESSELS,
        "horizons": HORIZONS,

        "horizon_type": "market_observations",

        "data_source": str(
            VESSEL_DATA_FILE
        ),

        "market_features": [
            "BDI",
            "Oil Price",
            "Commodity Price",
        ],

        "unit": "USD/day",

        "model_type": (
            "RandomForest + ExtraTrees + Ridge "
            "multivariate ensemble"
        ),

        "selection_rule": (
            "Use multivariate ML only when it beats "
            "persistence baseline on chronological holdout."
        ),

        "route_specific": False,

        "demo_market_data_used": demo_used,

        "warning": (
            "KOBC is a vessel-class time-charter "
            "benchmark in USD/day, not a route-specific "
            "voyage freight rate."
        ),
    }

    MODEL_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    joblib.dump(
        package,
        MODEL_FILE
    )

    print()
    print(
        f"Saved model package → {MODEL_FILE}"
    )

    return package


# ============================================================
# FORECAST ONE
# ============================================================

def forecast_one(
    df,
    model_info,
    vessel,
    horizon
):
    features = create_features(
        df,
        vessel
    )

    latest = features.iloc[-1]

    current = float(
        df[vessel].iloc[-1]
    )

    if model_info["selected_method"] == "persistence":
        # Persistence = zero future change.
        predicted_change = 0.0
        prediction = current

        rf_prediction = None
        et_prediction = None
        ridge_prediction = None

    else:
        X = latest[
            model_info["features"]
        ].to_frame().T

        rf_prediction = (
            model_info["rf_model"]
            .predict(X)[0]
        )

        et_prediction = (
            model_info["extra_trees_model"]
            .predict(X)[0]
        )

        ridge_prediction = (
            model_info["ridge_model"]
            .predict(X)[0]
        )

        weights = model_info[
            "blend_weights"
        ]

        predicted_change = (
            weights["random_forest"]
            * rf_prediction
            + weights["extra_trees"]
            * et_prediction
            + weights["ridge"]
            * ridge_prediction
        )

        prediction = current + predicted_change

    # Broad sanity guard on the final rate, while preserving
    # the ML model's direction and magnitude within a wide band.
    prediction = float(
        np.clip(
            prediction,
            current * 0.50,
            current * 1.50
        )
    )
    predicted_change = prediction - current

    target_date = (
        df["date"].iloc[-1]
        + pd.tseries.offsets.BDay(horizon)
    )

    return {
        "target_date":
            target_date.strftime("%Y-%m-%d"),

        "forecast":
            prediction,

        "predicted_change":
            float(predicted_change),

        "current":
            current,

        "rf_prediction":
            (
                None
                if rf_prediction is None
                else float(rf_prediction)
            ),

        "extra_trees_prediction":
            (
                None
                if et_prediction is None
                else float(et_prediction)
            ),

        "ridge_prediction":
            (
                None
                if ridge_prediction is None
                else float(ridge_prediction)
            ),

        "method":
            model_info["selected_method"],

        "horizon":
            horizon,

        "horizon_type":
            "market_observations",

        "unit":
            "USD/day",
    }


# ============================================================
# FORECAST ALL
# ============================================================

def forecast_vessel_rates():
    if not MODEL_FILE.exists():
        raise FileNotFoundError(
            "Model package not found. "
            "Run train_all_models() first."
        )

    package = joblib.load(
        MODEL_FILE
    )

    df = build_dataset()

    latest_date = df["date"].max()

    current = {}

    forecasts = {
        "7_day": {},
        "15_day": {},
        "30_day": {},
    }

    labels = {
        7: "7_day",
        15: "15_day",
        30: "30_day",
    }

    for vessel in VESSELS:
        current[vessel] = {
            "value": float(
                df[vessel].iloc[-1]
            ),
            "unit": "USD/day",
            "date":
                latest_date.strftime(
                    "%Y-%m-%d"
                ),
        }

        for horizon in HORIZONS:
            info = (
                package["models"]
                .get(vessel, {})
                .get(horizon)
            )

            if info is None:
                continue

            forecasts[
                labels[horizon]
            ][vessel] = forecast_one(
                df,
                info,
                vessel,
                horizon
            )

    return {
        "reference_date":
            latest_date.strftime(
                "%Y-%m-%d"
            ),

        "current":
            current,

        "forecast":
            forecasts,

        "unit":
            "USD/day",

        "source":
            "KOBC",

        "route_specific":
            False,

        "horizon_type":
            "market_observations",
    }


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":
    warnings.filterwarnings(
        "ignore"
    )

    train_all_models()

    result = forecast_vessel_rates()

    print()
    print("=" * 75)
    print(
        "CURRENT KOBC VESSEL BENCHMARKS"
    )
    print("=" * 75)

    for vessel, data in result[
        "current"
    ].items():
        print(
            f"{vessel:10s}: "
            f"${data['value']:,.2f}/day"
        )

    print()
    print("=" * 75)
    print(
        "7 / 15 / 30 MARKET-OBSERVATION FORECAST"
    )
    print("=" * 75)

    for horizon, vessel_data in result[
        "forecast"
    ].items():

        print(f"\n{horizon}:")

        for vessel, data in vessel_data.items():
            print(
                f"  {vessel:10s}: "
                f"${data['forecast']:,.2f}/day "
                f"on {data['target_date']} "
                f"[{data['method']}]"
            )
