import pandas as pd
import joblib


# ==========================================
# 1. LOAD TRAINED MODEL
# ==========================================

model_path = "models/freight_model.pkl"

model = joblib.load(model_path)

print("Trained model loaded successfully!")


# ==========================================
# 2. NEW SHIPMENT DATA
# ==========================================

new_data = pd.DataFrame([{
    "origin_port": "Mumbai",
    "destination_port": "Dubai",
    "cargo_type": "Steel",
    "bdi": 1800,
    "oil_price": 85,
    "commodity_price": 500,
    "commodity_demand": 75,
    "weather_disruption": 1,
    "port_congestion": 60,
    "usd_index": 104,
    "year": 2026,
    "month": 9,
    "day": 1
}])


# ==========================================
# 3. MAKE PREDICTION
# ==========================================

prediction = model.predict(new_data)


# ==========================================
# 4. SHOW RESULT
# ==========================================

print("\n========== FREIGHT RATE PREDICTION ==========")

print("Origin Port      :", new_data["origin_port"].iloc[0])
print("Destination Port :", new_data["destination_port"].iloc[0])
print("Cargo Type       :", new_data["cargo_type"].iloc[0])

print("Predicted Freight Rate:", round(prediction[0], 2))

print("\n========== PREDICTION COMPLETE ==========")