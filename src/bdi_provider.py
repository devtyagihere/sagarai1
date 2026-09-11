import os
import requests
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("OILPRICEAPI_KEY")

BASE_URL = "https://api.oilpriceapi.com/v1"

BDI_CODE = "BALTIC_DRY_INDEX"
BCI_CODE = "BALTIC_CAPESIZE_INDEX"


# ============================================================
# GENERIC LATEST INDEX
# ============================================================

def get_index(code):

    if not API_KEY:
        raise ValueError(
            "OILPRICEAPI_KEY not found in .env"
        )

    response = requests.get(
        f"{BASE_URL}/prices/latest",
        params={
            "by_code": code
        },
        headers={
            "Authorization": f"Token {API_KEY}",
            "Content-Type": "application/json"
        },
        timeout=15
    )

    response.raise_for_status()

    payload = response.json()

    if payload.get("status") != "success":
        raise ValueError(
            f"API returned unsuccessful response: {payload}"
        )

    data = payload.get("data")

    if not data:
        raise ValueError(
            "API response does not contain data"
        )

    price = data.get("price")

    if price is None:
        raise ValueError(
            "Price missing from API response"
        )

    return {
        "price": float(price),
        "updated_at": data.get("updated_at"),
        "as_of": data.get("as_of"),
        "source": data.get("source"),
        "unit": data.get("unit")
    }


# ============================================================
# CURRENT BDI
# ============================================================

def get_bdi():

    return get_index(BDI_CODE)["price"]


# ============================================================
# CURRENT BCI
# ============================================================

def get_bci():

    return get_index(BCI_CODE)["price"]


# ============================================================
# CURRENT BDI + BCI
# ============================================================

def get_freight_market_data():

    bdi = get_index(BDI_CODE)
    bci = get_index(BCI_CODE)

    return {

        "bdi":
            bdi["price"],

        "bdi_updated_at":
            bdi["updated_at"],

        "bdi_source":
            bdi["source"],

        "bci":
            bci["price"],

        "bci_updated_at":
            bci["updated_at"],

        "bci_source":
            bci["source"]
    }


# ============================================================
# HISTORICAL BDI
# ============================================================

def get_historical_bdi():

    if not API_KEY:

        raise ValueError(
            "OILPRICEAPI_KEY not found in .env"
        )

    response = requests.get(

        f"{BASE_URL}/prices/past_month",

        params={
            "by_code": BDI_CODE
        },

        headers={
            "Authorization": f"Token {API_KEY}",
            "Content-Type": "application/json"
        },

        timeout=15
    )

    response.raise_for_status()

    payload = response.json()

    if payload.get("status") != "success":

        raise ValueError(
            "BDI historical API returned unsuccessful response"
        )

    data = payload.get("data")

    if not data:

        raise ValueError(
            "Historical BDI data missing"
        )


    # --------------------------------------------------------
    # Handle different API response structures
    # --------------------------------------------------------

    if isinstance(data, list):

        records = data

    elif isinstance(data, dict):

        if isinstance(
            data.get("prices"),
            list
        ):

            records = data["prices"]

        elif isinstance(
            data.get("data"),
            list
        ):

            records = data["data"]

        else:

            records = [data]

    else:

        raise ValueError(
            "Unexpected BDI historical response format"
        )


    # --------------------------------------------------------
    # Convert to dataframe
    # --------------------------------------------------------

    rows = []


    for item in records:

        if not isinstance(item, dict):
            continue

        price = item.get("price")

        timestamp = (

            item.get("as_of")

            or

            item.get("created_at")

            or

            item.get("updated_at")
        )


        if price is None or timestamp is None:
            continue


        rows.append({

            "date":
                pd.to_datetime(
                    timestamp,
                    errors="coerce"
                ),

            "bdi":
                float(price)

        })


    df = pd.DataFrame(rows)


    if df.empty:

        raise ValueError(
            "No valid historical BDI observations found"
        )


    df = df.dropna(
        subset=[
            "date",
            "bdi"
        ]
    )


    # Remove timezone if present

    try:

        df["date"] = (
            df["date"]
            .dt
            .tz_localize(None)
        )

    except TypeError:

        pass


    # Sort + remove duplicate dates

    df = (

        df
        .sort_values("date")
        .drop_duplicates(
            subset=["date"],
            keep="last"
        )
        .reset_index(drop=True)

    )


    return df


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    print("=" * 60)
    print("REAL FREIGHT MARKET DATA TEST")
    print("=" * 60)


    # --------------------------------------------------------
    # BDI + BCI
    # --------------------------------------------------------

    try:

        market = get_freight_market_data()


        print("\nREAL BDI:")
        print(
            market["bdi"]
        )


        print("\nREAL BCI:")
        print(
            market["bci"]
        )


        print("\nBDI Updated:")
        print(
            market["bdi_updated_at"]
        )


        print("\nBCI Updated:")
        print(
            market["bci_updated_at"]
        )


        print("\nBDI Source:")
        print(
            market["bdi_source"]
        )


        print("\nBCI Source:")
        print(
            market["bci_source"]
        )


    except Exception as error:

        print("\nLatest market data failed:")
        print(error)


    # --------------------------------------------------------
    # Historical BDI
    # --------------------------------------------------------

    print("\n" + "=" * 60)
    print("HISTORICAL BDI TEST")
    print("=" * 60)


    try:

        history = get_historical_bdi()


        print("\nHistorical BDI:")
        print(history)


        print(
            "\nRows:",
            len(history)
        )


        print(
            "Start:",
            history["date"].min()
        )


        print(
            "End:",
            history["date"].max()
        )


    except Exception as error:

        print(
            "\nHistorical BDI failed:"
        )

        print(error)