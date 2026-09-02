from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.metrics import mean_absolute_error, mean_squared_error
from sklearn.ensemble import RandomForestRegressor


# ============================================================
# PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data" / "processed"

TEST_WEEKS = 104


# ============================================================
# METRICS
# ============================================================

def calculate_metrics(actual, predicted):

    mae = mean_absolute_error(actual, predicted)

    rmse = np.sqrt(
        mean_squared_error(actual, predicted)
    )

    return mae, rmse


# ============================================================
# EVALUATE ONE TARGET
# ============================================================

def evaluate_target(target_name, file_name):

    file_path = DATA_DIR / file_name

    df = pd.read_csv(file_path)

    df["Date"] = pd.to_datetime(df["Date"])

    df = (
        df
        .sort_values("Date")
        .reset_index(drop=True)
    )

    # --------------------------------------------------------
    # Train / test split
    # --------------------------------------------------------

    train = df.iloc[:-TEST_WEEKS].copy()
    test = df.iloc[-TEST_WEEKS:].copy()

    actual = test["target"]

    # --------------------------------------------------------
    # MODEL 1 — Naive
    # --------------------------------------------------------

    naive_predictions = test[
        f"{target_name}_lag_1"
    ]

    naive_mae, naive_rmse = calculate_metrics(
        actual,
        naive_predictions
    )

    # --------------------------------------------------------
    # MODEL 2 — Seasonal Naive
    # --------------------------------------------------------
    #
    # Predict this week's value using approximately
    # the same week last year.
    #
    # We already have lag_52.
    # --------------------------------------------------------

    seasonal_predictions = test[
        f"{target_name}_lag_52"
    ]

    seasonal_mae, seasonal_rmse = calculate_metrics(
        actual,
        seasonal_predictions
    )

    # --------------------------------------------------------
    # MODEL 3 — Random Forest
    # --------------------------------------------------------

    excluded = [
        "Date",
        "target"
    ]

    feature_columns = [
        column
        for column in df.columns
        if column not in excluded
    ]

    X_train = train[feature_columns]
    y_train = train["target"]

    X_test = test[feature_columns]

    model = RandomForestRegressor(
        n_estimators=500,
        max_depth=12,
        min_samples_leaf=2,
        random_state=42,
        n_jobs=-1
    )

    model.fit(
        X_train,
        y_train
    )

    ml_predictions = model.predict(X_test)

    ml_mae, ml_rmse = calculate_metrics(
        actual,
        ml_predictions
    )

    # --------------------------------------------------------
    # Results
    # --------------------------------------------------------

    print("\n")
    print("=" * 70)
    print(f"{target_name.upper()} — FORECASTING COMPARISON")
    print("=" * 70)

    print(
        f"\nEvaluation period: "
        f"{test['Date'].min().date()} → "
        f"{test['Date'].max().date()}"
    )

    print(f"Test observations: {len(test)}")

    print("\n" + "-" * 70)
    print(
        f"{'MODEL':<25}"
        f"{'MAE':>15}"
        f"{'RMSE':>15}"
    )
    print("-" * 70)

    print(
        f"{'Naive':<25}"
        f"{naive_mae:>15.4f}"
        f"{naive_rmse:>15.4f}"
    )

    print(
        f"{'Seasonal Naive':<25}"
        f"{seasonal_mae:>15.4f}"
        f"{seasonal_rmse:>15.4f}"
    )

    print(
        f"{'Random Forest':<25}"
        f"{ml_mae:>15.4f}"
        f"{ml_rmse:>15.4f}"
    )

    print("-" * 70)

    # --------------------------------------------------------
    # Determine winner
    # --------------------------------------------------------

    results = {
        "Naive": naive_mae,
        "Seasonal Naive": seasonal_mae,
        "Random Forest": ml_mae
    }

    winner = min(
        results,
        key=results.get
    )

    print(
        f"\nBest model by MAE: {winner}"
    )


# ============================================================
# RUN BOTH
# ============================================================

evaluate_target(
    "Gulf_Vessel",
    "gulf_ml_dataset.csv"
)

evaluate_target(
    "Pacific_Vessel",
    "pacific_ml_dataset.csv"
)


print("\n")
print("=" * 70)
print("FORECASTING EVALUATION COMPLETE")
print("=" * 70)