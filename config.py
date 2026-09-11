"""Configuration settings for the Shipping & Vessel Intelligence Engine."""

from pathlib import Path
from typing import Dict

# Project Base Paths
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
MARKET_DATA_DIR = DATA_DIR / "market"

# Default Dataset File Paths
DEFAULT_VESSELS_FILE = DATA_DIR / "vessels.csv"
DEFAULT_PORTS_FILE = DATA_DIR / "ports.csv"
DEFAULT_CARGO_TYPES_FILE = DATA_DIR / "cargo_types.csv"

# Market Data File Paths
DEFAULT_BDI_FILE            = MARKET_DATA_DIR / "bdi_history.csv"
DEFAULT_OIL_FILE            = MARKET_DATA_DIR / "oil_prices.csv"
DEFAULT_COMMODITY_FILE      = MARKET_DATA_DIR / "commodity_prices.csv"
DEFAULT_FREIGHT_HISTORY_FILE= MARKET_DATA_DIR / "freight_history.csv"

# Data provenance — NEVER claim synthetic data is live
MARKET_DATA_SOURCE: str = "SYNTHETIC"  # Options: SYNTHETIC, DEMO, REAL, LIVE

# Configurable Scoring Weights
DEFAULT_SCORING_WEIGHTS: Dict[str, float] = {
    "capacity_utilization": 0.40,
    "port_confidence": 0.30,
    "cargo_compatibility": 0.20,
    "operational_efficiency": 0.10,
}

# Capacity & Operational Thresholds
LOW_UTILIZATION_THRESHOLD: float = 0.50  # Flag warning if < 50% capacity used
OPTIMAL_UTILIZATION_MIN: float = 0.75   # Optimal loading range starts at 75%
OPTIMAL_UTILIZATION_MAX: float = 1.00   # Max 100%

# Maritime Navigation Constants
NAUTICAL_MILE_KM: float = 1.852
DEFAULT_VESSEL_SPEED_KNOTS: float = 14.0
HOURS_PER_DAY: float = 24.0

# Route Distance Adjustment Factor (Geodesic to estimated Sea-Lane baseline)
MARITIME_DETOUR_FACTOR: float = 1.15

# ML Model Configuration
ML_TEST_SIZE: float = 0.20          # 20% holdout for evaluation
ML_RANDOM_STATE: int = 42
ML_N_ESTIMATORS: int = 100          # RF trees — enough for a class project, not overkill

# ── Port Operations ──────────────────────────────────────────────────────────
DEFAULT_PORT_OPERATIONS_FILE = MARKET_DATA_DIR / "port_operations.csv"

# Congestion classification thresholds (score 0-100)
CONGESTION_LOW_THRESHOLD:           float = 25.0
CONGESTION_LOW_MODERATE_THRESHOLD:  float = 45.0
CONGESTION_MODERATE_THRESHOLD:      float = 65.0
CONGESTION_HIGH_THRESHOLD:          float = 80.0
# >= 80 → VERY HIGH

# ── Vessel Daily Rates (USD/day) ─────────────────────────────────────────────
# Based on Baltic Exchange indicative rates, 2023-2024 average range.
# Used for voyage cost estimation. Labeled SYNTHETIC/DEMO.
VESSEL_DAILY_RATES_USD: dict = {
    "mini-bulker": 7_500,
    "handysize":   12_000,
    "handymax":    16_000,
    "supramax":    19_000,
    "panamax":     23_000,
    "capesize":    28_000,
}

# ── Risk Score Thresholds ────────────────────────────────────────────────────
RISK_LOW_THRESHOLD:           float = 20.0
RISK_LOW_MODERATE_THRESHOLD:  float = 40.0
RISK_MODERATE_THRESHOLD:      float = 60.0
RISK_HIGH_THRESHOLD:          float = 75.0
# >= 75 → VERY HIGH

# ── Phase 4: Decision Engine Weights ─────────────────────────────────────────
# Factor weights must sum to exactly 1.00.
# Each weight reflects that factor's importance in the charter timing decision.
#
# freight_trend   0.20 — Most direct signal: if rates forecast to fall, charter now.
# bdi_trend       0.15 — Baltic Dry Index reflects overall dry-bulk market sentiment.
# oil_trend       0.10 — Bunker fuel cost driver; rising oil inflates voyage costs.
# commodity_trend 0.10 — Rising cargo commodity price → shipper urgency to export.
# port_congestion 0.15 — High congestion adds demurrage risk & delays.
# risk            0.15 — Weather/marine risk affects safety and schedule certainty.
# vessel_economics0.15 — Cheapest feasible voyage cost vs market median.
DECISION_WEIGHTS: Dict[str, float] = {
    "freight_trend":    0.20,
    "bdi_trend":        0.15,
    "oil_trend":        0.10,
    "commodity_trend":  0.10,
    "port_congestion":  0.15,
    "risk":             0.15,
    "vessel_economics": 0.15,
}

# ── Phase 4: Decision Thresholds ─────────────────────────────────────────────
# overall_score >= CHARTER_THRESHOLD  -> CHARTER NOW
# overall_score >= NEGOTIATE_THRESHOLD -> NEGOTIATE
# otherwise                            -> WAIT
DECISION_CHARTER_THRESHOLD:   float = 65.0
DECISION_NEGOTIATE_THRESHOLD:  float = 40.0
