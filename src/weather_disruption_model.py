import pandas as pd
import os
import joblib

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report


# 1. Load dataset
data = pd.read_csv("data/weather_disruption_data.csv")

print("Dataset loaded!")
print(data)


# 2. Input features
features = [
    "wind_speed",
    "precipitation",
    "weather_code"
]

target = "weather_disruption"

X = data[features]
y = data[target]


# 3. Split dataset
X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42,
    stratify=y
)

print("\nTraining samples:", len(X_train))
print("Testing samples:", len(X_test))


# 4. Create ML model
model = RandomForestClassifier(
    n_estimators=100,
    random_state=42,
    max_depth=5
)


# 5. Train model
print("\nTraining Weather Disruption Model...")

model.fit(X_train, y_train)

print("Model trained successfully!")


# 6. Test model
y_pred = model.predict(X_test)

accuracy = accuracy_score(y_test, y_pred)

print("\n========== MODEL PERFORMANCE ==========")
print("Accuracy:", round(accuracy, 2))

print("\nClassification Report:")
print(classification_report(y_test, y_pred))


# 7. Save model
os.makedirs("models", exist_ok=True)

model_path = "models/weather_disruption_model.pkl"

joblib.dump(model, model_path)

print("\nModel saved successfully!")
print("Location:", model_path)