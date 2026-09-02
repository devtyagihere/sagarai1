from pathlib import Path

import pandas as pd


# ============================================================
# PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[1]

FREIGHT_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "usda_freight_cleaned.csv"
)

EIA_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "eia_diesel_weekly.csv"
)

OUTPUT_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "freight_with_fuel.csv"
)


# ============================================================
# LOAD DATA
# ============================================================

print("=" * 65)
print("USDA FREIGHT + EIA DIESEL MERGE")
print("=" * 65)

freight = pd.read_csv(FREIGHT_FILE)
fuel = pd.read_csv(EIA_FILE)

freight["Date"] = pd.to_datetime(freight["Date"])
fuel["Date"] = pd.to_datetime(fuel["Date"])


# ============================================================
# SORT
# ============================================================

freight = (
    freight
    .sort_values("Date")
    .reset_index(drop=True)
)

fuel = (
    fuel
    .sort_values("Date")
    .reset_index(drop=True)
)


print("\nUSDA freight:")
print(f"Rows: {len(freight):,}")
print(
    f"Date range: "
    f"{freight['Date'].min().date()} → "
    f"{freight['Date'].max().date()}"
)

print("\nEIA diesel:")
print(f"Rows: {len(fuel):,}")
print(
    f"Date range: "
    f"{fuel['Date'].min().date()} → "
    f"{fuel['Date'].max().date()}"
)


# ============================================================
# PRESERVE EIA SOURCE DATE
# ============================================================

fuel = fuel.rename(
    columns={
        "Date": "EIA_Date"
    }
)


# ============================================================
# AS-OF MERGE
# ============================================================
#
# For each USDA freight observation:
#
# use the latest EIA observation whose date is
# ON or BEFORE the USDA observation date.
#
# This prevents future-data leakage.
# ============================================================

merged = pd.merge_asof(
    freight,
    fuel,
    left_on="Date",
    right_on="EIA_Date",
    direction="backward",
    allow_exact_matches=True,
)


# ============================================================
# CALCULATE DATA AVAILABILITY GAP
# ============================================================

merged["EIA_Lag_Days"] = (
    merged["Date"] - merged["EIA_Date"]
).dt.days


# ============================================================
# VALIDATION
# ============================================================

print("\n" + "-" * 65)
print("MERGE VALIDATION")
print("-" * 65)

print(f"\nRows after merge: {len(merged):,}")

print("\nMissing EIA values:")

print(
    merged[
        [
            "US_Diesel_Price",
            "Gulf_Coast_Diesel_Price",
        ]
    ].isna().sum()
)

print("\nMatched EIA observations:")

print(
    "US Diesel:",
    merged["US_Diesel_Price"].notna().sum()
)

print(
    "Gulf Coast Diesel:",
    merged["Gulf_Coast_Diesel_Price"].notna().sum()
)

print("\nEIA alignment lag (days):")

print(
    merged["EIA_Lag_Days"].describe().to_string()
)


# ============================================================
# CHECK FOR INVALID FUTURE ALIGNMENT
# ============================================================

future_rows = (
    merged["EIA_Lag_Days"] < 0
).sum()

print(
    "\nFuture-data leakage check:"
)

print(
    f"EIA observations after USDA date: {future_rows}"
)


# ============================================================
# SHOW SAMPLE ALIGNMENT
# ============================================================

print("\nSample USDA → EIA alignment:")

print(
    merged[
        [
            "Date",
            "EIA_Date",
            "EIA_Lag_Days",
            "US_Diesel_Price",
            "Gulf_Coast_Diesel_Price",
        ]
    ]
    .head(10)
    .to_string(index=False)
)


# ============================================================
# DUPLICATE CHECK
# ============================================================

print(
    "\nDuplicate USDA dates after merge:",
    merged["Date"].duplicated().sum()
)


# ============================================================
# SAVE
# ============================================================

OUTPUT_FILE.parent.mkdir(
    parents=True,
    exist_ok=True
)

merged.to_csv(
    OUTPUT_FILE,
    index=False
)


# ============================================================
# COMPLETE
# ============================================================

print("\n" + "=" * 65)
print("MERGE COMPLETE")
print("=" * 65)

print(f"\nOutput:")
print(OUTPUT_FILE)

print(f"\nRows saved: {len(merged):,}")

print("\nRaw USDA and EIA files were NOT modified.")