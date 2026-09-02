from pathlib import Path

import pandas as pd


# ============================================================
# PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[1]

INPUT_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "freight_fuel_features.csv"
)

GULF_OUTPUT = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "gulf_fuel_ml_dataset.csv"
)

PACIFIC_OUTPUT = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "pacific_fuel_ml_dataset.csv"
)


# ============================================================
# LOAD DATA
# ============================================================

print("=" * 65)
print("BUILDING FREIGHT + FUEL ML DATASETS")
print("=" * 65)

df = pd.read_csv(INPUT_FILE)

df["Date"] = pd.to_datetime(df["Date"])

df = (
    df
    .sort_values("Date")
    .reset_index(drop=True)
)


# ============================================================
# FUEL FEATURES
# ============================================================

fuel_features = [
    column
    for column in df.columns
    if (
        "Diesel" in column
        or "diesel" in column
        or "Gulf_Diesel" in column
    )
]


# ============================================================
# FREIGHT FEATURES
# ============================================================

freight_features = [
    "Truck",
    "Rail",
    "Barge",
    "Gulf_Vessel",
    "Pacific_Vessel",
]


# ============================================================
# CREATE LAG FEATURES FOR FREIGHT
# ============================================================

for column in freight_features:

    for lag in [1, 2, 4, 8, 12]:

        df[f"{column}_lag_{lag}w"] = (
            df[column].shift(lag)
        )


# ============================================================
# CREATE TARGETS
# ============================================================

df["Gulf_target"] = (
    df["Gulf_Vessel"].shift(-1)
)

df["Pacific_target"] = (
    df["Pacific_Vessel"].shift(-1)
)


# ============================================================
# ALL MODEL FEATURES
# ============================================================

lag_features = [
    column
    for column in df.columns
    if "_lag_" in column
]

model_features = (
    freight_features
    + fuel_features
    + lag_features
)


# Remove duplicate column names while preserving order
model_features = list(
    dict.fromkeys(model_features)
)


# ============================================================
# BUILD GULF DATASET
# ============================================================

gulf_columns = (
    ["Date"]
    + model_features
    + ["Gulf_target"]
)

gulf = df[gulf_columns].copy()

gulf = gulf.dropna().reset_index(drop=True)


# ============================================================
# BUILD PACIFIC DATASET
# ============================================================

pacific_columns = (
    ["Date"]
    + model_features
    + ["Pacific_target"]
)

pacific = df[pacific_columns].copy()

pacific = pacific.dropna().reset_index(drop=True)


# ============================================================
# SAVE
# ============================================================

GULF_OUTPUT.parent.mkdir(
    parents=True,
    exist_ok=True
)

gulf.to_csv(
    GULF_OUTPUT,
    index=False
)

pacific.to_csv(
    PACIFIC_OUTPUT,
    index=False
)


# ============================================================
# VALIDATION
# ============================================================

print("\n" + "-" * 65)
print("GULF DATASET")
print("-" * 65)

print(f"Rows:    {len(gulf):,}")
print(f"Columns: {len(gulf.columns):,}")

print(
    f"Date range: "
    f"{gulf['Date'].min().date()} → "
    f"{gulf['Date'].max().date()}"
)

print(
    f"Target: Gulf_target "
    f"→ next week's Gulf vessel cost"
)


print("\n" + "-" * 65)
print("PACIFIC DATASET")
print("-" * 65)

print(f"Rows:    {len(pacific):,}")
print(f"Columns: {len(pacific.columns):,}")

print(
    f"Date range: "
    f"{pacific['Date'].min().date()} → "
    f"{pacific['Date'].max().date()}"
)

print(
    f"Target: Pacific_target "
    f"→ next week's Pacific vessel cost"
)


# ============================================================
# FINAL CHECKS
# ============================================================

print("\n" + "-" * 65)
print("MODEL FEATURES")
print("-" * 65)

print(f"Total features: {len(model_features)}")

print("\nFuel features included:")
for feature in fuel_features:
    print(f"- {feature}")


print("\nMissing values:")

print(
    "Gulf:",
    gulf.isna().sum().sum()
)

print(
    "Pacific:",
    pacific.isna().sum().sum()
)


# ============================================================
# COMPLETE
# ============================================================

print("\n" + "=" * 65)
print("FREIGHT + FUEL ML DATASETS CREATED")
print("=" * 65)

print("\nOutputs:")

print(GULF_OUTPUT)
print(PACIFIC_OUTPUT)

print("\nThese datasets are ready for model training.")