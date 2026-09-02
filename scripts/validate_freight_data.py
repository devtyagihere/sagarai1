from pathlib import Path
import pandas as pd


# --------------------------------------------------
# 1. Locate project and raw dataset
# --------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[1]

DATA_FILE = (
    PROJECT_ROOT
    / "data"
    / "raw"
    / "usda_grain_transportation_cost_indicators.csv"
)


# --------------------------------------------------
# 2. Load raw data
# --------------------------------------------------

df = pd.read_csv(DATA_FILE)

# Parse dates only in memory.
# The raw CSV itself is NOT modified.
df["Date"] = pd.to_datetime(df["Date"], format="%m/%d/%Y")


# --------------------------------------------------
# 3. DATE VALIDATION
# --------------------------------------------------

print("\n" + "=" * 70)
print("DATE VALIDATION")
print("=" * 70)

print(f"\nDate range:")
print(f"  Start: {df['Date'].min().date()}")
print(f"  End:   {df['Date'].max().date()}")

print(f"\nUnique dates: {df['Date'].nunique():,}")
print(f"Total rows:   {len(df):,}")

print(f"\nDates sorted ascending: {df['Date'].is_monotonic_increasing}")
print(f"Dates sorted descending: {df['Date'].is_monotonic_decreasing}")

duplicate_dates = df["Date"].duplicated().sum()
print(f"Duplicate dates: {duplicate_dates:,}")


# --------------------------------------------------
# 4. WEEKLY CONTINUITY
# --------------------------------------------------

print("\n" + "-" * 70)
print("WEEKLY CONTINUITY")
print("-" * 70)

dates_ascending = df["Date"].sort_values()

date_gaps = dates_ascending.diff().dropna()

print(f"Minimum gap: {date_gaps.min().days} days")
print(f"Maximum gap: {date_gaps.max().days} days")

non_weekly = date_gaps[date_gaps != pd.Timedelta(days=7)]

print(f"Non-7-day gaps: {len(non_weekly):,}")

if len(non_weekly) > 0:
    print("\nNon-weekly gaps found:")

    for date, gap in non_weekly.items():
        previous_date = date - gap

        print(
            f"  {previous_date.date()} → "
            f"{date.date()} : {gap.days} days"
        )
else:
    print("\nEvery consecutive observation is exactly 7 days apart.")


# --------------------------------------------------
# 5. FREIGHT TARGET VALIDATION
# --------------------------------------------------

print("\n" + "=" * 70)
print("VESSEL FREIGHT VALIDATION")
print("=" * 70)

vessel_columns = [
    "Gulf_Vessel",
    "Pacific_Vessel",
]

for column in vessel_columns:

    print("\n" + "-" * 70)
    print(column)
    print("-" * 70)

    missing_count = df[column].isna().sum()
    zero_count = (df[column] == 0).sum()

    print(f"Missing values: {missing_count:,}")
    print(f"Zero values:    {zero_count:,}")

    if zero_count > 0:
        print("\nDates with zero values:")

        zero_rows = df.loc[
            df[column] == 0,
            ["Date", column]
        ]

        print(zero_rows.to_string(index=False))


# --------------------------------------------------
# 6. OTHER TRANSPORT MODES — MISSING VALUES
# --------------------------------------------------

print("\n" + "=" * 70)
print("OTHER TRANSPORT MODES — MISSING VALUES")
print("=" * 70)

transport_columns = [
    "Truck",
    "Rail",
    "Barge",
]

for column in transport_columns:

    missing_count = df[column].isna().sum()

    print(
        f"{column:<10} "
        f"missing: {missing_count:,} "
        f"({missing_count / len(df) * 100:.2f}%)"
    )

    if missing_count > 0:
        print("  Missing dates:")

        missing_dates = df.loc[
            df[column].isna(),
            "Date"
        ].dt.strftime("%Y-%m-%d").tolist()

        print("  " + ", ".join(missing_dates))


# --------------------------------------------------
# 7. EXTREME VALUES
# --------------------------------------------------

print("\n" + "=" * 70)
print("EXTREME VESSEL FREIGHT VALUES")
print("=" * 70)

for column in vessel_columns:

    print("\n" + "-" * 70)
    print(f"Highest values — {column}")
    print("-" * 70)

    highest = (
        df[["Date", column]]
        .dropna()
        .sort_values(column, ascending=False)
        .head(10)
    )

    print(highest.to_string(index=False))


# --------------------------------------------------
# 8. FINAL VALIDATION SUMMARY
# --------------------------------------------------

print("\n" + "=" * 70)
print("VALIDATION COMPLETE")
print("=" * 70)

print("\nNo data has been modified or saved.")
print("This script only inspected the raw dataset.")