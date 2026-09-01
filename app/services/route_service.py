"""Route and voyage duration intelligence service."""

from typing import Optional
from geopy.distance import geodesic

from app.models.port import Port
from app.models.request import DistanceEstimate, RouteEstimate
from app.models.vessel import Vessel
from config import DEFAULT_VESSEL_SPEED_KNOTS, HOURS_PER_DAY, NAUTICAL_MILE_KM


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
        Compute geodesic distance in nautical miles and estimate voyage duration.

        NOTE: This is clearly labeled as a GEOGRAPHIC ESTIMATE (great circle).
        Actual maritime routes via sea lanes (e.g. Malacca, Suez, Cape) are longer.
        """
        origin_coords = (origin_port.latitude, origin_port.longitude)
        dest_coords = (destination_port.latitude, destination_port.longitude)

        # Geodesic distance in kilometers converted to Nautical Miles
        distance_km = geodesic(origin_coords, dest_coords).kilometers
        distance_nm = round(distance_km / NAUTICAL_MILE_KM, 1)

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
                method="geographic_estimate",
            ),
            estimated_duration_days=duration_days,
            deadline_met=deadline_met,
            warning=(
                "Geographic distance is an idealized great-circle estimate. "
                "Actual maritime route and duration may differ significantly due to "
                "navigational straits, TSS routing, canal transit, and weather conditions."
            ),
        )
