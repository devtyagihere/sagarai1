"""
Port Operations Service — operational congestion layer on top of physical constraints.

DISTINCTION:
  Physical feasibility  = can the vessel physically enter the port? (draft/LOA/beam)
                          → handled by FeasibilityEngine (unchanged)
  Operational congestion= how long will the vessel wait once it arrives?
                          → handled by THIS service

CONGESTION FORMULA (documented):
  congestion_score =
      min(vessels_waiting / max(vessels_working, 1), 1.0) × 40   [berth saturation]
    + min(average_waiting_days / 5.0, 1.0)                × 40   [anchorage pressure]
    + operational_variability_factor                       × 20   [random/seasonal noise]
  clamped to [0, 100]

  Classification:
    0  – 25  → LOW
    25 – 45  → LOW-MODERATE
    45 – 65  → MODERATE
    65 – 80  → HIGH
    80 – 100 → VERY HIGH

DATA: SYNTHETIC — clearly labeled throughout.
      Replace CSV with live API (e.g. MarineTraffic, PortWatch) for production.
"""

from pathlib import Path
from typing import Dict, Optional
import pandas as pd

from app.models.operations import PortCongestion, PortOperationsResult
from config import (
    DEFAULT_PORT_OPERATIONS_FILE,
    CONGESTION_LOW_THRESHOLD,
    CONGESTION_LOW_MODERATE_THRESHOLD,
    CONGESTION_MODERATE_THRESHOLD,
    CONGESTION_HIGH_THRESHOLD,
    MARKET_DATA_SOURCE,
)

_FORMULA = (
    "score = min(waiting/working,1)×40 + min(avg_wait_days/5,1)×40 + variability×20; "
    "clamped [0,100]"
)

def _classify(score: float) -> str:
    if score < CONGESTION_LOW_THRESHOLD:           return "LOW"
    if score < CONGESTION_LOW_MODERATE_THRESHOLD:  return "LOW-MODERATE"
    if score < CONGESTION_MODERATE_THRESHOLD:      return "MODERATE"
    if score < CONGESTION_HIGH_THRESHOLD:          return "HIGH"
    return "VERY HIGH"

def _worst(a: str, b: str) -> str:
    order = ["LOW","LOW-MODERATE","MODERATE","HIGH","VERY HIGH"]
    ai = order.index(a) if a in order else 0
    bi = order.index(b) if b in order else 0
    return order[max(ai, bi)]


class PortOperationsService:
    """
    Loads port operational data and computes congestion scores.

    Physical port constraints (draft/LOA/beam) remain the responsibility of
    FeasibilityEngine. This service ONLY deals with operational throughput.
    """

    def __init__(self, path: Optional[Path] = None):
        self._path = path or DEFAULT_PORT_OPERATIONS_FILE
        self._data: Optional[Dict[str, dict]] = None

    def _load(self) -> None:
        if self._data is not None:
            return
        if not self._path.exists():
            raise FileNotFoundError(f"Port operations data not found: {self._path}")
        df = pd.read_csv(self._path)
        self._data = {
            str(row["port_name"]).strip().lower(): row.to_dict()
            for _, row in df.iterrows()
        }

    def get_port_congestion(self, port_name: str) -> Optional[PortCongestion]:
        """
        Return congestion metrics for a named port.
        Returns None if the port is not in the operations dataset.
        """
        self._load()
        key = port_name.strip().lower()
        row = self._data.get(key)
        if row is None:
            return None

        score = float(row.get("congestion_score", 0.0))
        return PortCongestion(
            port_name=str(row["port_name"]),
            vessels_working=int(row.get("vessels_working", 0)),
            vessels_waiting=int(row.get("vessels_waiting", 0)),
            congestion_score=round(score, 1),
            congestion_level=_classify(score),
            average_waiting_days=round(float(row.get("average_waiting_days", 0.0)), 1),
            congestion_forecast_7d=round(float(row.get("congestion_forecast_7d", score)), 1),
            congestion_forecast_15d=round(float(row.get("congestion_forecast_15d", score)), 1),
            congestion_forecast_30d=round(float(row.get("congestion_forecast_30d", score)), 1),
            data_source=str(row.get("data_source", MARKET_DATA_SOURCE)),
            formula_used=_FORMULA,
        )

    def get_port_operations_result(
        self, origin_name: str, destination_name: str
    ) -> PortOperationsResult:
        """
        Return combined congestion for origin and destination.
        combined_delay_risk is the worst-case of the two.
        """
        self._load()
        origin_cong = self.get_port_congestion(origin_name)
        dest_cong   = self.get_port_congestion(destination_name)

        ol = origin_cong.congestion_level if origin_cong else "LOW"
        dl = dest_cong.congestion_level   if dest_cong   else "LOW"
        combined = _worst(ol, dl)

        return PortOperationsResult(
            origin=origin_cong,
            destination=dest_cong,
            combined_delay_risk=combined,
            data_source=MARKET_DATA_SOURCE,
        )

    def all_ports(self):
        """Return raw dict of all loaded port operational data."""
        self._load()
        return list(self._data.values())


default_port_ops_service = PortOperationsService()
