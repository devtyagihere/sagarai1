import requests
import pandas as pd
import joblib

from src.marine_risk import calculate_marine_risk
from src.environmental_risk import calculate_environmental_risk


# --------------------------------------------------
# PORT COORDINATES
# --------------------------------------------------

PORT_COORDINATES = {
    "Dhamra": (20.8234, 86.9604),
    "Paradip": (20.2667, 86.6167),
    "Visakhapatnam": (17.6868, 83.2185),
    "Vizag": (17.6868, 83.2185),
    "Gangavaram": (17.6319, 83.2190),
    "Gopalpur": (19.2667, 84.9167),
    "Haldia": (22.0257, 88.0583),
    "Sagar-Sandheads": (21.0, 88.1)
}


# --------------------------------------------------
# GET LOCATION COORDINATES
# --------------------------------------------------

def get_coordinates(location):

    if location in PORT_COORDINATES:
        return PORT_COORDINATES[location]

    url = "https://geocoding-api.open-meteo.com/v1/search"

    params = {
        "name": location,
        "count": 1,
        "language": "en",
        "format": "json"
    }

    response = requests.get(
        url,
        params=params,
        timeout=15
    )

    response.raise_for_status()

    data = response.json()

    if "results" not in data or not data["results"]:
        return None

    result = data["results"][0]

    return result["latitude"], result["longitude"]


# --------------------------------------------------
# NORMAL WEATHER FORECAST
# 1-16 DAYS
# --------------------------------------------------

def get_normal_weather(latitude, longitude):

    weather_url = "https://api.open-meteo.com/v1/forecast"

    weather_params = {
        "latitude": latitude,
        "longitude": longitude,
        "daily": (
            "temperature_2m_max,"
            "precipitation_sum,"
            "wind_speed_10m_max,"
            "weather_code"
        ),
        "forecast_days": 16,
        "timezone": "auto"
    }

    response = requests.get(
        weather_url,
        params=weather_params,
        timeout=15
    )

    response.raise_for_status()

    data = response.json()

    daily = data["daily"]

    return pd.DataFrame({
        "date": pd.to_datetime(daily["time"]),
        "temperature": daily["temperature_2m_max"],
        "precipitation": daily["precipitation_sum"],
        "wind_speed": daily["wind_speed_10m_max"],
        "weather_code": daily["weather_code"]
    })


# --------------------------------------------------
# ENSEMBLE MEAN WEATHER FORECAST
# 17-30 DAYS
# --------------------------------------------------

def get_ensemble_weather(latitude, longitude):

    ensemble_url = (
        "https://ensemble-api.open-meteo.com/v1/ensemble"
    )

    ensemble_params = {
        "latitude": latitude,
        "longitude": longitude,
        "models": "gfs_seamless",
        "hourly": (
            "temperature_2m,"
            "precipitation,"
            "wind_speed_10m"
        ),
        "forecast_days": 35,
        "timezone": "auto"
    }

    response = requests.get(
        ensemble_url,
        params=ensemble_params,
        timeout=20
    )

    response.raise_for_status()

    data = response.json()

    hourly = data["hourly"]

    hourly_df = pd.DataFrame({
        "datetime": pd.to_datetime(hourly["time"]),
        "temperature": hourly["temperature_2m"],
        "precipitation": hourly["precipitation"],
        "wind_speed": hourly["wind_speed_10m"]
    })

    hourly_df["date"] = (
        hourly_df["datetime"].dt.normalize()
    )

    daily_df = (
        hourly_df
        .groupby("date")
        .agg({
            "temperature": "mean",
            "precipitation": "sum",
            "wind_speed": "max"
        })
        .reset_index()
    )

    daily_df["weather_code"] = None

    return daily_df


# --------------------------------------------------
# MARINE FORECAST
# --------------------------------------------------

def get_marine_weather(latitude, longitude):

    marine_df = pd.DataFrame()

    try:

        marine_url = (
            "https://marine-api.open-meteo.com/v1/marine"
        )

        marine_params = {
            "latitude": latitude,
            "longitude": longitude,
            "hourly": (
                "wave_height,"
                "wave_period,"
                "wave_direction"
            ),
            "forecast_days": 8,
            "cell_selection": "sea",
            "timezone": "auto"
        }

        response = requests.get(
            marine_url,
            params=marine_params,
            timeout=15
        )

        response.raise_for_status()

        data = response.json()

        if "hourly" not in data:
            return marine_df

        hourly = data["hourly"]

        marine_hourly = pd.DataFrame({
            "datetime": pd.to_datetime(
                hourly["time"]
            ),
            "wave_height": hourly.get(
                "wave_height"
            ),
            "wave_period": hourly.get(
                "wave_period"
            ),
            "wave_direction": hourly.get(
                "wave_direction"
            )
        })

        marine_hourly["date"] = (
            marine_hourly["datetime"]
            .dt.normalize()
        )

        marine_df = (
            marine_hourly
            .groupby("date")
            .agg({
                "wave_height": "max",
                "wave_period": "max",
                "wave_direction": "mean"
            })
            .reset_index()
        )

    except Exception as e:

        print(
            "Marine forecast unavailable:",
            e
        )

    return marine_df


# --------------------------------------------------
# MAIN WEATHER FUNCTION
# --------------------------------------------------

def get_weather(location, target_date=None):

    coordinates = get_coordinates(location)

    if coordinates is None:

        print(
            "Location not found:",
            location
        )

        return None

    latitude, longitude = coordinates

    # --------------------------------------------------
    # NORMAL FORECAST
    # --------------------------------------------------

    normal_df = get_normal_weather(
        latitude,
        longitude
    )

    normal_df["forecast_type"] = "operational"

    normal_df["forecast_source"] = (
        "Open-Meteo Normal Forecast"
    )

    # --------------------------------------------------
    # ENSEMBLE FORECAST
    # --------------------------------------------------

    try:

        ensemble_df = get_ensemble_weather(
            latitude,
            longitude
        )

        ensemble_df["forecast_type"] = (
            "probabilistic"
        )

        ensemble_df["forecast_source"] = (
            "Open-Meteo GFS Ensemble Mean"
        )

    except Exception as e:

        print(
            "Ensemble forecast unavailable:",
            e
        )

        ensemble_df = pd.DataFrame()

    # --------------------------------------------------
    # COMBINE WEATHER
    # --------------------------------------------------

    if not ensemble_df.empty:

        final_df = pd.concat(
            [
                normal_df,
                ensemble_df
            ],
            ignore_index=True
        )

    else:

        final_df = normal_df.copy()

    final_df = (
        final_df
        .drop_duplicates(
            subset=["date"],
            keep="first"
        )
        .sort_values("date")
        .reset_index(drop=True)
    )

    # --------------------------------------------------
    # MARINE
    # --------------------------------------------------

    marine_df = get_marine_weather(
        latitude,
        longitude
    )

    if not marine_df.empty:

        final_df = final_df.merge(
            marine_df,
            on="date",
            how="left"
        )

        final_df["marine_available"] = (
            final_df["wave_height"].notna()
        )

    else:

        final_df["wave_height"] = None
        final_df["wave_period"] = None
        final_df["wave_direction"] = None

        final_df["marine_available"] = False

    # --------------------------------------------------
    # TARGET DATE
    # --------------------------------------------------

    if target_date is not None:

        target = (
            pd.to_datetime(target_date)
            .normalize()
        )

        matching_rows = final_df[
            final_df["date"] == target
        ]

        if matching_rows.empty:

            print(
                "Weather forecast unavailable for:",
                target.strftime("%Y-%m-%d")
            )

            return None

        row = matching_rows.iloc[0]

        # --------------------------------------------------
        # WEATHER DISRUPTION
        # --------------------------------------------------

        weather_disruption = None

        if pd.notna(row["weather_code"]):

            weather_input = pd.DataFrame([{
                "wind_speed": row["wind_speed"],
                "precipitation": row["precipitation"]
            }])

            weather_disruption = int(
                weather_model.predict(
                    weather_input
                )[0]
            )

        # --------------------------------------------------
        # MARINE RISK
        # --------------------------------------------------

        marine_risk = calculate_marine_risk(
            row["wave_height"],
            row["wave_period"]
        )

        # --------------------------------------------------
        # ENVIRONMENTAL RISK
        # --------------------------------------------------

        environmental_risk = (
            calculate_environmental_risk(
                weather_disruption,
                marine_risk[
                    "marine_risk_score"
                ]
            )
        )

        # --------------------------------------------------
        # RETURN RESULT
        # --------------------------------------------------

        return {

            "date": row["date"].strftime(
                "%Y-%m-%d"
            ),

            "temperature": row["temperature"],

            "precipitation": row["precipitation"],

            "wind_speed": row["wind_speed"],

            "weather_code": row["weather_code"],

            "forecast_type": row[
                "forecast_type"
            ],

            "forecast_source": row[
                "forecast_source"
            ],

            # Marine
            "wave_height": row[
                "wave_height"
            ],

            "wave_period": row[
                "wave_period"
            ],

            "wave_direction": row[
                "wave_direction"
            ],

            "marine_available": bool(
                row["marine_available"]
            ),

            # Risk
            "weather_disruption":
                weather_disruption,

            "marine_risk_score":
                marine_risk[
                    "marine_risk_score"
                ],

            "marine_risk_level":
                marine_risk[
                    "marine_risk_level"
                ],

            "environmental_risk_score":
                environmental_risk[
                    "environmental_risk_score"
                ],

            "environmental_risk_level":
                environmental_risk[
                    "environmental_risk_level"
                ]
        }

    return final_df


# --------------------------------------------------
# WEATHER DISRUPTION MODEL
# --------------------------------------------------

weather_model = joblib.load(
    "models/weather_disruption_model.pkl"
)


# --------------------------------------------------
# DIRECT TEST
# --------------------------------------------------

if __name__ == "__main__":

    location = input(
        "Enter port/location: "
    )

    target_date = input(
        "Enter target date (YYYY-MM-DD): "
    )

    weather = get_weather(
        location,
        target_date
    )

    if weather is None:

        print(
            "\nWeather forecast unavailable."
        )

    else:

        print(
            "\n========== WEATHER =========="
        )

        print(
            "Date:",
            weather["date"]
        )

        print(
            "Temperature:",
            weather["temperature"]
        )

        print(
            "Precipitation:",
            weather["precipitation"]
        )

        print(
            "Wind Speed:",
            weather["wind_speed"]
        )

        print(
            "Weather Code:",
            weather["weather_code"]
        )

        print(
            "Forecast Type:",
            weather["forecast_type"]
        )

        print(
            "Forecast Source:",
            weather["forecast_source"]
        )

        print(
            "\n========== MARINE =========="
        )

        print(
            "Wave Height:",
            weather["wave_height"]
        )

        print(
            "Wave Period:",
            weather["wave_period"]
        )

        print(
            "Wave Direction:",
            weather["wave_direction"]
        )

        print(
            "Marine Available:",
            weather["marine_available"]
        )

        print(
            "\n========== WEATHER DISRUPTION =========="
        )

        print(
            "Weather Disruption:",
            weather["weather_disruption"]
        )

        print(
            "\n========== MARINE INTELLIGENCE =========="
        )

        print(
            "Marine Risk Score:",
            weather["marine_risk_score"]
        )

        print(
            "Marine Risk Level:",
            weather["marine_risk_level"]
        )

        print(
            "\n========== ENVIRONMENTAL RISK =========="
        )

        print(
            "Environmental Risk Score:",
            weather[
                "environmental_risk_score"
            ]
        )

        print(
            "Environmental Risk Level:",
            weather[
                "environmental_risk_level"
            ]
        )