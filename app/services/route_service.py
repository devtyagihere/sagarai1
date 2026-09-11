"""Route and voyage duration intelligence service."""

from typing import Optional
from geopy.distance import geodesic

from app.models.port import Port
from app.models.request import DistanceEstimate, RouteEstimate
from app.models.vessel import Vessel
from config import DEFAULT_VESSEL_SPEED_KNOTS, HOURS_PER_DAY, MARITIME_DETOUR_FACTOR, NAUTICAL_MILE_KM


class RouteService:
    """Calculates geographic distances and estimates voyage transit times."""

    def __init__(self, default_speed_knots: float = DEFAULT_VESSEL_SPEED_KNOTS):
        self.default_speed_knots = default_speed_knots

    def estimate_route(
        self,
        origin_port: Port,
        destination_port: Port,
        vessel: Optional[Vessel] = None,
        deadline_days: Optional[float] = None,
    ) -> RouteEstimate:
        """
        Compute sea-lane adjusted distance in nautical miles and estimate voyage duration.

        BUG 4 FIX: MARITIME_DETOUR_FACTOR (1.15) is now applied to the raw geodesic distance.
        Pure great-circle distances underestimate real maritime routes by 15-20% because they
        cross land. The factor accounts for navigational detours through straits, canals, and TSS.
        """
        origin_coords = (origin_port.latitude, origin_port.longitude)
        dest_coords = (destination_port.latitude, destination_port.longitude)

        # Geodesic distance in kilometers converted to Nautical Miles
        distance_km = geodesic(origin_coords, dest_coords).kilometers
        distance_nm_geodesic = distance_km / NAUTICAL_MILE_KM

        # BUG 4 FIX: Apply maritime detour factor for realistic sea-lane estimate
        distance_nm = round(distance_nm_geodesic * MARITIME_DETOUR_FACTOR, 1)

        # Determine vessel cruising speed
        speed_knots = vessel.avg_speed_knots if vessel else self.default_speed_knots
        if speed_knots <= 0:
            speed_knots = self.default_speed_knots

        # Transit hours & days
        transit_hours = distance_nm / speed_knots
        duration_days = round(transit_hours / HOURS_PER_DAY, 1)

        # Deadline comparison
        deadline_met: Optional[bool] = None
        if deadline_days is not None:
            deadline_met = duration_days <= deadline_days

        return RouteEstimate(
            origin_port=origin_port.port_name,
            destination_port=destination_port.port_name,
            distance_estimate=DistanceEstimate(
                value=distance_nm,
                unit="nautical_miles",
                method="sea_lane_estimate",
            ),
            estimated_duration_days=duration_days,
            deadline_met=deadline_met,
            warning=(
                f"Sea-lane adjusted distance (geodesic x {MARITIME_DETOUR_FACTOR} detour factor). "
                "Actual maritime route and duration may still differ due to "
                "navigational straits, TSS routing, canal transit, and weather conditions."
            ),
        )
