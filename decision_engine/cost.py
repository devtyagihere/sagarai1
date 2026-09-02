"""
Cost calculation module for the freight intelligence system.
"""


def calculate_total_cost(
    freight_cost,
    charter_cost,
    port_cost,
    delay_cost,
    other_cost=0
):
    """
    Calculate the total cost of a shipment/booking.

    Parameters
    ----------
    freight_cost : float
        Cost of transporting the cargo.

    charter_cost : float
        Vessel charter-related cost.

    port_cost : float
        Port-related charges.

    delay_cost : float
        Expected cost caused by delays.

    other_cost : float, optional
        Any additional costs.

    Returns
    -------
    dict
        Detailed cost breakdown and total cost.
    """

    total_cost = (
        freight_cost
        + charter_cost
        + port_cost
        + delay_cost
        + other_cost
    )

    return {
        "freight_cost": freight_cost,
        "charter_cost": charter_cost,
        "port_cost": port_cost,
        "delay_cost": delay_cost,
        "other_cost": other_cost,
        "total_cost": total_cost
    }