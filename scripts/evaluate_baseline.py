from pathlib import Path
import pandas as pd
from sklearn.metrics import mean_absolute_error, mean_squared_error


# --------------------------------------------------
# Paths
# --------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[1]

PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"

GULF_FILE = PROCESSED_DIR / "gulf_ml_dataset.csv"
PACIFIC_FILE = PROCESSED_DIR / "pacific_ml_dataset.csv"


# --------------------------------------------------
# Time-based split
# --------------------------------------------------

TEST_WEEKS = 104  # last 2 years


def evaluate_baseline(file_path, name):

    df = pd.read_csv(file_path)

    df["Date"] = pd.to_datetime(df["Date"])

    df = df.sort_values("Date").reset_index(drop=True)

    # The target is next week's price.
    # The current week's price is the lag_1 feature.
    lag_1_column = f"{name}_lag_1"

    # Remove rows where baseline cannot be calculated.
    df = df.dropna(
        subset=[lag_1_column, "target"]
    ).reset_index(drop=True)

    # Time-based split.
    train = df.iloc[:-TEST_WEEKS]
    test = df.iloc[-TEST_WEEKS:]

    # Naive forecast:
    # next week = current week
    predictions = test[lag_1_column]

    actual = test["target"]

    mae = mean_absolute_error(
        actual,
        predictions
    )

    rmse = mean_squared_error(
        actual,
        predictions
    ) ** 0.5

    print("\n" + "=" * 60)
    print(f"{name.upper()} BASELINE")
    print("=" * 60)

    print(f"\nTotal usable rows: {len(df):,}")
    print(f"Training rows:     {len(train):,}")
    print(f"Testing rows:      {len(test):,}")

    print(
        f"\nTest period: "
        f"{test['Date'].min().date()} → "
        f"{test['Date'].max().date()}"
    )

    print("\nNaive Forecast:")
    print("Next week's price = current week's price")

    print(f"\nMAE:  {mae:.4f}")
    print(f"RMSE: {rmse:.4f}")


# --------------------------------------------------
# Evaluate both targets
# --------------------------------------------------

evaluate_baseline(
    GULF_FILE,
    "Gulf_Vessel"
)

evaluate_baseline(
    PACIFIC_FILE,
    "Pacific_Vessel"
)


print("\n" + "=" * 60)
print("BASELINE EVALUATION COMPLETE")
print("=" * 60)