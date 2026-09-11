"""
Voyage distance and sailing-time estimation.

Distance is a great-circle/geodesic estimate, not a commercial nautical
routing distance. Production deployment should replace it with verified
port-to-port nautical routing distances.
"""

from math import radians, sin, cos, sqrt, atan2

PORT_COORDINATES = {
    "Paradip": (20.2670, 86.6950),
    "Dhamra": (20.7819, 86.9660),
    "Vizag": (17.6868, 83.2185),
    "Gangavaram": (17.5900, 83.2700),
    "Gopalpur": (19.2670, 84.9000),
    "Haldia": (22.0257, 88.0583),
    "Sagar-Sandheads": (21.1000, 88.0000),
    "Gladstone": (-23.8427, 151.2555),
    "Newcastle": (-32.9283, 151.7817),
    "Hay Point": (-21.2900, 149.3000),
    "Dampier": (-20.6600, 116.7100),
    "Port Hedland": (-20.3100, 118.5700),
    "Mumbai": (18.9388, 72.8354),
    "Singapore": (1.2644, 103.8200),
    "Shanghai": (31.2304, 121.4737),
    "Rotterdam": (51.9244, 4.4777),
    "Dubai": (25.276987, 55.296249),
    "Los Angeles": (33.7405, -118.2719),
    "Maputo": (-25.9692, 32.5732),
    "Richards Bay": (-28.7807, 32.0386),
    "Novorossiysk": (44.7239, 37.7689),
    "Samarinda": (-0.5020, 117.1537),
}

VESSEL_SPEED_KNOTS = {
    "Capesize": 13.5,
    "Panamax": 13.0,
    "Supramax": 12.5,
}

ALIASES = {
    "paradip port": "Paradip",
    "paradeep": "Paradip",
    "dhamra port": "Dhamra",
    "visakhapatnam": "Vizag",
    "vizag port": "Vizag",
    "gangavaram port": "Gangavaram",
    "haldia port": "Haldia",
    "mumbai port": "Mumbai",
    "singapore port": "Singapore",
    "shanghai port": "Shanghai",
    "gladstone port": "Gladstone",
    "newcastle port": "Newcastle",
    "hay point port": "Hay Point",
    "maputo port": "Maputo",
    "richards bay port": "Richards Bay",
}


def normalize_port_name(name):
    value = " ".join(str(name).strip().split())
    return ALIASES.get(value.lower(), value)


def haversine_nm(lat1, lon1, lat2, lon2):
    earth_radius_km = 6371.0088

    lat1, lat2 = radians(lat1), radians(lat2)
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)

    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    return (earth_radius_km * c) / 1.852


def estimate_voyage_distance_nm(origin, destination):
    origin = normalize_port_name(origin)
    destination = normalize_port_name(destination)

    if origin not in PORT_COORDINATES:
        raise ValueError(f"Unknown origin port: {origin}")

    if destination not in PORT_COORDINATES:
        raise ValueError(f"Unknown destination port: {destination}")

    lat1, lon1 = PORT_COORDINATES[origin]
    lat2, lon2 = PORT_COORDINATES[destination]

    return round(haversine_nm(lat1, lon1, lat2, lon2), 1)


def estimate_sailing_days(distance_nm, vessel_type, speed_knots=None):
    if distance_nm <= 0:
        raise ValueError("distance_nm must be greater than zero")

    if speed_knots is None:
        if vessel_type not in VESSEL_SPEED_KNOTS:
            raise ValueError(f"Unknown vessel type: {vessel_type}")
        speed_knots = VESSEL_SPEED_KNOTS[vessel_type]

    if speed_knots <= 0:
        raise ValueError("speed_knots must be greater than zero")

    return round(distance_nm / (speed_knots * 24), 2)


def estimate_voyage(origin, destination, vessel_type, speed_knots=None):
    distance_nm = estimate_voyage_distance_nm(origin, destination)
    sailing_days = estimate_sailing_days(
        distance_nm, vessel_type, speed_knots
    )

    return {
        "origin": normalize_port_name(origin),
        "destination": normalize_port_name(destination),
        "vessel_type": vessel_type,
        "distance_nm": distance_nm,
        "speed_knots": speed_knots or VESSEL_SPEED_KNOTS[vessel_type],
        "sailing_days": sailing_days,
        "distance_method": "great_circle_geodesic_estimate",
    }


if __name__ == "__main__":
    print("Voyage estimator test")
    print("=" * 50)

    for vessel in ("Capesize", "Panamax", "Supramax"):
        result = estimate_voyage("Gladstone", "Paradip", vessel)
        print(
            f"{vessel:10s} | "
            f"{result['distance_nm']:>8} NM | "
            f"{result['speed_knots']:>5} kn | "
            f"{result['sailing_days']:>6} days"
        )
