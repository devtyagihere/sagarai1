"""
Market Data Service — loads and analyses BDI, oil, commodity and freight data.

DATA PROVENANCE: All data shipped with this project is SYNTHETIC.
It is generated from statistical parameters inspired by real maritime markets
(2022-2024 range) but is NOT real trading data.

If live data sources become available, replace the CSV loaders with API clients
and update MARKET_DATA_SOURCE in config.py to "LIVE".
"""

from pathlib import Path
from typing import Dict, List, Optional, Tuple
import pandas as pd

from app.models.market import MarketIndicator, MarketSnapshot
from config import (
    DEFAULT_BDI_FILE,
    DEFAULT_COMMODITY_FILE,
    DEFAULT_FREIGHT_HISTORY_FILE,
    DEFAULT_OIL_FILE,
    MARKET_DATA_SOURCE,
)


class MarketDataService:
    """
    Loads market datasets and computes current values, trends, and changes.

    All loaded data is tagged with its actual provenance (SYNTHETIC/DEMO/REAL/LIVE).
    The service NEVER claims synthetic data is live.
    """

    def __init__(
        self,
        bdi_path: Optional[Path] = None,
        oil_path: Optional[Path] = None,
        commodity_path: Optional[Path] = None,
        freight_path: Optional[Path] = None,
    ):
        self.bdi_path       = bdi_path       or DEFAULT_BDI_FILE
        self.oil_path       = oil_path       or DEFAULT_OIL_FILE
        self.commodity_path = commodity_path or DEFAULT_COMMODITY_FILE
        self.freight_path   = freight_path   or DEFAULT_FREIGHT_HISTORY_FILE

        self._bdi_df:       Optional[pd.DataFrame] = None
        self._oil_df:       Optional[pd.DataFrame] = None
        self._comm_df:      Optional[pd.DataFrame] = None
        self._freight_df:   Optional[pd.DataFrame] = None
        self._loaded:       bool = False

    # ──────────────────────────────────────────────────────────────────────
    # Loading
    # ──────────────────────────────────────────────────────────────────────

    def load_all(self, force_reload: bool = False) -> None:
        """Load all market datasets into memory (cached after first load)."""
        if self._loaded and not force_reload:
            return
        self._bdi_df     = self._load_csv(self.bdi_path,       "date")
        self._oil_df     = self._load_csv(self.oil_path,       "date")
        self._comm_df    = self._load_csv(self.commodity_path, "date")
        self._freight_df = self._load_csv(self.freight_path,   "date")
        self._loaded = True

    def _load_csv(self, path: Path, date_col: str) -> pd.DataFrame:
        """Load CSV, parse dates, sort chronologically."""
        if not path.exists():
            raise FileNotFoundError(f"Market data file not found: {path}")
        df = pd.read_csv(path, parse_dates=[date_col])
        df = df.sort_values(date_col).reset_index(drop=True)
        return df

    # ──────────────────────────────────────────────────────────────────────
    # Generic indicator builder
    # ──────────────────────────────────────────────────────────────────────

    def _build_indicator(
        self,
        df: pd.DataFrame,
        date_col: str,
        value_col: str,
        name: str,
        unit: str,
    ) -> MarketIndicator:
        """
        From a time-series DataFrame, build a MarketIndicator with:
        - current value (latest row)
        - previous value (row before latest)
        - 7-day and 30-day rolling averages
        - direction and % change
        """
        series = df[[date_col, value_col]].dropna().copy()
        series = series.sort_values(date_col)

        if len(series) < 2:
            raise ValueError(f"Insufficient data to compute indicator '{name}' (need ≥2 rows).")

        latest_row   = series.iloc[-1]
        prev_row     = series.iloc[-2]

        current      = float(latest_row[value_col])
        previous     = float(prev_row[value_col])
        change_abs   = round(current - previous, 4)
        change_pct   = round((change_abs / previous) * 100, 2) if previous != 0 else 0.0

        # Rolling averages: last N rows (approximately N days when daily data)
        trend_7d  = round(float(series[value_col].tail(7).mean()),  4)
        trend_30d = round(float(series[value_col].tail(30).mean()), 4)

        if change_abs > 0:
            direction = "up"
        elif change_abs < 0:
            direction = "down"
        else:
            direction = "stable"

        # Detect data source from 'data_source' column if present
        provenance = MARKET_DATA_SOURCE
        if "data_source" in df.columns:
            src_vals = df["data_source"].dropna().unique()
            if len(src_vals) == 1:
                provenance = str(src_vals[0])

        return MarketIndicator(
            name=name,
            current_value=round(current, 2),
            previous_value=round(previous, 2),
            change_absolute=round(change_abs, 2),
            change_percent=change_pct,
            trend_7d=round(trend_7d, 2),
            trend_30d=round(trend_30d, 2),
            direction=direction,
            unit=unit,
            data_source=provenance,
            as_of_date=str(latest_row[date_col])[:10],
        )

    # ──────────────────────────────────────────────────────────────────────
    # Public API
    # ──────────────────────────────────────────────────────────────────────

    def get_bdi_indicator(self) -> MarketIndicator:
        """Return Baltic Dry Index (BDI) indicator."""
        self.load_all()
        return self._build_indicator(
            self._bdi_df, "date", "bdi",
            name="Baltic Dry Index (BDI)", unit="index points"
        )

    def get_oil_indicator(self) -> MarketIndicator:
        """Return WTI crude oil price indicator."""
        self.load_all()
        return self._build_indicator(
            self._oil_df, "date", "wti_usd_bbl",
            name="WTI Crude Oil", unit="USD/barrel"
        )

    def get_commodity_indicator(self, cargo_type: str) -> Optional[MarketIndicator]:
        """
        Return commodity price indicator relevant to the given cargo type.
        Returns None if the cargo type has no mapped commodity price.
        """
        self.load_all()
        col_map = {
            "iron_ore":    ("iron_ore_usd_t",  "Iron Ore",  "USD/tonne"),
            "coal":        ("coal_usd_t",       "Thermal/Coking Coal", "USD/tonne"),
            "grain":       ("grain_usd_t",      "Grain",     "USD/tonne"),
            "bauxite":     ("bauxite_usd_t",    "Bauxite",   "USD/tonne"),
            "fertilizer":  ("fertilizer_usd_t", "Fertilizer","USD/tonne"),
        }
        mapping = col_map.get(cargo_type.strip().lower())
        if mapping is None:
            return None
        col, label, unit = mapping
        return self._build_indicator(
            self._comm_df, "date", col, name=f"{label} Commodity Price", unit=unit
        )

    def get_market_snapshot(self, cargo_type: Optional[str] = None) -> MarketSnapshot:
        """
        Return a full market snapshot: BDI + oil + optional commodity price.
        Includes mandatory data provenance disclaimer.
        """
        self.load_all()
        bdi_ind  = self.get_bdi_indicator()
        oil_ind  = self.get_oil_indicator()
        comm_ind = self.get_commodity_indicator(cargo_type) if cargo_type else None

        return MarketSnapshot(
            bdi=bdi_ind,
            oil_price=oil_ind,
            commodity_price=comm_ind,
            data_source=MARKET_DATA_SOURCE,
        )

    def get_freight_df(self) -> pd.DataFrame:
        """Return the raw freight history DataFrame (for ML training)."""
        self.load_all()
        return self._freight_df.copy()

    def get_recent_rate(
        self,
        origin: str,
        destination: str,
        cargo_type: str,
        vessel_type: str,
        n_recent: int = 4,
    ) -> Optional[float]:
        """
        Return the average of the most recent N freight rates for a given route.
        Case-insensitive matching. Returns None if no matching records found.
        """
        self.load_all()
        df = self._freight_df
        mask = (
            (df["origin"].str.lower()       == origin.lower())      &
            (df["destination"].str.lower()  == destination.lower()) &
            (df["cargo_type"].str.lower()   == cargo_type.lower())  &
            (df["vessel_type"].str.lower()  == vessel_type.lower())
        )
        subset = df[mask].tail(n_recent)
        if subset.empty:
            return None
        return round(float(subset["freight_rate_usd_mt"].mean()), 2)

    def get_recent_market_values(self, n_days: int = 30) -> Dict[str, float]:
        """
        Return average BDI and oil price over the last n_days.
        Used as feature inputs to the ML model for forecasting.
        """
        self.load_all()
        bdi_recent = float(self._bdi_df["bdi"].tail(n_days).mean())
        oil_recent = float(self._oil_df["wti_usd_bbl"].tail(n_days).mean())
        return {"bdi": round(bdi_recent, 1), "oil_price": round(oil_recent, 2)}

    def get_latest_market_values(self) -> Dict[str, float]:
        """Return most recent single-day BDI and oil price."""
        self.load_all()
        bdi_latest = float(self._bdi_df["bdi"].iloc[-1])
        oil_latest = float(self._oil_df["wti_usd_bbl"].iloc[-1])
        return {"bdi": bdi_latest, "oil_price": oil_latest}

    def project_market_values(self, days_ahead: int) -> Dict[str, float]:
        """
        Project BDI and oil price N days into the future using a simple
        linear extrapolation of the last 30-day trend.

        This is a naive but transparent extrapolation — clearly NOT a prediction.
        The ML model uses these projected values as inputs for forecasting rates.
        """
        self.load_all()
        bdi_series = self._bdi_df["bdi"].tail(30).values
        oil_series = self._oil_df["wti_usd_bbl"].tail(30).values

        # Linear trend: slope = (last - first) / (n-1)
        bdi_slope  = (bdi_series[-1] - bdi_series[0])  / max(len(bdi_series) - 1, 1)
        oil_slope  = (oil_series[-1] - oil_series[0])  / max(len(oil_series) - 1, 1)

        # Project forward, clamp to realistic bounds
        proj_bdi = max(400.0, min(4500.0, float(bdi_series[-1]) + bdi_slope * days_ahead))
        proj_oil = max(45.0,  min(120.0,  float(oil_series[-1]) + oil_slope * days_ahead))

        return {
            "bdi":       round(proj_bdi, 1),
            "oil_price": round(proj_oil, 2),
        }


# Global singleton — shared across the application
default_market_service = MarketDataService()
