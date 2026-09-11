import os
import requests
import pandas as pd
from dotenv import load_dotenv

# Load .env
load_dotenv()

EIA_API_KEY = os.getenv("EIA_API_KEY")

if not EIA_API_KEY:
    raise ValueError("EIA_API_KEY not found in .env file")


EIA_WTI_URL = "https://api.eia.gov/v2/seriesid/PET.RWTC.D"


def get_oil_price():
    """
    Fetch latest available WTI crude oil spot price.

    Returns:
        float: Latest WTI price in USD/barrel
    """

    params = {
        "api_key": EIA_API_KEY,
        "frequency": "daily",
        "data[0]": "value",
        "sort[0][column]": "period",
        "sort[0][direction]": "desc",
        "length": 1
    }

    response = requests.get(
        EIA_WTI_URL,
        params=params,
        timeout=15
    )

    response.raise_for_status()

    data = response.json()

    rows = data.get("response", {}).get("data", [])

    if not rows:
        raise Exception("No current WTI price returned by EIA")

    value = rows[0].get("value")

    if value in (None, "", "null"):
        raise Exception("Current WTI price is unavailable")

    return float(value)


def get_historical_oil_prices(start_date=None, end_date=None):
    """
    Fetch historical daily WTI crude oil prices from EIA.

    Args:
        start_date: YYYY-MM-DD
        end_date: YYYY-MM-DD

    Returns:
        pandas.DataFrame with:
        date, oil_price
    """

    params = {
        "api_key": EIA_API_KEY,
        "frequency": "daily",
        "data[0]": "value",
        "sort[0][column]": "period",
        "sort[0][direction]": "asc",
        "length": 5000
    }

    if start_date:
        params["start"] = start_date

    if end_date:
        params["end"] = end_date

    response = requests.get(
        EIA_WTI_URL,
        params=params,
        timeout=30
    )

    response.raise_for_status()

    data = response.json()

    rows = data.get("response", {}).get("data", [])

    if not rows:
        raise Exception("No historical WTI data returned by EIA")

    records = []

    for row in rows:

        value = row.get("value")
        period = row.get("period")

        if value in (None, "", "null"):
            continue

        records.append({
            "date": pd.to_datetime(period),
            "oil_price": float(value)
        })

    df = pd.DataFrame(records)

    if df.empty:
        raise Exception("Historical WTI dataset is empty")

    df = df.sort_values("date").reset_index(drop=True)

    return df


if __name__ == "__main__":

    print("========== CURRENT OIL PRICE ==========")

    current_price = get_oil_price()

    print("WTI:", current_price, "USD/barrel")
    print("Source: U.S. EIA")


    print("\n========== HISTORICAL OIL DATA ==========")

    historical_data = get_historical_oil_prices()

    print("Rows:", len(historical_data))
    print("Start:", historical_data["date"].min().date())
    print("End:", historical_data["date"].max().date())

    print("\nLatest 10 records:")
    print(historical_data.tail(10).to_string(index=False))