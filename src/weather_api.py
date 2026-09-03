import requests
import pandas as pd
import joblib


# ==========================================
# 1. LOAD WEATHER DISRUPTION ML MODEL
# ==========================================

model = joblib.load("models/weather_disruption_model.pkl")

print("Weather Disruption ML model loaded successfully!")


# ==========================================
# 2. GET LOCATION COORDINATES
# ==========================================

def get_coordinates(location):

    url = "https://geocoding-api.open-meteo.com/v1/search"

    params = {
        "name": location,
        "count": 1,
        "language": "en",
        "format": "json"
    }

    response = requests.get(url, params=params)

    if response.status_code != 200:
        print("Geocoding API error!")
        return None

    data = response.json()

    if "results" not in data:
        print("Location not found!")
        return None

    result = data["results"][0]

    return {
        "latitude": result["latitude"],
        "longitude": result["longitude"],
        "name": result["name"],
        "country": result.get("country", "")
    }


# ==========================================
# 3. GET CURRENT WEATHER
# ==========================================

def get_weather(location):

    coordinates = get_coordinates(location)

    if coordinates is None:
        return None

    url = "https://api.open-meteo.com/v1/forecast"

    params = {
        "latitude": coordinates["latitude"],
        "longitude": coordinates["longitude"],
        "current": "temperature_2m,precipitation,wind_speed_10m,weather_code"
    }

    response = requests.get(url, params=params)

    if response.status_code != 200:
        print("Weather API error!")
        return None

    data = response.json()

    current = data["current"]

    weather_data = {
        "location": coordinates["name"],
        "country": coordinates["country"],
        "temperature": current["temperature_2m"],
        "precipitation": current["precipitation"],
        "wind_speed": current["wind_speed_10m"],
        "weather_code": current["weather_code"]
    }

    return weather_data


# ==========================================
# 4. PREDICT WEATHER DISRUPTION
# ==========================================

def predict_weather_disruption(weather_data):

    # ML model ke liye sirf ye 3 features required hain
    prediction_input = pd.DataFrame([{
        "wind_speed": weather_data["wind_speed"],
        "precipitation": weather_data["precipitation"],
        "weather_code": weather_data["weather_code"]
    }])

    # Trained Random Forest model prediction
    prediction = model.predict(prediction_input)[0]

    return int(prediction)


# ==========================================
# 5. MAIN PROGRAM
# ==========================================

if __name__ == "__main__":

    location = input("Enter location: ")

    weather = get_weather(location)

    if weather:

        # Predict disruption using ML model
        disruption = predict_weather_disruption(weather)

        print("\n========== CURRENT WEATHER ==========")

        print("Location:", weather["location"])
        print("Country:", weather["country"])
        print("Temperature:", weather["temperature"], "°C")
        print("Precipitation:", weather["precipitation"], "mm")
        print("Wind Speed:", weather["wind_speed"], "km/h")
        print("Weather Code:", weather["weather_code"])

        print("\n========== ML PREDICTION ==========")

        print("Weather Disruption:", disruption)

        if disruption == 1:
            print("Status: WEATHER DISRUPTION DETECTED")
        else:
            print("Status: NO WEATHER DISRUPTION")