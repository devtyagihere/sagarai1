# ============================================================
# VESSEL ECONOMIC OPTIMIZATION
# ============================================================
#
# Current functionality:
# 1. Vessel capacity check
# 2. Port compatibility check
# 3. Economic optimization framework
#
# IMPORTANT:
# Real vessel-specific freight rates are required for
# economic comparison.
#
# No fake freight rates are generated.
# ============================================================


# ============================================================
# VESSEL BENCHMARK PROFILES
# ============================================================

VESSEL_PROFILES = {

    "Capesize": {
        "dwt": 180000,
        "draft_m": 18.2,
        "loa_m": 290.0,
        "beam_m": 45.0,
        "cargo_capacity_factor": 0.95
    },

    "Panamax": {
        "dwt": 82500,
        "draft_m": 14.43,
        "loa_m": 229.0,
        "beam_m": 32.25,
        "cargo_capacity_factor": 0.95
    },

    "Supramax": {
        "dwt": 58328,
        "draft_m": 12.80,
        "loa_m": 189.99,
        "beam_m": 32.26,
        "cargo_capacity_factor": 0.95
    }
}


# ============================================================
# PORT COMPATIBILITY
# ============================================================

PORT_COMPATIBILITY = {

    "Dhamra": {

        "supported_vessels": {
            "Capesize": True,
            "Panamax": True,
            "Supramax": True
        },

        "cargo_types": [
            "Coal",
            "Iron Ore",
            "Steel"
        ]
    },

    "Paradip": {

        "supported_vessels": {
            "Capesize": True,
            "Panamax": True,
            "Supramax": True
        },

        "cargo_types": [
            "Coal",
            "Iron Ore",
            "Steel"
        ]
    }
}


# ============================================================
# CAPACITY CHECK
# ============================================================

def check_cargo_capacity(
    cargo_quantity,
    vessel
):

    if vessel not in VESSEL_PROFILES:

        raise ValueError(
            f"Unknown vessel class: {vessel}"
        )


    profile = VESSEL_PROFILES[vessel]


    usable_capacity = (
        profile["dwt"]
        *
        profile["cargo_capacity_factor"]
    )


    feasible = (
        cargo_quantity <= usable_capacity
    )


    return {

        "feasible":
            feasible,

        "vessel_dwt":
            profile["dwt"],

        "estimated_usable_capacity":
            usable_capacity,

        "remaining_capacity":
            max(
                usable_capacity - cargo_quantity,
                0
            ),

        "draft_m":
            profile["draft_m"],

        "loa_m":
            profile["loa_m"],

        "beam_m":
            profile["beam_m"]
    }


# ============================================================
# PORT COMPATIBILITY CHECK
# ============================================================

def check_port_compatibility(
    destination_port,
    vessel,
    cargo_type
):

    if destination_port not in PORT_COMPATIBILITY:

        return {

            "status":
                "Unavailable",

            "compatible":
                None,

            "reason":
                "Verified port compatibility data "
                "is unavailable for this port."
        }


    port = PORT_COMPATIBILITY[
        destination_port
    ]


    vessel_supported = (
        port["supported_vessels"]
        .get(
            vessel,
            False
        )
    )


    cargo_supported = (
        cargo_type
        in
        port["cargo_types"]
    )


    compatible = (
        vessel_supported
        and
        cargo_supported
    )


    if compatible:

        reason = (
            "Vessel class and cargo type are "
            "compatible with the configured port data."
        )

    elif not vessel_supported:

        reason = (
            f"{vessel} is not confirmed for "
            f"{destination_port}."
        )

    else:

        reason = (
            f"{cargo_type} is not configured as "
            f"supported cargo for {destination_port}."
        )


    return {

        "status":
            "Verified",

        "compatible":
            compatible,

        "vessel_supported":
            vessel_supported,

        "cargo_supported":
            cargo_supported,

        "reason":
            reason
    }


# ============================================================
# FREIGHT COST CALCULATOR
# ============================================================

def calculate_freight_cost(
    cargo_quantity,
    freight_rate,
    rate_unit
):

    if freight_rate is None:

        return None


    freight_rate = float(
        freight_rate
    )


    if freight_rate < 0:

        raise ValueError(
            "Freight rate cannot be negative."
        )


    # --------------------------------------------------------
    # Voyage freight
    # --------------------------------------------------------

    if rate_unit == "USD_PER_MT":

        return (
            cargo_quantity
            *
            freight_rate
        )


    # --------------------------------------------------------
    # Time charter
    #
    # We need voyage duration for this.
    # We are intentionally not guessing duration.
    # --------------------------------------------------------

    if rate_unit == "USD_PER_DAY":

        raise ValueError(
            "USD_PER_DAY requires voyage duration."
        )


    raise ValueError(
        f"Unsupported freight rate unit: {rate_unit}"
    )


# ============================================================
# ECONOMIC OPTIMIZER
# ============================================================

def optimize_vessel_economically(
    cargo_quantity,
    destination_port,
    cargo_type,
    vessel_rates=None
):

    if cargo_quantity <= 0:

        raise ValueError(
            "Cargo quantity must be greater than 0."
        )


    if not cargo_type:

        raise ValueError(
            "Cargo type is required."
        )


    # --------------------------------------------------------
    # Vessel classes
    # --------------------------------------------------------

    vessels = [

        "Supramax",

        "Panamax",

        "Capesize"
    ]


    # ========================================================
    # NO REAL VESSEL RATES AVAILABLE
    # ========================================================

    if not vessel_rates:

        comparison = {}


        for vessel in vessels:

            capacity = check_cargo_capacity(

                cargo_quantity,

                vessel
            )


            port = check_port_compatibility(

                destination_port,

                vessel,

                cargo_type
            )


            # IMPORTANT:
            # Keep the same output structure as the
            # economic branch so the test code does not
            # crash with KeyError.

            comparison[vessel] = {

                "capacity_feasible":
                    capacity["feasible"],

                "port_compatible":
                    port["compatible"],

                "economically_evaluable":
                    False,

                "freight_rate":
                    None,

                "freight_rate_unit":
                    None,

                "estimated_total_freight_cost":
                    None,

                "vessel_dwt":
                    capacity["vessel_dwt"],

                "estimated_usable_capacity":
                    capacity[
                        "estimated_usable_capacity"
                    ],

                "remaining_capacity":
                    capacity[
                        "remaining_capacity"
                    ],

                "draft_m":
                    capacity["draft_m"],

                "loa_m":
                    capacity["loa_m"],

                "beam_m":
                    capacity["beam_m"],

                "port_reason":
                    port["reason"]
            }


        return {

            "status":
                "economic_comparison_unavailable",

            "recommended_vessel":
                None,

            "recommendation_type":
                "economic",

            "reason":
                "Real vessel-specific freight rates "
                "are not available.",

            "comparison":
                comparison,

            "note":
                "No synthetic freight rates were used."
        }


    # ========================================================
    # REAL RATE ECONOMIC COMPARISON
    # ========================================================

    comparison = {}


    for vessel in vessels:

        capacity = check_cargo_capacity(

            cargo_quantity,

            vessel
        )


        port = check_port_compatibility(

            destination_port,

            vessel,

            cargo_type
        )


        rate_information = vessel_rates.get(
            vessel
        )


        # ----------------------------------------------------
        # Rate missing for this vessel
        # ----------------------------------------------------

        if rate_information is None:

            comparison[vessel] = {

                "capacity_feasible":
                    capacity["feasible"],

                "port_compatible":
                    port["compatible"],

                "economically_evaluable":
                    False,

                "freight_rate":
                    None,

                "freight_rate_unit":
                    None,

                "estimated_total_freight_cost":
                    None,

                "vessel_dwt":
                    capacity["vessel_dwt"],

                "estimated_usable_capacity":
                    capacity[
                        "estimated_usable_capacity"
                    ],

                "remaining_capacity":
                    capacity[
                        "remaining_capacity"
                    ],

                "draft_m":
                    capacity["draft_m"],

                "loa_m":
                    capacity["loa_m"],

                "beam_m":
                    capacity["beam_m"],

                "port_reason":
                    port["reason"]
            }

            continue


        # ----------------------------------------------------
        # Read rate
        # ----------------------------------------------------

        if isinstance(
            rate_information,
            dict
        ):

            freight_rate = (
                rate_information.get(
                    "rate"
                )
            )

            if freight_rate is None:

                freight_rate = (
                    rate_information.get(
                        "freight_rate"
                    )
                )


            rate_unit = (
                rate_information.get(
                    "unit"
                )
            )

            if rate_unit is None:

                rate_unit = (
                    rate_information.get(
                        "rate_unit"
                    )
                )

        else:

            raise ValueError(
                f"Invalid rate format for {vessel}"
            )


        # ----------------------------------------------------
        # Determine whether comparison is possible
        # ----------------------------------------------------

        economically_evaluable = (

            capacity["feasible"]

            and

            port["compatible"] is True

            and

            freight_rate is not None

            and

            rate_unit is not None
        )


        total_cost = None


        if economically_evaluable:

            total_cost = calculate_freight_cost(

                cargo_quantity,

                freight_rate,

                rate_unit
            )


        comparison[vessel] = {

            "capacity_feasible":
                capacity["feasible"],

            "port_compatible":
                port["compatible"],

            "economically_evaluable":
                economically_evaluable,

            "freight_rate":
                freight_rate,

            "freight_rate_unit":
                rate_unit,

            "estimated_total_freight_cost":
                total_cost,

            "vessel_dwt":
                capacity["vessel_dwt"],

            "estimated_usable_capacity":
                capacity[
                    "estimated_usable_capacity"
                ],

            "remaining_capacity":
                capacity[
                    "remaining_capacity"
                ],

            "draft_m":
                capacity["draft_m"],

            "loa_m":
                capacity["loa_m"],

            "beam_m":
                capacity["beam_m"],

            "port_reason":
                port["reason"]
        }


    # ========================================================
    # FIND ECONOMICALLY FEASIBLE VESSELS
    # ========================================================

    feasible_vessels = [

        vessel

        for vessel in vessels

        if comparison[vessel][
            "economically_evaluable"
        ]

        and

        comparison[vessel][
            "estimated_total_freight_cost"
        ] is not None
    ]


    # ========================================================
    # NO COMPLETE ECONOMIC DATA
    # ========================================================

    if not feasible_vessels:

        return {

            "status":
                "economic_comparison_unavailable",

            "recommended_vessel":
                None,

            "recommendation_type":
                "economic",

            "reason":
                "No vessel has sufficient real "
                "vessel-specific freight-rate data "
                "for an economic comparison.",

            "comparison":
                comparison,

            "note":
                "No synthetic freight rates were used."
        }


    # ========================================================
    # CHEAPEST FEASIBLE VESSEL
    # ========================================================

    recommended_vessel = min(

        feasible_vessels,

        key=lambda vessel:

            comparison[vessel][
                "estimated_total_freight_cost"
            ]
    )


    recommended_cost = comparison[
        recommended_vessel
    ][
        "estimated_total_freight_cost"
    ]


    return {

        "status":
            "success",

        "recommended_vessel":
            recommended_vessel,

        "recommendation_type":
            "economic",

        "recommended_total_freight_cost":
            recommended_cost,

        "reason":
            (
                f"{recommended_vessel} has the "
                "lowest estimated total freight "
                "cost among feasible vessels "
                "using the supplied real "
                "vessel-specific rates."
            ),

        "comparison":
            comparison
    }


# ============================================================
# MAIN FUNCTION
# ============================================================

def optimize_vessel(
    cargo_quantity,
    destination_port,
    cargo_type,
    vessel_rates=None
):

    return optimize_vessel_economically(

        cargo_quantity=
            cargo_quantity,

        destination_port=
            destination_port,

        cargo_type=
            cargo_type,

        vessel_rates=
            vessel_rates
    )


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    print("=" * 70)

    print(
        "VESSEL ECONOMIC OPTIMIZATION TEST"
    )

    print("=" * 70)


    cargo_quantity = 50000

    cargo_type = "Coal"

    destination_port = "Dhamra"


    # --------------------------------------------------------
    # NO FAKE RATES
    # --------------------------------------------------------

    vessel_rates = None


    result = optimize_vessel_economically(

        cargo_quantity=
            cargo_quantity,

        destination_port=
            destination_port,

        cargo_type=
            cargo_type,

        vessel_rates=
            vessel_rates
    )


    print(
        "\nCargo:",
        cargo_quantity,
        "MT"
    )


    print(
        "Cargo Type:",
        cargo_type
    )


    print(
        "Destination:",
        destination_port
    )


    print(
        "\nEconomic Recommendation:",
        result[
            "recommended_vessel"
        ]
    )


    print(
        "Status:",
        result["status"]
    )


    print(
        "Reason:",
        result["reason"]
    )


    print(
        "\nVESSEL COMPARISON"
    )

    print("-" * 70)


    for vessel, data in (
        result["comparison"].items()
    ):

        print(
            f"\n{vessel}"
        )


        print(
            "  Capacity feasible:",
            data[
                "capacity_feasible"
            ]
        )


        print(
            "  Port compatible:",
            data[
                "port_compatible"
            ]
        )


        print(
            "  Economic evaluation:",
            data[
                "economically_evaluable"
            ]
        )


        print(
            "  Freight rate:",
            data[
                "freight_rate"
            ]
        )


        print(
            "  Total freight cost:",
            data[
                "estimated_total_freight_cost"
            ]
        )


        print(
            "  DWT:",
            data[
                "vessel_dwt"
            ]
        )


        print(
            "  Usable capacity:",
            data[
                "estimated_usable_capacity"
            ],
            "MT"
        )


        print(
            "  Remaining capacity:",
            data[
                "remaining_capacity"
            ],
            "MT"
        )


        print(
            "  Draft:",
            data[
                "draft_m"
            ],
            "m"
        )


        print(
            "  LOA:",
            data[
                "loa_m"
            ],
            "m"
        )


        print(
            "  Beam:",
            data[
                "beam_m"
            ],
            "m"
        )


        print(
            "  Port reason:",
            data[
                "port_reason"
            ]
        )