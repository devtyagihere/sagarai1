from pathlib import Path

import pandas as pd


# ============================================================
# PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[1]

RAW_FILE = (
    PROJECT_ROOT
    / "data"
    / "raw"
    / "PET_PRI_GND_A_EPD2D_PTE_DPGAL_W.xls"
)

OUTPUT_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "eia_diesel_weekly.csv"
)


# ============================================================
# EIA SOURCE COLUMNS
# ============================================================

US_COLUMN = "US_Diesel_Price"
GULF_COLUMN = "Gulf_Coast_Diesel_Price"


# ============================================================
# READ EIA WORKBOOK
# ============================================================

print("=" * 60)
print("EIA DIESEL DATA PROCESSING")
print("=" * 60)

print(f"\nInput:")
print(RAW_FILE)


# Data 1 = U.S. diesel
data1 = pd.read_excel(
    RAW_FILE,
    sheet_name="Data 1",
    header=None
)

# Data 2 = regional diesel
data2 = pd.read_excel(
    RAW_FILE,
    sheet_name="Data 2",
    header=None
)


# ============================================================
# EXTRACT U.S. SERIES
# ============================================================

us = data1.iloc[3:, [0, 1]].copy()

us.columns = [
    "Date",
    US_COLUMN
]

us["Date"] = pd.to_datetime(
    us["Date"],
    errors="coerce"
)

us[US_COLUMN] = pd.to_numeric(
    us[US_COLUMN],
    errors="coerce"
)

us = us.dropna(
    subset=["Date"]
)


# ============================================================
# EXTRACT GULF COAST SERIES
# ============================================================

# Data 2 structure:
#
# column 0 = Date
# column 6 = Gulf Coast (PADD 3)
#
# This is the R30 series identified from the EIA workbook.

gulf = data2.iloc[3:, [0, 6]].copy()

gulf.columns = [
    "Date",
    GULF_COLUMN
]

gulf["Date"] = pd.to_datetime(
    gulf["Date"],
    errors="coerce"
)

gulf[GULF_COLUMN] = pd.to_numeric(
    gulf[GULF_COLUMN],
    errors="coerce"
)

gulf = gulf.dropna(
    subset=["Date"]
)


# ============================================================
# MERGE THE TWO SERIES
# ============================================================

diesel = pd.merge(
    us,
    gulf,
    on="Date",
    how="outer"
)

diesel = (
    diesel
    .sort_values("Date")
    .drop_duplicates("Date")
    .reset_index(drop=True)
)


# ============================================================
# VALIDATION
# ============================================================

print("\n" + "-" * 60)
print("VALIDATION")
print("-" * 60)

print(f"\nRows: {len(diesel):,}")
print(f"Columns: {len(diesel.columns)}")

print(
    f"\nDate range:"
    f"\nStart: {diesel['Date'].min().date()}"
    f"\nEnd:   {diesel['Date'].max().date()}"
)

print("\nMissing values:")

print(
    diesel.isna().sum()
)

print(
    f"\nDuplicate dates: "
    f"{diesel['Date'].duplicated().sum()}"
)

print("\nFirst 5 rows:")
print(
    diesel.head().to_string(index=False)
)

print("\nLast 5 rows:")
print(
    diesel.tail().to_string(index=False)
)


# ============================================================
# SAVE
# ============================================================

OUTPUT_FILE.parent.mkdir(
    parents=True,
    exist_ok=True
)

diesel.to_csv(
    OUTPUT_FILE,
    index=False
)


# ============================================================
# COMPLETE
# ============================================================

print("\n" + "=" * 60)
print("EIA DIESEL PROCESSING COMPLETE")
print("=" * 60)

print(f"\nOutput:")
print(OUTPUT_FILE)

print("\nRaw EIA workbook was NOT modified.")