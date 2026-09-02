from pathlib import Path
import pandas as pd


# --------------------------------------------------
# 1. Locate the project and raw dataset
# --------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[1]

DATA_FILE = (
    PROJECT_ROOT
    / "data"
    / "raw"
    / "usda_grain_transportation_cost_indicators.csv"
)


# --------------------------------------------------
# 2. Load the raw dataset
# --------------------------------------------------

df = pd.read_csv(DATA_FILE)


# --------------------------------------------------
# 3. Basic dataset information
# --------------------------------------------------

print("\n" + "=" * 60)
print("USDA FREIGHT DATASET — BASIC PROFILE")
print("=" * 60)

print(f"\nFile: {DATA_FILE}")
print(f"Rows: {df.shape[0]:,}")
print(f"Columns: {df.shape[1]}")


# --------------------------------------------------
# 4. Column names
# --------------------------------------------------

print("\n" + "-" * 60)
print("COLUMNS")
print("-" * 60)

for column in df.columns:
    print(f"- {column}")


# --------------------------------------------------
# 5. Data types
# --------------------------------------------------

print("\n" + "-" * 60)
print("DATA TYPES")
print("-" * 60)

print(df.dtypes)


# --------------------------------------------------
# 6. Missing values
# --------------------------------------------------

print("\n" + "-" * 60)
print("MISSING VALUES")
print("-" * 60)

missing = df.isna().sum()

print(missing)


# --------------------------------------------------
# 7. Duplicate rows
# --------------------------------------------------

print("\n" + "-" * 60)
print("DUPLICATES")
print("-" * 60)

duplicate_rows = df.duplicated().sum()

print(f"Duplicate rows: {duplicate_rows:,}")


# --------------------------------------------------
# 8. First and last records
# --------------------------------------------------

print("\n" + "-" * 60)
print("FIRST 5 ROWS")
print("-" * 60)

print(df.head())


print("\n" + "-" * 60)
print("LAST 5 ROWS")
print("-" * 60)

print(df.tail())


# --------------------------------------------------
# 9. Numerical summary
# --------------------------------------------------

print("\n" + "-" * 60)
print("NUMERICAL SUMMARY")
print("-" * 60)

print(df.describe())


print("\n" + "=" * 60)
print("PROFILE COMPLETE")
print("=" * 60)