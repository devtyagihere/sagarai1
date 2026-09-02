from pathlib import Path
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]

RAW_FILE = (
    PROJECT_ROOT
    / "data"
    / "raw"
    / "usda_grain_transportation_cost_indicators.csv"
)

PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"

OUTPUT_FILE = (
    PROCESSED_DIR
    / "usda_freight_cleaned.csv"
)


# -----------------------------
# Load
# -----------------------------

df = pd.read_csv(RAW_FILE)


# -----------------------------
# Parse and sort date
# -----------------------------

df["Date"] = pd.to_datetime(
    df["Date"],
    format="%m/%d/%Y"
)

df = df.sort_values("Date").reset_index(drop=True)


# -----------------------------
# Numeric columns
# -----------------------------

numeric_columns = [
    "Week",
    "Month",
    "Year",
    "Truck",
    "Rail",
    "Barge",
    "Gulf_Vessel",
    "Pacific_Vessel",
]

for column in numeric_columns:
    df[column] = pd.to_numeric(
        df[column],
        errors="coerce"
    )


# -----------------------------
# Known vessel zero anomaly
# -----------------------------
#
# The USDA dataset contains synchronized
# zero values for both vessel series.
#
# We treat these as missing observations
# rather than real $0 freight rates.
#
# Raw data remains untouched.
# -----------------------------

vessel_columns = [
    "Gulf_Vessel",
    "Pacific_Vessel",
]

for column in vessel_columns:
    df.loc[df[column] == 0, column] = pd.NA


# -----------------------------
# Create output directory
# -----------------------------

PROCESSED_DIR.mkdir(
    parents=True,
    exist_ok=True
)


# -----------------------------
# Save processed dataset
# -----------------------------

df.to_csv(
    OUTPUT_FILE,
    index=False
)


# -----------------------------
# Report
# -----------------------------

print("=" * 60)
print("FREIGHT DATA CLEANING COMPLETE")
print("=" * 60)

print(f"\nInput:")
print(RAW_FILE)

print(f"\nOutput:")
print(OUTPUT_FILE)

print(f"\nRows: {len(df):,}")
print(f"Columns: {len(df.columns)}")

print("\nMissing values after cleaning:")

print(df.isna().sum())

print("\nProcessed date range:")
print(f"Start: {df['Date'].min().date()}")
print(f"End:   {df['Date'].max().date()}")

print("\nRaw dataset was NOT modified.")