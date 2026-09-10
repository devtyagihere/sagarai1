import pandas as pd
import joblib
import os

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report


# --------------------------------------------------
# LOAD DATA
# --------------------------------------------------

data = pd.read_csv(
    "data/weather_disruption_data.csv"
)

print("Weather disruption dataset loaded!")
print("Rows:", len(data))


# --------------------------------------------------
# FEATURES AND TARGET
# --------------------------------------------------

features = [
    "wind_speed",
    "precipitation"
]

target = "weather_disruption"


X = data[features]
y = data[target]


# --------------------------------------------------
# TRAIN / TEST SPLIT
# --------------------------------------------------

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42,
    stratify=y
)


print("\nTraining rows:", len(X_train))
print("Testing rows:", len(X_test))


# --------------------------------------------------
# RANDOM FOREST MODEL
# --------------------------------------------------

model = RandomForestClassifier(
    n_estimators=100,
    max_depth=5,
    random_state=42,
    n_jobs=-1
)


# --------------------------------------------------
# TRAIN MODEL
# --------------------------------------------------

print("\nTraining weather disruption model...")

model.fit(
    X_train,
    y_train
)

print("Model trained successfully!")


# --------------------------------------------------
# EVALUATION
# --------------------------------------------------

y_pred = model.predict(X_test)

accuracy = accuracy_score(
    y_test,
    y_pred
)

print("\n========== MODEL PERFORMANCE ==========")

print(
    "Accuracy:",
    round(accuracy, 4)
)

print("\nClassification Report:")

print(
    classification_report(
        y_test,
        y_pred,
        zero_division=0
    )
)


# --------------------------------------------------
# SAVE MODEL
# --------------------------------------------------

os.makedirs(
    "models",
    exist_ok=True
)

model_path = (
    "models/weather_disruption_model.pkl"
)

joblib.dump(
    model,
    model_path
)

print("\nModel saved successfully!")

print(
    "Location:",
    model_path
)

print(
    "\n========== TRAINING COMPLETE =========="
)