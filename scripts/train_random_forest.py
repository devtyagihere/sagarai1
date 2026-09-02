from pathlib import Path

import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error


# --------------------------------------------------
# Paths
# --------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[1]
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"


# --------------------------------------------------
# Configuration
# --------------------------------------------------

TEST_WEEKS = 104

TARGETS = {
    "Gulf_Vessel": PROCESSED_DIR / "gulf_ml_dataset.csv",
    "Pacific_Vessel": PROCESSED_DIR / "pacific_ml_dataset.csv",
}


# --------------------------------------------------
# Train + evaluate
# --------------------------------------------------

def train_model(file_path, target_name):

    df = pd.read_csv(file_path)

    df["Date"] = pd.to_datetime(df["Date"])
    df = df.sort_values("Date").reset_index(drop=True)

    # Never give the model the date itself or the target.
    # "target" is next week's freight cost.
    excluded_columns = [
        "Date",
        "target",
    ]

    feature_columns = [
        column
        for column in df.columns
        if column not in excluded_columns
    ]

    X = df[feature_columns]
    y = df["target"]

    # ----------------------------------------------
    # Time-based split
    # ----------------------------------------------

    X_train = X.iloc[:-TEST_WEEKS]
    X_test = X.iloc[-TEST_WEEKS:]

    y_train = y.iloc[:-TEST_WEEKS]
    y_test = y.iloc[-TEST_WEEKS:]

    # ----------------------------------------------
    # Random Forest
    # ----------------------------------------------

    model = RandomForestRegressor(
        n_estimators=500,
        max_depth=12,
        min_samples_leaf=2,
        random_state=42,
        n_jobs=-1,
    )

    model.fit(X_train, y_train)

    # ----------------------------------------------
    # Predictions
    # ----------------------------------------------

    predictions = model.predict(X_test)

    # ----------------------------------------------
    # Metrics
    # ----------------------------------------------

    mae = mean_absolute_error(
        y_test,
        predictions,
    )

    rmse = mean_squared_error(
        y_test,
        predictions,
    ) ** 0.5

    # ----------------------------------------------
    # Results
    # ----------------------------------------------

    print("\n" + "=" * 60)
    print(f"{target_name.upper()} — RANDOM FOREST")
    print("=" * 60)

    print(f"\nFeatures:        {len(feature_columns)}")
    print(f"Training rows:   {len(X_train):,}")
    print(f"Testing rows:    {len(X_test):,}")

    print(
        f"\nTest period: "
        f"{df['Date'].iloc[-TEST_WEEKS].date()} → "
        f"{df['Date'].iloc[-1].date()}"
    )

    print("\nPerformance:")
    print(f"MAE:  {mae:.4f}")
    print(f"RMSE: {rmse:.4f}")

    # ----------------------------------------------
    # Compare against naive baseline
    # ----------------------------------------------

    baseline_predictions = df[
        f"{target_name}_lag_1"
    ].iloc[-TEST_WEEKS:]

    baseline_mae = mean_absolute_error(
        y_test,
        baseline_predictions,
    )

    baseline_rmse = mean_squared_error(
        y_test,
        baseline_predictions,
    ) ** 0.5

    print("\nNaive baseline:")
    print(f"MAE:  {baseline_mae:.4f}")
    print(f"RMSE: {baseline_rmse:.4f}")

    print("\nImprovement:")
    print(
        f"MAE improvement: "
        f"{(1 - mae / baseline_mae) * 100:.2f}%"
    )

    print(
        f"RMSE improvement: "
        f"{(1 - rmse / baseline_rmse) * 100:.2f}%"
    )

    return model


# --------------------------------------------------
# Train both models
# --------------------------------------------------

for target_name, file_path in TARGETS.items():

    train_model(
        file_path,
        target_name,
    )


print("\n" + "=" * 60)
print("RANDOM FOREST TRAINING COMPLETE")
print("=" * 60)