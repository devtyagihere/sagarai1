import pandas as pd
import os
import joblib

from sklearn.model_selection import train_test_split
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder
from sklearn.ensemble import RandomForestRegressor
from sklearn.pipeline import Pipeline
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score


# ==========================================
# 1. LOAD DATA
# ==========================================

data = pd.read_csv("data/demo_data.csv")

print("Dataset loaded successfully!")
print("Rows:", len(data))
print("Columns:", len(data.columns))
print("\nAvailable columns:")
print(data.columns.tolist())


# ==========================================
# 2. PREPARE DATE
# ==========================================

data["date"] = pd.to_datetime(data["date"])

# Extract useful information from date
data["year"] = data["date"].dt.year
data["month"] = data["date"].dt.month
data["day"] = data["date"].dt.day


# ==========================================
# 3. SELECT FEATURES
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

target = "freight_rate"


# ==========================================
# 4. INPUT AND OUTPUT
# ==========================================

X = data[features]
y = data[target]

print("\nFeatures:")
print(features)

print("\nTarget:")
print(target)


# ==========================================
# 5. CATEGORICAL AND NUMERICAL FEATURES
# ==========================================

categorical_features = [
    "origin_port",
    "destination_port",
    "cargo_type"
]

numerical_features = [
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


# ==========================================
# 6. PREPROCESSING
# ==========================================

preprocessor = ColumnTransformer(
    transformers=[
        (
            "categorical",
            OneHotEncoder(handle_unknown="ignore"),
            categorical_features
        ),
        (
            "numerical",
            "passthrough",
            numerical_features
        )
    ]
)


# ==========================================
# 7. CREATE AI MODEL
# ==========================================

model = RandomForestRegressor(
    n_estimators=100,
    random_state=42,
    max_depth=15,
    n_jobs=-1
)


# ==========================================
# 8. CREATE PIPELINE
# ==========================================

pipeline = Pipeline(
    steps=[
        ("preprocessor", preprocessor),
        ("model", model)
    ]
)


# ==========================================
# 9. TRAIN-TEST SPLIT
# ==========================================

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42
)

print("\nTraining data:", len(X_train))
print("Testing data:", len(X_test))


# ==========================================
# 10. TRAIN MODEL
# ==========================================

print("\nTraining Random Forest model...")

pipeline.fit(X_train, y_train)

print("Model trained successfully!")


# ==========================================
# 11. MAKE PREDICTIONS
# ==========================================

y_pred = pipeline.predict(X_test)


# ==========================================
# 12. MODEL EVALUATION
# ==========================================

mae = mean_absolute_error(y_test, y_pred)
mse = mean_squared_error(y_test, y_pred)
rmse = mse ** 0.5
r2 = r2_score(y_test, y_pred)

print("\n========== MODEL PERFORMANCE ==========")

print("MAE  :", round(mae, 2))
print("RMSE :", round(rmse, 2))
print("R2   :", round(r2, 4))


# ==========================================
# 13. SHOW SAMPLE PREDICTIONS
# ==========================================

results = pd.DataFrame({
    "Actual Freight Rate": y_test.values,
    "Predicted Freight Rate": y_pred
})

print("\n========== SAMPLE PREDICTIONS ==========")
print(results.head(10))


# ==========================================
# 14. SAVE MODEL
# ==========================================

os.makedirs("models", exist_ok=True)

model_path = "models/freight_model.pkl"

joblib.dump(pipeline, model_path)

print("\nModel saved successfully!")
print("Location:", model_path)

print("\n========== TRAINING COMPLETE ==========")