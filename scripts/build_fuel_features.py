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
    / "freight_with_fuel.csv"
)

OUTPUT_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "freight_fuel_features.csv"
)


# ============================================================
# LOAD DATA
# ============================================================

print("=" * 65)
print("FREIGHT + FUEL FEATURE ENGINEERING")
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

fuel_columns = [
    "US_Diesel_Price",
    "Gulf_Coast_Diesel_Price",
]

for column in fuel_columns:

    # --------------------------------------------------------
    # Price changes
    # --------------------------------------------------------

    df[f"{column}_change_1w"] = (
        df[column].diff(1)
    )

    df[f"{column}_change_2w"] = (
        df[column].diff(2)
    )

    df[f"{column}_change_4w"] = (
        df[column].diff(4)
    )

    # --------------------------------------------------------
    # Percentage changes
    # --------------------------------------------------------

    df[f"{column}_pct_change_1w"] = (
        df[column].pct_change(1)
    )

    df[f"{column}_pct_change_4w"] = (
        df[column].pct_change(4)
    )

    # --------------------------------------------------------
    # Rolling averages
    # --------------------------------------------------------

    df[f"{column}_ma_4w"] = (
        df[column]
        .rolling(window=4)
        .mean()
    )

    df[f"{column}_ma_8w"] = (
        df[column]
        .rolling(window=8)
        .mean()
    )

    df[f"{column}_ma_12w"] = (
        df[column]
        .rolling(window=12)
        .mean()
    )

    # --------------------------------------------------------
    # Rolling volatility
    # --------------------------------------------------------

    df[f"{column}_volatility_4w"] = (
        df[column]
        .rolling(window=4)
        .std()
    )

    df[f"{column}_volatility_8w"] = (
        df[column]
        .rolling(window=8)
        .std()
    )


# ============================================================
# REGIONAL FUEL SPREAD
# ============================================================
#
# Difference between Gulf Coast diesel and U.S. diesel.
#
# This tells the model whether Gulf fuel prices are behaving
# differently from the national fuel market.
# ============================================================

df["Gulf_Diesel_Spread"] = (
    df["Gulf_Coast_Diesel_Price"]
    - df["US_Diesel_Price"]
)


df["Gulf_Diesel_Spread_change_1w"] = (
    df["Gulf_Diesel_Spread"].diff(1)
)


df["Gulf_Diesel_Spread_change_4w"] = (
    df["Gulf_Diesel_Spread"].diff(4)
)


# ============================================================
# REMOVE EARLY ROWS CREATED BY ROLLING FEATURES
# ============================================================

feature_columns = [
    column
    for column in df.columns
    if column not in [
        "Date",
    ]
]

required_fuel_features = [
    "US_Diesel_Price",
    "Gulf_Coast_Diesel_Price",
    "US_Diesel_Price_ma_12w",
    "Gulf_Coast_Diesel_Price_ma_12w",
]


df = df.dropna(
    subset=required_fuel_features
).reset_index(drop=True)


# ============================================================
# VALIDATION
# ============================================================

print("\n" + "-" * 65)
print("FEATURE VALIDATION")
print("-" * 65)

print(f"\nRows: {len(df):,}")
print(f"Columns: {len(df.columns)}")

print(
    f"\nDate range:"
    f"\nStart: {df['Date'].min().date()}"
    f"\nEnd:   {df['Date'].max().date()}"
)

print("\nMissing values in fuel features:")

fuel_feature_columns = [
    column
    for column in df.columns
    if (
        "Diesel" in column
        or "diesel" in column
    )
]

print(
    df[fuel_feature_columns]
    .isna()
    .sum()
    .to_string()
)


# ============================================================
# SAMPLE
# ============================================================

print("\nSample fuel features:")

sample_columns = [
    "Date",
    "US_Diesel_Price",
    "Gulf_Coast_Diesel_Price",
    "US_Diesel_Price_change_1w",
    "US_Diesel_Price_pct_change_1w",
    "US_Diesel_Price_ma_4w",
    "US_Diesel_Price_ma_12w",
    "Gulf_Coast_Diesel_Price_change_1w",
    "Gulf_Coast_Diesel_Price_pct_change_1w",
    "Gulf_Diesel_Spread",
]

print(
    df[sample_columns]
    .head(10)
    .to_string(index=False)
)


# ============================================================
# SAVE
# ============================================================

OUTPUT_FILE.parent.mkdir(
    parents=True,
    exist_ok=True
)

df.to_csv(
    OUTPUT_FILE,
    index=False
)


# ============================================================
# COMPLETE
# ============================================================

print("\n" + "=" * 65)
print("FUEL FEATURE ENGINEERING COMPLETE")
print("=" * 65)

print(f"\nOutput:")
print(OUTPUT_FILE)

print(f"\nRows saved: {len(df):,}")
print(f"Columns saved: {len(df.columns):,}")

print("\nRaw data was NOT modified.")