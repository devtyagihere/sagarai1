# ============================================================
# VESSEL ECONOMIC OPTIMIZATION
# ============================================================
#
# Features:
# 1. Vessel capacity check
# 2. Port compatibility check
# 3. Real KOBC vessel benchmark rates
# 4. Voyage distance estimation
# 5. Sailing-time estimation
# 6. Economic freight comparison
# 7. Cheapest feasible vessel recommendation
#
# IMPORTANT:
# KOBC rates are vessel-class market benchmark rates.
# They are NOT route-specific voyage rates.
#
# Voyage distance is currently a great-circle estimate.
# Production version should replace this with verified
# maritime routing distance.
# ============================================================


# ============================================================
# IMPORTS
# ============================================================

from src.voyage_estimator import estimate_voyage
from src.vessel_rate_forecasting_model import forecast_vessel_rates


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
#
# NOTE:
# These are currently configured compatibility rules.
# Actual berth compatibility can depend on draft, tide,
# berth, loading condition and operational restrictions.
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

    utilization_percent = (
        cargo_quantity / usable_capacity
    ) * 100

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

        "capacity_utilization_percent":
            utilization_percent,

        "draft_m":
            profile["draft_m"],

        "loa_m":
            profile["loa_m"],

        "beam_m":
            profile["beam_m"]
    }


# ============================================================
# CAPACITY UTILIZATION ASSESSMENT
# ============================================================

def assess_capacity_utilization(utilization_percent):
    """
    Classify cargo utilization for decision support.

    This is an explanatory efficiency indicator only.
    It does NOT override the primary economic comparison.
    """

    if utilization_percent >= 80:
        return "Highly efficient"

    if utilization_percent >= 60:
        return "Efficient"

    if utilization_percent >= 40:
        return "Moderate"

    return "Under-utilized"


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
# REAL KOBC RATE LOADER
# ============================================================

def load_current_kobc_rates():

    market = forecast_vessel_rates()

    current = market.get(
        "current",
        {}
    )

    rates = {}

    for vessel in [
        "Capesize",
        "Panamax",
        "Supramax"
    ]:

        item = current.get(
            vessel
        )

        if item is None:
            continue

        value = item.get(
            "value"
        )

        if value is None:
            continue

        rates[vessel] = {

            "rate":
                float(value),

            "unit":
                "USD_PER_DAY",

            "source":
                "KOBC",

            "date":
                item.get("date"),

            "route_specific":
                False
        }

    if not rates:

        raise RuntimeError(
            "No real KOBC vessel rates are available."
        )

    return rates


# ============================================================
# FREIGHT COST CALCULATOR
# ============================================================

def calculate_freight_cost(
    cargo_quantity,
    freight_rate,
    rate_unit,
    voyage_days=None
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
    # VOYAGE RATE
    # --------------------------------------------------------

    if rate_unit == "USD_PER_MT":

        return (
            cargo_quantity
            *
            freight_rate
        )

    # --------------------------------------------------------
    # TIME-CHARTER / DAILY RATE
    # --------------------------------------------------------

    if rate_unit == "USD_PER_DAY":

        if voyage_days is None:

            raise ValueError(
                "USD_PER_DAY requires voyage duration."
            )

        if voyage_days <= 0:

            raise ValueError(
                "Voyage duration must be greater than 0."
            )

        return (
            freight_rate
            *
            voyage_days
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
    vessel_rates=None,
    origin=None
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

    # --------------------------------------------------------
    # Load real KOBC rates automatically
    # --------------------------------------------------------

    rate_loading_error = None

    if vessel_rates is None:

        try:

            vessel_rates = (
                load_current_kobc_rates()
            )

        except Exception as exc:

            rate_loading_error = str(
                exc
            )

            vessel_rates = None

    # --------------------------------------------------------
    # No rates available
    # --------------------------------------------------------

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

                "freight_rate_source":
                    None,

                "freight_rate_date":
                    None,

                "voyage_distance_nm":
                    None,

                "voyage_days":
                    None,

                "estimated_total_freight_cost":
                    None,

                "estimated_freight_cost_per_mt":
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

                "capacity_utilization_percent":
                    capacity[
                        "capacity_utilization_percent"
                    ],

                "utilization_assessment":
                    assess_capacity_utilization(
                        capacity[
                            "capacity_utilization_percent"
                        ]
                    ),

                "draft_m":
                    capacity["draft_m"],

                "loa_m":
                    capacity["loa_m"],

                "beam_m":
                    capacity["beam_m"],

                "port_reason":
                    port["reason"]
            }

        reason = (
            "Real vessel-specific freight rates "
            "are not available."
        )

        if rate_loading_error:

            reason += (
                f" Rate loading error: "
                f"{rate_loading_error}"
            )

        return {

            "status":
                "economic_comparison_unavailable",

            "recommended_vessel":
                None,

            "recommendation_type":
                "economic",

            "reason":
                reason,

            "comparison":
                comparison,

            "origin":
                origin,

            "destination":
                destination_port,

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

        rate_information = (
            vessel_rates.get(
                vessel
            )
        )

        # ----------------------------------------------------
        # Missing rate
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

                "freight_rate_source":
                    None,

                "freight_rate_date":
                    None,

                "voyage_distance_nm":
                    None,

                "voyage_days":
                    None,

                "estimated_total_freight_cost":
                    None,

                "estimated_freight_cost_per_mt":
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

            rate_source = (
                rate_information.get(
                    "source"
                )
            )

            rate_date = (
                rate_information.get(
                    "date"
                )
            )

        else:

            raise ValueError(
                f"Invalid rate format for {vessel}"
            )

        # ----------------------------------------------------
        # Voyage estimation
        # ----------------------------------------------------

        voyage = None

        voyage_distance_nm = None
        voyage_days = None
        voyage_error = None

        if origin:

            try:

                voyage = estimate_voyage(
                    origin=origin,
                    destination=destination_port,
                    vessel_type=vessel
                )

                voyage_distance_nm = (
                    voyage["distance_nm"]
                )

                voyage_days = (
                    voyage["sailing_days"]
                )

            except Exception as exc:

                voyage_error = str(
                    exc
                )

        # ----------------------------------------------------
        # Economic evaluation
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

        # ----------------------------------------------------
        # USD/day requires voyage duration
        # ----------------------------------------------------

        if (

            economically_evaluable

            and

            rate_unit == "USD_PER_DAY"

            and

            voyage_days is None

        ):

            economically_evaluable = False

        total_cost = None

        cost_per_mt = None

        if economically_evaluable:

            total_cost = (
                calculate_freight_cost(
                    cargo_quantity=
                        cargo_quantity,

                    freight_rate=
                        freight_rate,

                    rate_unit=
                        rate_unit,

                    voyage_days=
                        voyage_days
                )
            )

            cost_per_mt = (
                total_cost
                /
                cargo_quantity
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

            "freight_rate_source":
                rate_source,

            "freight_rate_date":
                rate_date,

            "voyage_distance_nm":
                voyage_distance_nm,

            "voyage_days":
                voyage_days,

            "voyage_error":
                voyage_error,

            "estimated_total_freight_cost":
                total_cost,

            "estimated_freight_cost_per_mt":
                cost_per_mt,

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

            "capacity_utilization_percent":
                capacity[
                    "capacity_utilization_percent"
                ],

            "utilization_assessment":
                assess_capacity_utilization(
                    capacity[
                        "capacity_utilization_percent"
                    ]
                ),

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
                (
                    "No vessel has sufficient real "
                    "vessel-specific freight-rate and "
                    "voyage-duration data for an "
                    "economic comparison."
                ),

            "comparison":
                comparison,

            "origin":
                origin,

            "destination":
                destination_port,

            "note":
                (
                    "KOBC rates are vessel-class "
                    "benchmarks. No synthetic "
                    "freight rates were used."
                )
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

    recommended_cost = (
        comparison[
            recommended_vessel
        ][
            "estimated_total_freight_cost"
        ]
    )

    recommended_cost_per_mt = (
        comparison[
            recommended_vessel
        ][
            "estimated_freight_cost_per_mt"
        ]
    )

    return {

        "status":
            "success",

        "recommended_vessel":
            recommended_vessel,

        "recommendation_type":
            "economic",

        "recommended_total_freight_cost":
            recommended_cost,

        "recommended_freight_cost_per_mt":
            recommended_cost_per_mt,

        "recommended_capacity_utilization_percent":
            comparison[recommended_vessel][
                "capacity_utilization_percent"
            ],

        "recommended_utilization_assessment":
            comparison[recommended_vessel][
                "utilization_assessment"
            ],

        "reason":
            (
                f"{recommended_vessel} has the "
                "lowest estimated total freight "
                "cost among feasible vessels "
                "using the supplied real "
                "vessel-class benchmark rates "
                "and estimated voyage duration. "
                f"Its cargo capacity utilization is "
                f"{comparison[recommended_vessel]['capacity_utilization_percent']:.2f}% "
                f"({comparison[recommended_vessel]['utilization_assessment']})."
            ),

        "origin":
            origin,

        "destination":
            destination_port,

        "comparison":
            comparison,

        "note":
            (
                "KOBC rates are vessel-class "
                "market benchmarks and are not "
                "route-specific voyage rates."
            )
    }


# ============================================================
# FORECAST-BASED VESSEL OPTIMIZATION
# ============================================================

def optimize_vessel_with_rate_forecast(
    cargo_quantity,
    destination_port,
    cargo_type,
    origin=None
):
    """
    Compare vessel economics using the trained KOBC vessel-rate
    forecasting model for each supported market-observation horizon.

    IMPORTANT:
        The KOBC forecasts are vessel-class benchmark rates in
        USD/day, not route-specific voyage freight rates.
        Horizons are KOBC market observations, not guaranteed
        calendar-day intervals.

    No synthetic vessel rates are created here.
    """

    market = forecast_vessel_rates()

    forecast_map = market.get("forecast", {})

    if not forecast_map:
        raise RuntimeError(
            "No vessel-rate forecasts are available."
        )

    scenario_results = {}

    for horizon_label, vessel_forecasts in forecast_map.items():
        forecast_rates = {}

        for vessel in VESSEL_PROFILES:
            forecast_info = vessel_forecasts.get(vessel)

            if forecast_info is None:
                continue

            forecast_value = forecast_info.get("forecast")

            if forecast_value is None:
                continue

            forecast_rates[vessel] = {
                "rate": float(forecast_value),
                "unit": "USD_PER_DAY",
                "source": "KOBC_ML_FORECAST",
                "date": forecast_info.get("target_date"),
                "route_specific": False,
                "forecast_horizon": forecast_info.get("horizon"),
                "horizon_type": forecast_info.get(
                    "horizon_type",
                    "market_observations"
                ),
                "forecast_method": forecast_info.get("method")
            }

        if not forecast_rates:
            continue

        result = optimize_vessel_economically(
            cargo_quantity=cargo_quantity,
            destination_port=destination_port,
            cargo_type=cargo_type,
            vessel_rates=forecast_rates,
            origin=origin
        )

        # Make it explicit that this is a forecast scenario,
        # not a current observed-rate recommendation.
        if result.get("status") == "success":
            recommended = result.get("recommended_vessel")
            recommended_data = result.get("comparison", {}).get(
                recommended, {}
            )

            result["recommendation_type"] = "forecast_economic"
            result["forecast_horizon"] = horizon_label
            result["forecast_horizon_type"] = "market_observations"
            result["forecast_reference_date"] = market.get(
                "reference_date"
            )
            result["reason"] = (
                f"{recommended} has the lowest estimated voyage "
                f"freight cost under the {horizon_label} KOBC "
                "rate forecast among feasible vessels. "
                f"Expected capacity utilization is "
                f"{recommended_data.get('capacity_utilization_percent', 0):.2f}% "
                f"({recommended_data.get('utilization_assessment', 'Unknown')})."
            )

        result["forecast_source"] = "KOBC"
        result["forecast_route_specific"] = False

        scenario_results[horizon_label] = result

    if not scenario_results:
        raise RuntimeError(
            "No usable vessel-rate forecast scenarios are available."
        )

    return {
        "status": "success",
        "reference_date": market.get("reference_date"),
        "horizon_type": market.get(
            "horizon_type",
            "market_observations"
        ),
        "source": "KOBC",
        "route_specific": False,
        "scenarios": scenario_results,
        "note": (
            "Forecasts are KOBC vessel-class benchmark rates. "
            "They are not route-specific voyage freight rates. "
            "Estimated voyage cost uses the current voyage-duration "
            "estimator together with each forecast benchmark rate."
        )
    }


# ============================================================
# MAIN FUNCTION
# ============================================================

def optimize_vessel(
    cargo_quantity,
    destination_port,
    cargo_type,
    vessel_rates=None,
    origin=None
):

    return optimize_vessel_economically(

        cargo_quantity=
            cargo_quantity,

        destination_port=
            destination_port,

        cargo_type=
            cargo_type,

        vessel_rates=
            vessel_rates,

        origin=
            origin
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

    # --------------------------------------------------------
    # Test scenario
    # --------------------------------------------------------

    cargo_quantity = 50000

    cargo_type = "Coal"

    origin = "Gladstone"

    destination_port = "Paradip"

    # --------------------------------------------------------
    # Load REAL KOBC rates
    # --------------------------------------------------------

    print(
        "\nLoading real KOBC vessel rates..."
    )

    try:

        vessel_rates = (
            load_current_kobc_rates()
        )

    except Exception as exc:

        print(
            "\nERROR loading KOBC rates:"
        )

        print(exc)

        raise

    # --------------------------------------------------------
    # Show rates
    # --------------------------------------------------------

    print(
        "\nCurrent KOBC vessel rates:"
    )

    print("-" * 70)

    for vessel, data in vessel_rates.items():

        print(

            f"{vessel:<12} | "
            f"{data['rate']:>10,.2f} "
            f"{data['unit']:<12} | "
            f"Source: {data['source']} | "
            f"Date: {data['date']}"
        )

    # --------------------------------------------------------
    # Run optimization
    # --------------------------------------------------------

    result = optimize_vessel_economically(

        cargo_quantity=
            cargo_quantity,

        destination_port=
            destination_port,

        cargo_type=
            cargo_type,

        vessel_rates=
            vessel_rates,

        origin=
            origin
    )

    # --------------------------------------------------------
    # Basic information
    # --------------------------------------------------------

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
        "Origin:",
        origin
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

    # --------------------------------------------------------
    # Recommended cost
    # --------------------------------------------------------

    if result["status"] == "success":

        print(
            "\nRecommended Total Freight Cost:",
            f"${result['recommended_total_freight_cost']:,.2f}"
        )

        print(
            "Recommended Freight Cost / MT:",
            f"${result['recommended_freight_cost_per_mt']:,.2f}"
        )

    # --------------------------------------------------------
    # Vessel comparison
    # --------------------------------------------------------

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
            "  Rate unit:",
            data[
                "freight_rate_unit"
            ]
        )

        print(
            "  Rate source:",
            data[
                "freight_rate_source"
            ]
        )

        print(
            "  Rate date:",
            data[
                "freight_rate_date"
            ]
        )

        print(
            "  Voyage distance:",
            data[
                "voyage_distance_nm"
            ],
            "NM"
        )

        print(
            "  Estimated sailing days:",
            data[
                "voyage_days"
            ]
        )

        print(
            "  Total freight cost:",
            data[
                "estimated_total_freight_cost"
            ]
        )

        print(
            "  Freight cost / MT:",
            data[
                "estimated_freight_cost_per_mt"
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
            "  Capacity utilization:",
            f"{data['capacity_utilization_percent']:.2f}%"
        )

        print(
            "  Utilization assessment:",
            data["utilization_assessment"]
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

    # --------------------------------------------------------
    # Forecast-based vessel scenarios
    # --------------------------------------------------------
    print(
        "\nFORECAST-BASED VESSEL OPTIMIZATION"
    )
    print("-" * 70)

    try:
        forecast_result = optimize_vessel_with_rate_forecast(
            cargo_quantity=cargo_quantity,
            destination_port=destination_port,
            cargo_type=cargo_type,
            origin=origin
        )

        print(
            "Reference date:",
            forecast_result["reference_date"]
        )
        print(
            "Horizon type:",
            forecast_result["horizon_type"]
        )

        for horizon, scenario in forecast_result[
            "scenarios"
        ].items():
            print(f"\n{horizon}:")

            if scenario["status"] != "success":
                print("  Recommendation unavailable")
                continue

            recommended = scenario[
                "recommended_vessel"
            ]
            recommended_data = scenario[
                "comparison"
            ][recommended]

            print(
                "  Recommended vessel:",
                recommended
            )
            print(
                "  Forecast rate:",
                f"${recommended_data['freight_rate']:,.2f}/day"
            )
            print(
                "  Estimated voyage cost:",
                f"${recommended_data['estimated_total_freight_cost']:,.2f}"
            )
            print(
                "  Freight cost / MT:",
                f"${recommended_data['estimated_freight_cost_per_mt']:,.2f}"
            )
            print(
                "  Capacity utilization:",
                f"{recommended_data['capacity_utilization_percent']:.2f}%"
            )
            print(
                "  Utilization assessment:",
                recommended_data["utilization_assessment"]
            )
            print(
                "  Target date:",
                recommended_data["freight_rate_date"]
            )

    except Exception as exc:
        print("\nForecast optimization unavailable:")
        print(exc)

    print(
        "\n" + "=" * 70
    )