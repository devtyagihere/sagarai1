import io
import requests
import pandas as pd
import numpy as np

from sklearn.ensemble import RandomForestRegressor


WORLD_BANK_URL = (
    "https://thedocs.worldbank.org/en/doc/"
    "74e8be41ceb20fa0da750cda2f6b9e4e-0050012026/related/"
    "CMO-Historical-Data-Monthly.xlsx"
)


# ============================================================
# CARGO → WORLD BANK COMMODITY MAPPING
# ============================================================

COMMODITY_MAPPING = {

    "Iron Ore": {
        "world_bank_name": "Iron ore, cfr spot",
        "display_name": "Iron Ore",
        "unit": "USD/dmtu"
    },

    "Coal": {
        "world_bank_name": "Coal, Australian",
        "display_name": "Australian Coal",
        "unit": "USD/mt"
    },

    # IMPORTANT:
    # World Bank Pink Sheet does not directly provide a steel
    # series in the current mapping we are using.
    # Therefore Iron Ore is explicitly used as a proxy.
    "Steel": {
        "world_bank_name": "Iron ore, cfr spot",
        "display_name": "Steel (Iron Ore Proxy)",
        "unit": "USD/dmtu"
    }
}


# ============================================================
# DOWNLOAD WORLD BANK DATA
# ============================================================

def _download_world_bank_data():

    response = requests.get(
        WORLD_BANK_URL,
        timeout=30
    )

    response.raise_for_status()

    excel_data = io.BytesIO(
        response.content
    )

    raw = pd.read_excel(
        excel_data,
        sheet_name="Monthly Prices",
        header=None
    )

    return raw


# ============================================================
# EXTRACT COMMODITY HISTORY
# ============================================================

def _get_commodity_history(cargo_type):

    if cargo_type not in COMMODITY_MAPPING:

        raise ValueError(
            f"Unsupported cargo type: {cargo_type}. "
            f"Supported types: "
            f"{list(COMMODITY_MAPPING.keys())}"
        )

    mapping = COMMODITY_MAPPING[cargo_type]

    world_bank_name = (
        mapping["world_bank_name"]
    )

    raw = _download_world_bank_data()

    # --------------------------------------------------------
    # Find header row
    # --------------------------------------------------------

    header_row = None

    for row_index in range(len(raw)):

        row_values = (
            raw.iloc[row_index]
            .astype(str)
            .str.lower()
        )

        if row_values.str.contains(
            world_bank_name.lower(),
            regex=False
        ).any():

            header_row = row_index
            break

    if header_row is None:

        raise Exception(
            f"Commodity column not found: "
            f"{world_bank_name}"
        )

    # --------------------------------------------------------
    # Find commodity column
    # --------------------------------------------------------

    commodity_column = None

    for column_index in range(
        len(raw.columns)
    ):

        value = str(
            raw.iloc[
                header_row,
                column_index
            ]
        ).lower()

        if world_bank_name.lower() in value:

            commodity_column = (
                column_index
            )

            break

    if commodity_column is None:

        raise Exception(
            f"Commodity column not found: "
            f"{world_bank_name}"
        )

    # --------------------------------------------------------
    # Extract monthly observations
    # --------------------------------------------------------

    data = raw.iloc[
        header_row + 1:
    ].copy()

    data = data[
        data.iloc[:, 0]
        .astype(str)
        .str.match(
            r"^\d{4}M\d{2}$"
        )
    ]

    if data.empty:

        raise Exception(
            "No monthly commodity "
            "price data found"
        )

    # --------------------------------------------------------
    # Clean dataframe
    # --------------------------------------------------------

    result = pd.DataFrame({

        "period":
            data.iloc[:, 0],

        "commodity_price":
            pd.to_numeric(
                data.iloc[
                    :,
                    commodity_column
                ],
                errors="coerce"
            )
    })

    result = result.dropna(
        subset=[
            "commodity_price"
        ]
    )

    if result.empty:

        raise Exception(
            f"No valid prices available "
            f"for {cargo_type}"
        )

    # --------------------------------------------------------
    # Convert YYYY-MM
    # --------------------------------------------------------

    result["date"] = pd.to_datetime(
        result["period"].str.replace(
            "M",
            "-",
            regex=False
        ) + "-01",
        errors="coerce"
    )

    result = result.dropna(
        subset=["date"]
    )

    result = (
        result
        .sort_values("date")
        .reset_index(drop=True)
    )

    return result


# ============================================================
# CURRENT COMMODITY PRICE
# ============================================================

def get_commodity_price(cargo_type):

    mapping = COMMODITY_MAPPING[
        cargo_type
    ]

    result = _get_commodity_history(
        cargo_type
    )

    latest = result.iloc[-1]

    return {

        "cargo_type":
            cargo_type,

        "commodity":
            mapping["display_name"],

        "period":
            latest["period"],

        "price":
            float(
                latest["commodity_price"]
            ),

        "unit":
            mapping["unit"],

        "source":
            "World Bank Pink Sheet"
    }


# ============================================================
# CREATE ML FEATURES
# ============================================================

def _create_features(df):

    data = df.copy()

    data["year"] = (
        data["date"].dt.year
    )

    data["month"] = (
        data["date"].dt.month
    )

    # --------------------------------------------------------
    # Lag features
    # --------------------------------------------------------

    for lag in [
        1,
        2,
        3,
        6,
        12
    ]:

        data[
            f"lag_{lag}"
        ] = data[
            "commodity_price"
        ].shift(lag)

    # --------------------------------------------------------
    # Rolling features
    # --------------------------------------------------------

    shifted = data[
        "commodity_price"
    ].shift(1)

    for window in [
        3,
        6,
        12
    ]:

        data[
            f"rolling_mean_{window}"
        ] = shifted.rolling(
            window
        ).mean()

        data[
            f"rolling_std_{window}"
        ] = shifted.rolling(
            window
        ).std()

    # --------------------------------------------------------
    # Momentum
    # --------------------------------------------------------

    data["change_1"] = (
        data["commodity_price"]
        .shift(1)
        -
        data["commodity_price"]
        .shift(2)
    )

    data["change_3"] = (
        data["commodity_price"]
        .shift(1)
        -
        data["commodity_price"]
        .shift(4)
    )

    data["return_1"] = (
        data["commodity_price"]
        .shift(1)
        /
        data["commodity_price"]
        .shift(2)
        - 1
    )

    data["return_3"] = (
        data["commodity_price"]
        .shift(1)
        /
        data["commodity_price"]
        .shift(4)
        - 1
    )

    data = data.replace(
        [np.inf, -np.inf],
        np.nan
    )

    return data


# ============================================================
# TRAIN COMMODITY ML MODEL
# ============================================================

def _train_model(history):

    data = _create_features(
        history
    )

    feature_columns = [

        "year",
        "month",

        "lag_1",
        "lag_2",
        "lag_3",
        "lag_6",
        "lag_12",

        "rolling_mean_3",
        "rolling_mean_6",
        "rolling_mean_12",

        "rolling_std_3",
        "rolling_std_6",
        "rolling_std_12",

        "change_1",
        "change_3",

        "return_1",
        "return_3"
    ]

    data = data.dropna(
        subset=feature_columns + [
            "commodity_price"
        ]
    )

    if len(data) < 30:

        raise Exception(
            "Not enough historical "
            "commodity observations "
            "for ML forecasting."
        )

    X = data[
        feature_columns
    ]

    y = data[
        "commodity_price"
    ]

    model = RandomForestRegressor(

        n_estimators=300,

        max_depth=10,

        min_samples_leaf=2,

        random_state=42,

        n_jobs=-1
    )

    model.fit(
        X,
        y
    )

    return (
        model,
        feature_columns
    )


# ============================================================
# NEXT MONTH ML FORECAST
# ============================================================

def _forecast_next_month(history):

    model, feature_columns = (
        _train_model(history)
    )

    data = history.copy()

    # Add one future month
    future_date = (
        data["date"].iloc[-1]
        +
        pd.DateOffset(months=1)
    )

    # Build temporary dataframe
    temp = pd.concat(
        [
            data,
            pd.DataFrame({
                "date": [
                    future_date
                ],
                "period": [
                    future_date.strftime(
                        "%YM%m"
                    )
                ],
                "commodity_price": [
                    np.nan
                ]
            })
        ],
        ignore_index=True
    )

    temp = _create_features(
        temp
    )

    future_row = temp.iloc[
        [-1]
    ]

    X_future = future_row[
        feature_columns
    ]

    prediction = model.predict(
        X_future
    )[0]

    return float(
        prediction
    )


# ============================================================
# COMMODITY FORECAST API
# ============================================================

def get_commodity_forecast(
    cargo_type
):

    mapping = COMMODITY_MAPPING[
        cargo_type
    ]

    history = _get_commodity_history(
        cargo_type
    )

    current_price = float(
        history[
            "commodity_price"
        ].iloc[-1]
    )

    latest_period = (
        history[
            "period"
        ].iloc[-1]
    )

    # --------------------------------------------------------
    # ML forecast for next monthly observation
    # --------------------------------------------------------

    next_month_prediction = (
        _forecast_next_month(
            history
        )
    )

    # --------------------------------------------------------
    # Convert monthly forecast into
    # requested freight horizons.
    #
    # World Bank Pink Sheet is monthly,
    # therefore we should NOT pretend
    # it provides daily forecasts.
    #
    # We interpolate toward the next
    # monthly ML prediction.
    # --------------------------------------------------------

    price_change = (
        next_month_prediction
        -
        current_price
    )

    forecast_7 = (
        current_price
        +
        price_change * 0.25
    )

    forecast_15 = (
        current_price
        +
        price_change * 0.50
    )

    forecast_30 = (
        next_month_prediction
    )

    return {

        "cargo_type":
            cargo_type,

        "commodity":
            mapping["display_name"],

        "current_price":
            current_price,

        "period":
            latest_period,

        "unit":
            mapping["unit"],

        "source":
            "World Bank Pink Sheet + "
            "Random Forest ML",

        "demand":
            None,

        "forecast": {

            "7_day":
                float(forecast_7),

            "15_day":
                float(forecast_15),

            "30_day":
                float(forecast_30)
        },

        "forecast_basis":
            "Monthly World Bank historical "
            "commodity prices with Random "
            "Forest next-month forecasting."
    }


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    print(
        "=" * 60
    )

    print(
        "COMMODITY PROVIDER TEST"
    )

    print(
        "=" * 60
    )

    for cargo in [
        "Iron Ore",
        "Coal",
        "Steel"
    ]:

        print(
            f"\n{'=' * 20} "
            f"{cargo} {'=' * 20}"
        )

        try:

            current = (
                get_commodity_price(
                    cargo
                )
            )

            print(
                "Current price:",
                current["price"],
                current["unit"]
            )

            print(
                "Period:",
                current["period"]
            )

            forecast = (
                get_commodity_forecast(
                    cargo
                )
            )

            print(
                "7-day forecast:",
                forecast[
                    "forecast"
                ]["7_day"]
            )

            print(
                "15-day forecast:",
                forecast[
                    "forecast"
                ]["15_day"]
            )

            print(
                "30-day forecast:",
                forecast[
                    "forecast"
                ]["30_day"]
            )

            print(
                "Source:",
                forecast["source"]
            )

        except Exception as error:

            print(
                "ERROR:",
                error
            )