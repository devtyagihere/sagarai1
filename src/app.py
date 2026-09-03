from flask import Flask, request, jsonify
import pandas as pd
import joblib

# Weather functions
from src.weather_api import get_weather, predict_weather_disruption


# ==========================================
# 1. CREATE FLASK APP
# ==========================================

app = Flask(__name__)


# ==========================================
# 2. LOAD TRAINED FREIGHT ML MODEL
# ==========================================

model = joblib.load("models/freight_model.pkl")

print("Freight ML model loaded successfully!")


# ==========================================
# 3. HOME / HEALTH CHECK
# ==========================================

@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "message": "Freight Intelligence API is running!"
    })


# ==========================================
# 4. FREIGHT PREDICTION API
# ==========================================

@app.route("/predict", methods=["POST"])
def predict():

    # Get data sent by user/frontend
    input_data = request.get_json()

    # ==========================================
    # 4.1 GET WEATHER AUTOMATICALLY
    # ==========================================

    weather_location = input_data["weather_location"]

    weather = get_weather(weather_location)

    if weather is None:
        return jsonify({
            "error": "Unable to fetch weather data"
        }), 400

    # ==========================================
    # 4.2 WEATHER ML PREDICTION
    # ==========================================

    weather_disruption = predict_weather_disruption(weather)

    # Add automatically predicted weather disruption
    # to freight prediction input
    input_data["weather_disruption"] = weather_disruption


    # ==========================================
    # 4.3 CONVERT INPUT TO DATAFRAME
    # ==========================================

    data = pd.DataFrame([input_data])


    # ==========================================
    # 4.4 PROCESS DATE
    # ==========================================

    data["date"] = pd.to_datetime(data["date"])

    data["year"] = data["date"].dt.year
    data["month"] = data["date"].dt.month
    data["day"] = data["date"].dt.day


    # ==========================================
    # 4.5 FEATURES REQUIRED BY FREIGHT ML
    # ==========================================

    features = [
        "origin_port",
        "destination_port",
        "cargo_type",
        "bdi",
        "oil_price",
        "commodity_price",
        "commodity_demand",
        "weather_disruption",
        "port_congestion",
        "usd_index",
        "year",
        "month",
        "day"
    ]


    # Select required features
    X = data[features]


    # ==========================================
    # 4.6 FREIGHT RATE PREDICTION
    # ==========================================

    prediction = model.predict(X)


    # ==========================================
    # 4.7 RETURN RESULT
    # ==========================================

    return jsonify({

        "origin_port": input_data["origin_port"],

        "destination_port": input_data["destination_port"],

        "cargo_type": input_data["cargo_type"],

        "weather_location": weather["location"],

        "weather_disruption": weather_disruption,

        "predicted_freight_rate": round(
            float(prediction[0]), 2
        )
    })


# ==========================================
# 5. START API SERVER
# ==========================================

if __name__ == "__main__":
    app.run(debug=True)