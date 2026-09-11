"""Cargo intelligence service for validating cargo-vessel compatibility."""

from typing import Any, Dict, Optional
from app.models.vessel import Vessel
from app.services.data_loader import DataLoader, default_data_loader


class CargoService:
    """Service evaluating cargo physical properties and vessel handling constraints."""

    def __init__(self, data_loader: Optional[DataLoader] = None):
        self.data_loader = data_loader or default_data_loader

    def check_compatibility(self, cargo_type: str, vessel: Vessel) -> Dict[str, Any]:
        """
        Check if a given cargo type can be safely transported by the specified vessel class.

        Handles:
        - Dry bulk standard commodities (iron ore, coal, grain, bauxite)
        - Differentiated steel forms (steel coils, steel plates, steel products)
        - Incompatible liquid or gas cargoes
        """
        cleaned_cargo = cargo_type.strip().lower()
        cargo_info = self.data_loader.get_cargo_info(cleaned_cargo)

        # Handle generic steel inquiry
        if cleaned_cargo == "steel":
            return {
                "compatible": False,
                "reason": "Ambiguous cargo 'steel'. Specify exact steel form (steel_coils, steel_plates, or steel_products).",
                "requires_geared": True,
                "stowage_factor": None,
                "category": "break_bulk",
            }

        # Check if cargo is recognized in database
        if not cargo_info:
            # Fallback: check if cargo is directly listed in vessel's supported cargo list
            if cleaned_cargo in [c.lower() for c in vessel.supported_cargo]:
                return {
                    "compatible": True,
                    "reason": f"Cargo '{cargo_type}' is supported by {vessel.vessel_class} specifications.",
                    "requires_geared": False,
                    "stowage_factor": 1.0,
                    "category": "dry_bulk",
                }
            return {
                "compatible": False,
                "reason": f"Unknown or unsupported cargo type '{cargo_type}'.",
                "requires_geared": False,
                "stowage_factor": None,
                "category": "unknown",
            }

        # Liquid bulk or hazardous incompatible cargoes
        if cargo_info["category"] in ("liquid_bulk", "gas_tanker"):
            return {
                "compatible": False,
                "reason": f"Liquid/gas cargo '{cargo_type}' is incompatible with dry bulk vessel class {vessel.vessel_class}.",
                "requires_geared": False,
                "stowage_factor": cargo_info["stowage_factor_m3_per_tonne"],
                "category": cargo_info["category"],
            }

        # Specific steel product handling
        if cargo_info["category"] == "break_bulk":
            if cargo_info["requires_geared_vessel"] and vessel.vessel_class in ("Panamax", "Capesize"):
                return {
                    "compatible": False,
                    "reason": f"Break-bulk steel cargo '{cargo_type}' requires geared vessels with onboard cranes. {vessel.vessel_class} bulkers are typically gearless.",
                    "requires_geared": True,
                    "stowage_factor": cargo_info["stowage_factor_m3_per_tonne"],
                    "category": "break_bulk",
                }

        # Check vessel's supported cargo list
        vessel_cargos = [c.lower() for c in vessel.supported_cargo]
        if cleaned_cargo in vessel_cargos:
            return {
                "compatible": True,
                "reason": f"Cargo '{cargo_type}' is fully supported by {vessel.vessel_class} configuration.",
                "requires_geared": cargo_info.get("requires_geared_vessel", False),
                "stowage_factor": cargo_info.get("stowage_factor_m3_per_tonne", 1.0),
                "category": cargo_info["category"],
            }

        # Check allowed vessel classes if specified in cargo info
        allowed_classes = [ac.lower() for ac in cargo_info.get("allowed_vessel_classes", [])]
        if vessel.vessel_class.lower() in allowed_classes:
            return {
                "compatible": True,
                "reason": f"Cargo '{cargo_type}' is permitted for {vessel.vessel_class}.",
                "requires_geared": cargo_info.get("requires_geared_vessel", False),
                "stowage_factor": cargo_info.get("stowage_factor_m3_per_tonne", 1.0),
                "category": cargo_info["category"],
            }

        return {
            "compatible": False,
            "reason": f"Cargo type '{cargo_type}' is not supported by {vessel.vessel_class} vessel configuration.",
            "requires_geared": cargo_info.get("requires_geared_vessel", False),
            "stowage_factor": cargo_info.get("stowage_factor_m3_per_tonne", 1.0),
            "category": cargo_info["category"],
        }
