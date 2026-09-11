"""
Freight Rate Forecasting Service using scikit-learn Random Forest.

MODEL DESIGN (kept simple and explainable for viva):
- Algorithm : RandomForestRegressor (ensemble of decision trees)
- Features  : BDI, oil price, commodity price, distance, vessel type (encoded),
              cargo type (encoded)
- Target    : freight_rate_usd_mt
- Split     : chronological 80/20 (older data = train, newer = test)
- Forecast  : project market inputs N days ahead using trend extrapolation,
              then predict rate from those projected inputs

HONEST DISCLAIMER:
- Trained on SYNTHETIC data — metrics reflect synthetic patterns, not real markets.
- Forecast horizon beyond 30 days is not reliable.
- This is an educational ML demonstration, not a commercial forecasting tool.
"""

from __future__ import annotations

import math
from typing import Dict, List, Optional, Tuple

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.preprocessing import LabelEncoder

from app.models.market import FreightForecast, ModelEvaluation
from app.services.market_service import MarketDataService, default_market_service
from config import ML_N_ESTIMATORS, ML_RANDOM_STATE, ML_TEST_SIZE, MARKET_DATA_SOURCE

# ─────────────────────────────────────────────────────────────────────────────
# Feature and label definitions
# ─────────────────────────────────────────────────────────────────────────────

NUMERIC_FEATURES = ["bdi", "oil_price", "commodity_price", "distance_nm"]
CATEGORICAL_FEATURES = ["vessel_type", "cargo_type"]
ALL_FEATURES = NUMERIC_FEATURES + ["vessel_type_enc", "cargo_type_enc"]
TARGET = "freight_rate_usd_mt"


class FreightForecastingService:
    """
    Trains a Random Forest on freight history, evaluates it honestly,
    and generates rate forecasts for 7 / 15 / 30 day horizons.
    """

    def __init__(self, market_service: Optional[MarketDataService] = None):
        self.market_service = market_service or default_market_service
        self._model: Optional[RandomForestRegressor] = None
        self._vessel_enc: Optional[LabelEncoder] = None
        self._cargo_enc:  Optional[LabelEncoder] = None
        self._evaluation: Optional[ModelEvaluation] = None
        self._is_trained: bool = False

    # ──────────────────────────────────────────────────────────────────────
    # Data preparation
    # ──────────────────────────────────────────────────────────────────────

    def _prepare_data(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Encode categorical features, handle missing values, chronological split.
        Returns (train_df, test_df).
        """
        df = df.copy()
        df = df.dropna(subset=NUMERIC_FEATURES + CATEGORICAL_FEATURES + [TARGET])

        # Label encode vessel_type and cargo_type
        self._vessel_enc = LabelEncoder()
        self._cargo_enc  = LabelEncoder()
        df["vessel_type_enc"] = self._vessel_enc.fit_transform(df["vessel_type"].str.lower())
        df["cargo_type_enc"]  = self._cargo_enc.fit_transform(df["cargo_type"].str.lower())

        # Chronological split — no data leakage
        n = len(df)
        split_idx = int(n * (1.0 - ML_TEST_SIZE))
        train_df = df.iloc[:split_idx].copy()
        test_df  = df.iloc[split_idx:].copy()
        return train_df, test_df

    # ──────────────────────────────────────────────────────────────────────
    # Training & Evaluation
    # ──────────────────────────────────────────────────────────────────────

    def train(self, force_retrain: bool = False) -> ModelEvaluation:
        """
        Load freight history, train a Random Forest, evaluate on holdout set.
        Results are stored in self._evaluation and returned.
        """
        if self._is_trained and not force_retrain:
            return self._evaluation

        df = self.market_service.get_freight_df()

        if len(df) < 20:
            # Not enough data to train meaningfully
            self._evaluation = ModelEvaluation(
                model_name="RandomForestRegressor",
                mae=None, rmse=None, r2=None,
                train_samples=0, test_samples=0,
                features_used=ALL_FEATURES,
                training_data_source=MARKET_DATA_SOURCE,
                note="Insufficient training data (< 20 rows). Model not trained.",
            )
            return self._evaluation

        train_df, test_df = self._prepare_data(df)
        X_train = train_df[ALL_FEATURES].values
        y_train = train_df[TARGET].values
        X_test  = test_df[ALL_FEATURES].values
        y_test  = test_df[TARGET].values

        # Train Random Forest
        self._model = RandomForestRegressor(
            n_estimators=ML_N_ESTIMATORS,
            random_state=ML_RANDOM_STATE,
            n_jobs=-1,
        )
        self._model.fit(X_train, y_train)
        self._is_trained = True

        # Evaluate on test set
        if len(X_test) > 0:
            y_pred = self._model.predict(X_test)
            mae  = round(float(mean_absolute_error(y_test, y_pred)), 4)
            rmse = round(float(math.sqrt(mean_squared_error(y_test, y_pred))), 4)
            r2   = round(float(r2_score(y_test, y_pred)), 4)
            note = (
                f"Model trained on {len(X_train)} SYNTHETIC samples. "
                f"MAE={mae:.2f} USD/mt means predictions are off by ~{mae:.1f} USD/mt on average. "
                "Metrics reflect synthetic data patterns only — not real market performance."
            )
        else:
            mae = rmse = r2 = None
            note = "Test set was empty — no evaluation possible."

        self._evaluation = ModelEvaluation(
            model_name="RandomForestRegressor",
            mae=mae,
            rmse=rmse,
            r2=r2,
            train_samples=len(X_train),
            test_samples=len(X_test),
            features_used=ALL_FEATURES,
            training_data_source=MARKET_DATA_SOURCE,
            note=note,
        )
        return self._evaluation

    # ──────────────────────────────────────────────────────────────────────
    # Forecasting
    # ──────────────────────────────────────────────────────────────────────

    def _encode_vessel(self, vessel_type: str) -> int:
        """Encode a vessel type string. Returns 0 if unseen label."""
        if self._vessel_enc is None:
            return 0
        try:
            return int(self._vessel_enc.transform([vessel_type.lower()])[0])
        except ValueError:
            return 0   # unknown class → use 0

    def _encode_cargo(self, cargo_type: str) -> int:
        """Encode a cargo type string. Returns 0 if unseen label."""
        if self._cargo_enc is None:
            return 0
        try:
            return int(self._cargo_enc.transform([cargo_type.lower()])[0])
        except ValueError:
            return 0

    def _predict_for_market(
        self,
        bdi: float,
        oil_price: float,
        commodity_price: float,
        distance_nm: float,
        vessel_type: str,
        cargo_type: str,
    ) -> float:
        """Build one feature vector and predict freight rate."""
        if self._model is None:
            raise RuntimeError("Model has not been trained yet. Call train() first.")
        features = np.array([[
            bdi, oil_price, commodity_price, distance_nm,
            self._encode_vessel(vessel_type),
            self._encode_cargo(cargo_type),
        ]])
        return float(self._model.predict(features)[0])

    def forecast(
        self,
        origin: str,
        destination: str,
        cargo_type: str,
        vessel_type: str,
        distance_nm: float,
    ) -> Optional[FreightForecast]:
        """
        Generate freight rate forecasts for 7 / 15 / 30 day horizons.

        Steps:
        1. Get current market values (BDI, oil, commodity)
        2. Get most recent historical rate for this route
        3. Use model to predict rate at current market values (as baseline)
        4. Project market values N days ahead using trend extrapolation
        5. Predict rate for each projected market state
        6. Return structured FreightForecast

        Returns None if model is not trained or if commodity data is unavailable.
        """
        if not self._is_trained:
            self.train()

        if self._model is None:
            # Training failed (insufficient data)
            return None

        # Commodity price for this cargo type
        comm_indicator = self.market_service.get_commodity_indicator(cargo_type)
        if comm_indicator is None:
            # Use average commodity price from freight history as fallback
            df = self.market_service.get_freight_df()
            route_mask = df["cargo_type"].str.lower() == cargo_type.lower()
            if route_mask.any():
                comm_price = float(df.loc[route_mask, "commodity_price"].mean())
            else:
                comm_price = 100.0
        else:
            comm_price = comm_indicator.current_value

        # Current market state
        current_market = self.market_service.get_latest_market_values()
        current_bdi = current_market["bdi"]
        current_oil = current_market["oil_price"]

        # Current rate from history (most recent 4 records for this route)
        current_rate = self.market_service.get_recent_rate(
            origin, destination, cargo_type, vessel_type
        )
        if current_rate is None:
            # No exact route match — predict from current market
            try:
                current_rate = self._predict_for_market(
                    current_bdi, current_oil, comm_price, distance_nm,
                    vessel_type, cargo_type
                )
            except Exception:
                return None

        # Project and predict for each horizon
        forecasts: Dict[int, float] = {}
        for days in (7, 15, 30):
            proj = self.market_service.project_market_values(days)
            try:
                rate = self._predict_for_market(
                    proj["bdi"], proj["oil_price"], comm_price,
                    distance_nm, vessel_type, cargo_type
                )
                forecasts[days] = round(max(2.0, rate), 2)
            except Exception:
                forecasts[days] = current_rate   # fallback to current

        forecast_30d = forecasts[30]
        change_pct   = round(((forecast_30d - current_rate) / max(current_rate, 0.01)) * 100, 2)

        if change_pct > 2.0:
            direction = "up"
        elif change_pct < -2.0:
            direction = "down"
        else:
            direction = "stable"

        return FreightForecast(
            origin=origin,
            destination=destination,
            cargo_type=cargo_type,
            vessel_type=vessel_type,
            current_rate_usd_mt=round(current_rate, 2),
            forecast_7d_usd_mt=forecasts[7],
            forecast_15d_usd_mt=forecasts[15],
            forecast_30d_usd_mt=forecasts[30],
            forecast_direction=direction,
            forecast_change_percent=change_pct,
            model_name="RandomForestRegressor",
            data_source=MARKET_DATA_SOURCE,
        )

    def get_evaluation(self) -> Optional[ModelEvaluation]:
        """Return cached evaluation metrics (None if not yet trained)."""
        return self._evaluation


# Global singleton — trained lazily on first forecast request
default_forecasting_service = FreightForecastingService()
