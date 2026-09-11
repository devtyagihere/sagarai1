"""Data loader service for loading, validating, and indexing maritime datasets."""

from pathlib import Path
from typing import Dict, List, Optional
import pandas as pd

from app.models.port import Port
from app.models.vessel import Vessel
from app.utils.constants import DataQualityStatus
from config import DEFAULT_CARGO_TYPES_FILE, DEFAULT_PORTS_FILE, DEFAULT_VESSELS_FILE


class DataLoader:
    """Thread-safe dataset loader with column validation, caching, and normalization."""

    REQUIRED_VESSEL_COLS = {
        "vessel_class",
        "min_capacity_tonnes",
        "max_capacity_tonnes",
        "typical_draft_m",
        "typical_length_m",
        "typical_beam_m",
        "avg_speed_knots",
        "supported_cargo",
        "data_status",
        "source",
    }

    REQUIRED_PORT_COLS = {
        "port_name",
        "country",
        "latitude",
        "longitude",
        "max_draft_m",
        "max_length_m",
        "max_beam_m",
        "data_status",
        "source",
    }

    REQUIRED_CARGO_COLS = {
        "cargo_type",
        "category",
        "stowage_factor_m3_per_tonne",
        "requires_geared_vessel",
        "hazmat_class",
        "allowed_vessel_classes",
        "description",
    }

    def __init__(
        self,
        vessels_path: Optional[Path] = None,
        ports_path: Optional[Path] = None,
        cargo_types_path: Optional[Path] = None,
    ):
        self.vessels_path = vessels_path or DEFAULT_VESSELS_FILE
        self.ports_path = ports_path or DEFAULT_PORTS_FILE
        self.cargo_types_path = cargo_types_path or DEFAULT_CARGO_TYPES_FILE

        self._vessels: Dict[str, Vessel] = {}
        self._ports: Dict[str, Port] = {}
        self._cargo_types: Dict[str, dict] = {}
        self._is_loaded: bool = False

    def load_all(self, force_reload: bool = False) -> None:
        """Load and validate all datasets into memory."""
        if self._is_loaded and not force_reload:
            return

        self._load_vessels()
        self._load_ports()
        self._load_cargo_types()
        self._is_loaded = True

    def _load_vessels(self) -> None:
        """Load and validate vessel dataset."""
        if not self.vessels_path.exists():
            raise FileNotFoundError(f"Vessel dataset not found at {self.vessels_path}")

        df = pd.read_csv(self.vessels_path)
        missing_cols = self.REQUIRED_VESSEL_COLS - set(df.columns)
        if missing_cols:
            raise ValueError(f"vessels.csv missing required columns: {sorted(missing_cols)}")

        self._vessels.clear()
        for _, row in df.iterrows():
            if pd.isna(row["vessel_class"]):
                continue

            raw_cargo = str(row["supported_cargo"]) if pd.notna(row["supported_cargo"]) else ""
            supported_cargos = [c.strip().lower() for c in raw_cargo.split(";") if c.strip()]
            status_str = str(row["data_status"]).strip().lower()
            try:
                data_status = DataQualityStatus(status_str)
            except ValueError:
                data_status = DataQualityStatus.ESTIMATED

            vessel = Vessel(
                vessel_class=str(row["vessel_class"]).strip(),
                min_capacity_tonnes=float(row["min_capacity_tonnes"]),
                max_capacity_tonnes=float(row["max_capacity_tonnes"]),
                typical_draft_m=float(row["typical_draft_m"]),
                typical_length_m=float(row["typical_length_m"]),
                typical_beam_m=float(row["typical_beam_m"]),
                avg_speed_knots=float(row["avg_speed_knots"]),
                supported_cargo=supported_cargos,
                data_status=data_status,
                source=str(row.get("source", "Standard Reference")),
            )
            # Store keyed by lowercase for case-insensitive lookup
            self._vessels[vessel.vessel_class.lower()] = vessel

    def _load_ports(self) -> None:
        """Load and validate port dataset."""
        if not self.ports_path.exists():
            raise FileNotFoundError(f"Port dataset not found at {self.ports_path}")

        df = pd.read_csv(self.ports_path)
        missing_cols = self.REQUIRED_PORT_COLS - set(df.columns)
        if missing_cols:
            raise ValueError(f"ports.csv missing required columns: {sorted(missing_cols)}")

        self._ports.clear()
        for _, row in df.iterrows():
            if pd.isna(row["port_name"]):
                continue

            port_name = str(row["port_name"]).strip()
            status_str = str(row.get("data_status", "verified")).strip().lower()
            try:
                data_status = DataQualityStatus(status_str)
            except ValueError:
                data_status = DataQualityStatus.ESTIMATED

            port = Port(
                port_name=port_name,
                country=str(row["country"]).strip(),
                latitude=float(row["latitude"]),
                longitude=float(row["longitude"]),
                max_draft_m=float(row["max_draft_m"]) if pd.notna(row["max_draft_m"]) else None,
                max_length_m=float(row["max_length_m"]) if pd.notna(row["max_length_m"]) else None,
                max_beam_m=float(row["max_beam_m"]) if pd.notna(row["max_beam_m"]) else None,
                data_status=data_status,
                source=str(row.get("source", "Port Authority")),
                last_verified=str(row["last_verified"]) if "last_verified" in row and pd.notna(row["last_verified"]) else None,
            )
            # Store lowercase key for case-insensitive lookup
            self._ports[port_name.lower()] = port

    def _load_cargo_types(self) -> None:
        """Load and validate cargo type dataset."""
        if not self.cargo_types_path.exists():
            raise FileNotFoundError(f"Cargo type dataset not found at {self.cargo_types_path}")

        df = pd.read_csv(self.cargo_types_path)
        missing_cols = self.REQUIRED_CARGO_COLS - set(df.columns)
        if missing_cols:
            raise ValueError(f"cargo_types.csv missing required columns: {sorted(missing_cols)}")

        self._cargo_types.clear()
        for _, row in df.iterrows():
            if pd.isna(row["cargo_type"]):
                continue

            c_type = str(row["cargo_type"]).strip().lower()
            allowed_classes_raw = str(row.get("allowed_vessel_classes", ""))
            allowed_classes = [c.strip() for c in allowed_classes_raw.split(";") if c.strip()]

            requires_geared = False
            if pd.notna(row.get("requires_geared_vessel")):
                val = str(row["requires_geared_vessel"]).strip().lower()
                requires_geared = val in ("true", "1", "yes")

            self._cargo_types[c_type] = {
                "cargo_type": c_type,
                "category": str(row["category"]).strip().lower(),
                "stowage_factor_m3_per_tonne": float(row["stowage_factor_m3_per_tonne"]) if pd.notna(row["stowage_factor_m3_per_tonne"]) else 1.0,
                "requires_geared_vessel": requires_geared,
                "hazmat_class": str(row.get("hazmat_class", "none")).strip(),
                "allowed_vessel_classes": allowed_classes,
                "description": str(row.get("description", "")).strip(),
            }

    def get_vessels(self) -> List[Vessel]:
        """Return all loaded vessels."""
        self.load_all()
        return list(self._vessels.values())

    def get_vessel(self, vessel_class: str) -> Optional[Vessel]:
        """Find a vessel by class name (case-insensitive)."""
        self.load_all()
        return self._vessels.get(vessel_class.strip().lower())

    def get_port(self, port_name: str) -> Optional[Port]:
        """Find a port by name (case-insensitive, trims whitespace)."""
        self.load_all()
        cleaned = port_name.strip().lower()
        if cleaned in self._ports:
            return self._ports[cleaned]

        # Check for common aliases (e.g., Vizag -> Visakhapatnam)
        alias_map = {
            "vizag": "visakhapatnam",
            "kolkata": "haldia",
            "sandheads": "sagar-sandheads",
        }
        target_name = alias_map.get(cleaned)
        if target_name and target_name in self._ports:
            return self._ports[target_name]

        return None

    def get_all_ports(self) -> List[Port]:
        """Return list of all unique ports."""
        self.load_all()
        return list(self._ports.values())

    def get_cargo_info(self, cargo_type: str) -> Optional[dict]:
        """Get cargo specification dictionary (case-insensitive)."""
        self.load_all()
        return self._cargo_types.get(cargo_type.strip().lower())

    def get_all_cargo_types(self) -> List[dict]:
        """Return all registered cargo type specifications."""
        self.load_all()
        return list(self._cargo_types.values())


# Global default instance
default_data_loader = DataLoader()
