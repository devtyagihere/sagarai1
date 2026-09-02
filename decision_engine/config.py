# Decision Engine Configuration


# -----------------------------
# Risk Weights
# -----------------------------

RISK_WEIGHTS = {
    "freight_volatility": 0.30,
    "port_congestion": 0.25,
    "vessel_reliability": 0.20,
    "delay_probability": 0.15,
    "forecast_uncertainty": 0.10
}


# -----------------------------
# Decision Score Weights
# -----------------------------

DECISION_WEIGHTS = {
    "cost": 0.40,
    "risk": 0.30,
    "forecast": 0.20,
    "reliability": 0.10
}


# -----------------------------
# Booking Decision Thresholds
# -----------------------------

BOOK_THRESHOLD = 75
WAIT_THRESHOLD = 50