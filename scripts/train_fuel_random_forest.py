from pathlib import Path

import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error


# ============================================================
# PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[1]

GULF_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "gulf_fuel_ml_dataset.csv"
)

PACIFIC_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "pacific_fuel_ml_dataset.csv"
)


# ============================================================
# SETTINGS
# ============================================================

TEST_SIZE = 104

RANDOM_STATE = 42


# ============================================================
# FUNCTION
# ============================================================

def train_and_evaluate(file_path, target_column, name):

    df = pd.read_csv(file_path)

    df["Date"] = pd.to_datetime(df["Date"])

    df = (
        df
        .sort_values("Date")
        .reset_index(drop=True)
    )

    # --------------------------------------------------------
    # Features
    # --------------------------------------------------------

    exclude_columns = [
        "Date",
        "Gulf_target",
        "Pacific_target",
    ]

    feature_columns = [
        column
        for column in df.columns
        if column not in exclude_columns
    ]

    X = df[feature_columns]
    y = df[target_column]

    # --------------------------------------------------------
    # Time-based split
    # --------------------------------------------------------

    train_size = len(df) - TEST_SIZE

    X_train = X.iloc[:train_size]
    X_test = X.iloc[train_size:]

    y_train = y.iloc[:train_size]
    y_test = y.iloc[train_size:]

    # --------------------------------------------------------
    # Model
    # --------------------------------------------------------

    model = RandomForestRegressor(
        n_estimators=300,
        max_depth=8,
        min_samples_leaf=3,
        random_state=RANDOM_STATE,
        n_jobs=-1,
    )

    model.fit(
        X_train,
        y_train
    )

    # --------------------------------------------------------
    # Predictions
    # --------------------------------------------------------

    predictions = model.predict(X_test)

    # --------------------------------------------------------
    # Metrics
    # --------------------------------------------------------

    mae = mean_absolute_error(
        y_test,
        predictions
    )

    rmse = mean_squared_error(
        y_test,
        predictions
    ) ** 0.5

    # --------------------------------------------------------
    # Naive baseline
    # --------------------------------------------------------
    #
    # Target = next week's price.
    # Therefore current week's price is the naive forecast.
    # --------------------------------------------------------

    naive_predictions = (
        df["Gulf_Vessel"]
        if target_column == "Gulf_target"
        else df["Pacific_Vessel"]
    ).iloc[train_size:].values

    naive_mae = mean_absolute_error(
        y_test,
        naive_predictions
    )

    naive_rmse = mean_squared_error(
        y_test,
        naive_predictions
    ) ** 0.5

    # --------------------------------------------------------
    # Improvement
    # --------------------------------------------------------

    mae_improvement = (
        (naive_mae - mae)
        / naive_mae
        * 100
    )

    rmse_improvement = (
        (naive_rmse - rmse)
        / naive_rmse
        * 100
    )

    # --------------------------------------------------------
    # Output
    # --------------------------------------------------------

    print("\n" + "=" * 65)
    print(f"{name} — FREIGHT + FUEL RANDOM FOREST")
    print("=" * 65)

    print(f"\nFeatures:        {len(feature_columns)}")
    print(f"Training rows:   {len(X_train):,}")
    print(f"Testing rows:    {len(X_test):,}")

    print(
        f"\nTest period: "
        f"{df['Date'].iloc[train_size].date()} → "
        f"{df['Date'].iloc[-1].date()}"
    )

    print("\nRandom Forest + Fuel:")

    print(f"MAE:  {mae:.4f}")
    print(f"RMSE: {rmse:.4f}")

    print("\nNaive baseline:")

    print(f"MAE:  {naive_mae:.4f}")
    print(f"RMSE: {naive_rmse:.4f}")

    print("\nImprovement:")

    print(
        f"MAE improvement:  {mae_improvement:+.2f}%"
    )

    print(
        f"RMSE improvement: {rmse_improvement:+.2f}%"
    )

    # --------------------------------------------------------
    # Feature importance
    # --------------------------------------------------------

    importance = pd.DataFrame(
        {
            "Feature": feature_columns,
            "Importance": model.feature_importances_,
        }
    ).sort_values(
        "Importance",
        ascending=False
    )

    print("\nTop 10 features:")

    print(
        importance
        .head(10)
        .to_string(index=False)
    )

    return model


# ============================================================
# TRAIN BOTH MODELS
# ============================================================

print("=" * 65)
print("FREIGHT + FUEL RANDOM FOREST TRAINING")
print("=" * 65)

gulf_model = train_and_evaluate(
    GULF_FILE,
    "Gulf_target",
    "GULF_VESSEL"
)

pacific_model = train_and_evaluate(
    PACIFIC_FILE,
    "Pacific_target",
    "PACIFIC_VESSEL"
)


# ============================================================
# COMPLETE
# ============================================================

print("\n" + "=" * 65)
print("FREIGHT + FUEL TRAINING COMPLETE")
print("=" * 65)