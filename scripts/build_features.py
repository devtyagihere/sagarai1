from pathlib import Path
import pandas as pd
import numpy as np


# --------------------------------------------------
# Paths
# --------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[1]

INPUT_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "usda_freight_cleaned.csv"
)

OUTPUT_DIR = PROJECT_ROOT / "data" / "processed"


# --------------------------------------------------
# Load data
# --------------------------------------------------

df = pd.read_csv(INPUT_FILE)

df["Date"] = pd.to_datetime(df["Date"])

df = df.sort_values("Date").reset_index(drop=True)


# --------------------------------------------------
# Common features
# --------------------------------------------------

df["week_sin"] = np.sin(
    2 * np.pi * df["Week"] / 52
)

df["week_cos"] = np.cos(
    2 * np.pi * df["Week"] / 52
)

df["Truck_current"] = df["Truck"]
df["Barge_current"] = df["Barge"]


# --------------------------------------------------
# Function to build one target dataset
# --------------------------------------------------

def build_target_dataset(target):

    data = df.copy()

    # -----------------------------
    # Lag features
    # -----------------------------

    lag_periods = [1, 2, 4, 8, 13, 26, 52]

    for lag in lag_periods:
        data[f"{target}_lag_{lag}"] = (
            data[target].shift(lag)
        )

    # -----------------------------
    # Rolling features
    # -----------------------------

    history = data[target].shift(1)

    rolling_windows = [4, 8, 13, 26]

    for window in rolling_windows:

        data[f"{target}_rolling_mean_{window}"] = (
            history.rolling(window).mean()
        )

        data[f"{target}_rolling_std_{window}"] = (
            history.rolling(window).std()
        )

    # -----------------------------
    # Momentum features
    # -----------------------------

    data[f"{target}_change_1w"] = (
        data[target].shift(1)
        - data[target].shift(2)
    )

    data[f"{target}_change_4w"] = (
        data[target].shift(1)
        - data[target].shift(5)
    )

    data[f"{target}_pct_change_1w"] = (
        data[target].shift(1).pct_change(1)
    )

    data[f"{target}_pct_change_4w"] = (
        data[target].shift(1).pct_change(4)
    )

    # -----------------------------
    # Next-week target
    # -----------------------------

    data["target"] = data[target].shift(-1)

    # -----------------------------
    # Select useful columns
    # -----------------------------

    feature_columns = [
        "Date",
        "Week",
        "Month",
        "Year",
        "Truck_current",
        "Barge_current",
        "week_sin",
        "week_cos",
    ]

    feature_columns += [
        f"{target}_lag_{lag}"
        for lag in lag_periods
    ]

    feature_columns += [
        f"{target}_rolling_mean_{window}"
        for window in rolling_windows
    ]

    feature_columns += [
        f"{target}_rolling_std_{window}"
        for window in rolling_windows
    ]

    feature_columns += [
        f"{target}_change_1w",
        f"{target}_change_4w",
        f"{target}_pct_change_1w",
        f"{target}_pct_change_4w",
        "target",
    ]

    data = data[feature_columns]

    # -----------------------------
    # Remove only rows that cannot
    # be used by THIS target model
    # -----------------------------

    data = data.dropna().reset_index(drop=True)

    return data


# --------------------------------------------------
# Build Gulf dataset
# --------------------------------------------------

gulf_df = build_target_dataset("Gulf_Vessel")

gulf_output = (
    OUTPUT_DIR / "gulf_ml_dataset.csv"
)

gulf_df.to_csv(
    gulf_output,
    index=False
)


# --------------------------------------------------
# Build Pacific dataset
# --------------------------------------------------

pacific_df = build_target_dataset("Pacific_Vessel")

pacific_output = (
    OUTPUT_DIR / "pacific_ml_dataset.csv"
)

pacific_df.to_csv(
    pacific_output,
    index=False
)


# --------------------------------------------------
# Report
# --------------------------------------------------

print("=" * 60)
print("ML DATASETS CREATED")
print("=" * 60)

print("\nGULF DATASET")
print(f"Rows:    {len(gulf_df):,}")
print(f"Columns: {len(gulf_df.columns)}")
print(f"Output:  {gulf_output}")

print("\nPACIFIC DATASET")
print(f"Rows:    {len(pacific_df):,}")
print(f"Columns: {len(pacific_df.columns)}")
print(f"Output:  {pacific_output}")

print("\nDate ranges:")

print(
    f"Gulf:    "
    f"{gulf_df['Date'].min().date()} → "
    f"{gulf_df['Date'].max().date()}"
)

print(
    f"Pacific: "
    f"{pacific_df['Date'].min().date()} → "
    f"{pacific_df['Date'].max().date()}"
)

print("\nFeature engineering complete.")