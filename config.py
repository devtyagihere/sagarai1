"""Configuration settings for the Shipping & Vessel Intelligence Engine."""

from pathlib import Path
from typing import Dict

# Project Base Paths
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"

# Default Dataset File Paths
DEFAULT_VESSELS_FILE = DATA_DIR / "vessels.csv"
DEFAULT_PORTS_FILE = DATA_DIR / "ports.csv"
DEFAULT_CARGO_TYPES_FILE = DATA_DIR / "cargo_types.csv"

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
# Great-circle distances cross land; estimated maritime routes often add ~15-20% buffer for canal/strait detours
MARITIME_DETOUR_FACTOR: float = 1.15
