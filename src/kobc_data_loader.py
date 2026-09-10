from pathlib import Path
import pandas as pd
import re


# ============================================================
# CONFIG
# ============================================================

RAW_XLS_FILES = [
    Path("data/kobc_kdci_raw.xls"),
    Path("data/kobc_kdci_raw.xlsx"),
]

OUTPUT_FILE = Path("data/kobc_vessel_rates.csv")


# ============================================================
# HEADER DETECTION
# ============================================================

def normalize_column_name(value):
    """Normalize Excel column names for reliable matching."""

    if pd.isna(value):
        return ""

    text = str(value).strip().lower()

    # Remove spaces, underscores, hyphens and brackets
    text = re.sub(r"[\s_\-\(\)\[\]]+", "", text)

    return text


def find_header_row(raw_df):
    """
    Find the row containing:
    DATE, CAPE, PANAMAX, SUPRAMAX
    """

    required = {
        "date",
        "cape",
        "panamax",
        "supramax",
    }

    # KOBC files normally have title/header information
    # before the actual table header.
    max_rows = min(30, len(raw_df))

    for row_number in range(max_rows):

        row_values = {
            normalize_column_name(value)
            for value in raw_df.iloc[row_number].tolist()
        }

        if required.issubset(row_values):
            return row_number

    return None


# ============================================================
# FIND BEST SHEET
# ============================================================

def find_best_sheet(path):
    """
    Read all sheets without assuming the first row is the header.
    Automatically detects the real KOBC header row.
    """

    print(f"Reading official KOBC file: {path}")

    sheets = pd.read_excel(
        path,
        sheet_name=None,
        header=None
    )

    for sheet_name, raw_df in sheets.items():

        header_row = find_header_row(raw_df)

        if header_row is not None:

            print(f"Found KOBC data sheet: {sheet_name}")
            print(f"Detected header row: {header_row + 1}")

            df = pd.read_excel(
                path,
                sheet_name=sheet_name,
                header=header_row
            )

            return sheet_name, df

    raise ValueError(
        "Could not find a KOBC sheet containing "
        "Date, CAPE, PANAMAX and SUPRAMAX."
    )


# ============================================================
# COLUMN NORMALIZATION
# ============================================================

def find_column(df, possible_names):
    """
    Find a dataframe column using normalized names.
    """

    normalized = {
        normalize_column_name(column): column
        for column in df.columns
    }

    for name in possible_names:

        key = normalize_column_name(name)

        if key in normalized:
            return normalized[key]

    return None


def normalize_kobc_columns(df):
    """
    Convert KOBC column names into our standard schema.
    """

    date_col = find_column(
        df,
        [
            "DATE",
            "Date",
            "일자",
            "날짜",
        ]
    )

    cape_col = find_column(
        df,
        [
            "CAPE",
            "Capesize",
            "Capesize",
            "CAPE SIZE",
        ]
    )

    panamax_col = find_column(
        df,
        [
            "PANAMAX",
            "Panamax",
        ]
    )

    supramax_col = find_column(
        df,
        [
            "SUPRAMAX",
            "Supramax",
        ]
    )

    missing = []

    if date_col is None:
        missing.append("DATE")

    if cape_col is None:
        missing.append("CAPE")

    if panamax_col is None:
        missing.append("PANAMAX")

    if supramax_col is None:
        missing.append("SUPRAMAX")

    if missing:
        raise ValueError(
            "Missing required KOBC columns: "
            + ", ".join(missing)
        )

    result = pd.DataFrame({
        "date": df[date_col],
        "Capesize": df[cape_col],
        "Panamax": df[panamax_col],
        "Supramax": df[supramax_col],
    })

    return result


# ============================================================
# CLEAN DATA
# ============================================================

def clean_data(df):
    """
    Clean official KOBC observations.

    No synthetic values.
    No interpolation.
    """

    df = df.copy()

    # Date
    df["date"] = pd.to_datetime(
        df["date"],
        errors="coerce"
    )

    # Numeric conversion
    for column in [
        "Capesize",
        "Panamax",
        "Supramax",
    ]:

        df[column] = (
            df[column]
            .astype(str)
            .str.replace(",", "", regex=False)
            .str.replace("-", "", regex=False)
            .str.strip()
        )

        df[column] = pd.to_numeric(
            df[column],
            errors="coerce"
        )

    # Remove rows without dates
    df = df.dropna(subset=["date"])

    # Remove rows where all vessel rates are missing
    df = df.dropna(
        subset=[
            "Capesize",
            "Panamax",
            "Supramax",
        ],
        how="all"
    )

    # Remove duplicate dates
    df = (
        df.sort_values("date")
        .drop_duplicates(
            subset=["date"],
            keep="last"
        )
    )

    # Keep only required columns
    df = df[
        [
            "date",
            "Capesize",
            "Panamax",
            "Supramax",
        ]
    ]

    return df


# ============================================================
# LOAD OFFICIAL FILE
# ============================================================

def load_official_file():

    raw_file = None

    for candidate in RAW_XLS_FILES:

        if candidate.exists():
            raw_file = candidate
            break

    if raw_file is None:

        raise FileNotFoundError(
            "KOBC raw file not found.\n"
            "Expected one of:\n"
            "  data/kobc_kdci_raw.xls\n"
            "  data/kobc_kdci_raw.xlsx"
        )

    sheet_name, raw_df = find_best_sheet(raw_file)

    print(f"Using sheet: {sheet_name}")

    df = normalize_kobc_columns(raw_df)

    df = clean_data(df)

    return df


# ============================================================
# SAVE
# ============================================================

def save_output(df):

    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    df.to_csv(
        OUTPUT_FILE,
        index=False
    )

    print()
    print("=" * 70)
    print("KOBC DATA SUCCESSFULLY PROCESSED")
    print("=" * 70)

    print(f"Output file : {OUTPUT_FILE}")
    print(f"Rows        : {len(df)}")

    if len(df) > 0:

        print(
            f"Start date  : "
            f"{df['date'].min().date()}"
        )

        print(
            f"End date    : "
            f"{df['date'].max().date()}"
        )

    print()
    print("Columns:")
    print(
        "  date, Capesize, Panamax, Supramax"
    )

    print()
    print("First 5 observations:")
    print(df.head().to_string(index=False))

    print()
    print("Last 5 observations:")
    print(df.tail().to_string(index=False))

    print()
    print(
        "IMPORTANT: These are official KOBC "
        "market benchmarks in USD/day."
    )

    print(
        "No synthetic values or interpolation "
        "were added."
    )

    print("=" * 70)


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 70)
    print("KOBC OFFICIAL HISTORICAL DATA LOADER")
    print("=" * 70)

    df = load_official_file()

    save_output(df)


if __name__ == "__main__":
    main()