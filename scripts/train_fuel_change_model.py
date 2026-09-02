from pathlib import Path

import pandas as pd
import joblib
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error


# ============================================================
# PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[1]

GULF_FILE = PROJECT_ROOT / "data" / "processed" / "gulf_fuel_ml_dataset.csv"
PACIFIC_FILE = PROJECT_ROOT / "data" / "processed" / "pacific_fuel_ml_dataset.csv"

MODEL_DIR = PROJECT_ROOT / "models"
MODEL_DIR.mkdir(parents=True, exist_ok=True)


# ============================================================
# SETTINGS
# ============================================================

TEST_SIZE = 104
RANDOM_STATE = 42


# ============================================================
# TRAIN + EVALUATE
# ============================================================

def train_and_evaluate(file_path, vessel_column, target_column, name):

    df = pd.read_csv(file_path)

    df["Date"] = pd.to_datetime(df["Date"])

    df = (
        df
        .sort_values("Date")
        .reset_index(drop=True)
    )

    # --------------------------------------------------------
    # NEXT WEEK'S PRICE CHANGE
    # --------------------------------------------------------

    df["price_change_target"] = (
        df[target_column] - df[vessel_column]
    )

    # --------------------------------------------------------
    # FEATURES
    # --------------------------------------------------------

    exclude_columns = [
        "Date",
        "Gulf_target",
        "Pacific_target",
        "price_change_target",
    ]

    feature_columns = [
        column
        for column in df.columns
        if column not in exclude_columns
    ]

    # --------------------------------------------------------
    # REMOVE MISSING VALUES
    # --------------------------------------------------------

    model_df = df.dropna(
        subset=feature_columns + ["price_change_target"]
    ).reset_index(drop=True)

    X = model_df[feature_columns]
    y = model_df["price_change_target"]

    # --------------------------------------------------------
    # TIME-BASED SPLIT
    # --------------------------------------------------------

    train_size = len(model_df) - TEST_SIZE

    X_train = X.iloc[:train_size]
    X_test = X.iloc[train_size:]

    y_train = y.iloc[:train_size]
    y_test = y.iloc[train_size:]

    # --------------------------------------------------------
    # TRAIN MODEL
    # --------------------------------------------------------

    model = RandomForestRegressor(
        n_estimators=300,
        max_depth=8,
        min_samples_leaf=3,
        random_state=RANDOM_STATE,
        n_jobs=-1,
    )

    model.fit(X_train, y_train)

    # --------------------------------------------------------
    # PREDICT CHANGE
    # --------------------------------------------------------

    predicted_change = model.predict(X_test)

    # --------------------------------------------------------
    # RECONSTRUCT PRICE
    # --------------------------------------------------------

    current_prices = (
        model_df[vessel_column]
        .iloc[train_size:]
        .values
    )

    actual_next_prices = (
        model_df[target_column]
        .iloc[train_size:]
        .values
    )

    predicted_prices = (
        current_prices + predicted_change
    )

    # --------------------------------------------------------
    # EVALUATE
    # --------------------------------------------------------

    mae = mean_absolute_error(
        actual_next_prices,
        predicted_prices
    )

    rmse = mean_squared_error(
        actual_next_prices,
        predicted_prices
    ) ** 0.5

    # --------------------------------------------------------
    # NAIVE BASELINE
    # --------------------------------------------------------

    naive_predictions = current_prices

    naive_mae = mean_absolute_error(
        actual_next_prices,
        naive_predictions
    )

    naive_rmse = mean_squared_error(
        actual_next_prices,
        naive_predictions
    ) ** 0.5

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
    # OUTPUT
    # --------------------------------------------------------

    print("\n" + "=" * 65)
    print(f"{name} — FUEL + FREIGHT CHANGE MODEL")
    print("=" * 65)

    print(f"\nFeatures:        {len(feature_columns)}")
    print(f"Training rows:   {len(X_train):,}")
    print(f"Testing rows:    {len(X_test):,}")

    print(
        f"\nTest period: "
        f"{model_df['Date'].iloc[train_size].date()} → "
        f"{model_df['Date'].iloc[-1].date()}"
    )

    print("\nModel predicts:")
    print("Next week's freight price CHANGE")

    print("\nReconstructed price forecast:")
    print(f"MAE:  {mae:.4f}")
    print(f"RMSE: {rmse:.4f}")

    print("\nNaive baseline:")
    print(f"MAE:  {naive_mae:.4f}")
    print(f"RMSE: {naive_rmse:.4f}")

    print("\nImprovement:")
    print(f"MAE improvement:  {mae_improvement:+.2f}%")
    print(f"RMSE improvement: {rmse_improvement:+.2f}%")

    # --------------------------------------------------------
    # FEATURE IMPORTANCE
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

    # --------------------------------------------------------
    # SAVE MODEL
    # --------------------------------------------------------

    model_file = MODEL_DIR / f"{name.lower()}_fuel_change_model.joblib"

    joblib.dump(
        {
            "model": model,
            "features": feature_columns,
            "vessel_column": vessel_column,
            "target_column": target_column,
        },
        model_file
    )

    print(f"\nModel saved:")
    print(model_file)

    return model


# ============================================================
# GULF
# ============================================================

print("=" * 65)
print("FREIGHT PRICE-CHANGE FORECASTING")
print("=" * 65)

gulf_model = train_and_evaluate(
    GULF_FILE,
    "Gulf_Vessel",
    "Gulf_target",
    "gulf",
)


# ============================================================
# PACIFIC
# ============================================================

pacific_model = train_and_evaluate(
    PACIFIC_FILE,
    "Pacific_Vessel",
    "Pacific_target",
    "pacific",
)


# ============================================================
# COMPLETE
# ============================================================

print("\n" + "=" * 65)
print("PRICE-CHANGE MODELING COMPLETE")
print("=" * 65)

print("\nSaved models:")
print(MODEL_DIR / "gulf_fuel_change_model.joblib")
print(MODEL_DIR / "pacific_fuel_change_model.joblib")