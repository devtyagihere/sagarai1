# ============================================================
# FREIGHT INTELLIGENCE - FLASK API
# ============================================================

from flask import Flask, request, jsonify, send_file
import pandas as pd
import os

from src.bdi_forecasting_model import forecast_bdi
from src.oil_forecasting_model import forecast_oil_prices

from src.commodity_price_provider import (
    get_commodity_forecast
)

from src.weather_api import get_weather

from src.port_congestion_forecasting_model import (
    forecast_congestion
)

from src.train_model import load_models

from src.vessel_optimization import (
    optimize_vessel,
    optimize_vessel_with_rate_forecast,
    VESSEL_PROFILES
)

from src.market_entry_decision import (
    evaluate_market_entry
)

from src.decision_engine import (
    unified_risk,
    idle_scenario
)


# ============================================================
# FLASK APPLICATION
# ============================================================

app = Flask(__name__)


# ============================================================
# LOAD FREIGHT MODELS
# ============================================================

freight_model_package = load_models()

freight_models = freight_model_package["models"]

freight_horizons = freight_model_package.get(
    "horizons",
    [7, 15, 30]
)


print("=" * 70)
print("FREIGHT FORECASTING MODELS LOADED")
print("=" * 70)

print(
    "Available model types:",
    list(freight_models.keys())
)

print(
    "Horizons:",
    freight_horizons
)


# ============================================================
# SAFE VALUE HELPERS
# ============================================================

def safe_float(value):

    if value is None:
        return None

    try:

        value = float(value)

        if pd.isna(value):
            return None

        return value

    except Exception:

        return None


def safe_int(value):

    if value is None:
        return None

    try:

        value = float(value)

        if pd.isna(value):
            return None

        return int(value)

    except Exception:

        return None


# ============================================================
# CONGESTION SUPPORT
# ============================================================

def destination_has_congestion(destination_port):

    if not destination_port:
        return False

    return (
        destination_port.strip().lower()
        == "paradip"
    )


# ============================================================
# FREIGHT PREDICTION
# ============================================================

def predict_freight(
    origin_port,
    destination_port,
    cargo_type,
    bdi,
    oil_price,
    commodity_price,
    commodity_demand,
    weather_disruption,
    usd_index,
    date,
    horizon,
    port_congestion=None,
    use_congestion=False
):

    # --------------------------------------------------------
    # SELECT MODEL
    # --------------------------------------------------------

    if (
        use_congestion
        and "congestion" in freight_models
    ):

        model_type = "congestion"

    else:

        model_type = "base"


    # --------------------------------------------------------
    # CHECK MODEL
    # --------------------------------------------------------

    if model_type not in freight_models:

        raise ValueError(
            f"Freight model '{model_type}' "
            f"is not available."
        )


    # --------------------------------------------------------
    # GET HORIZON MODEL
    # --------------------------------------------------------

    horizon_models = freight_models[
        model_type
    ]


    if horizon not in horizon_models:

        raise ValueError(
            f"{model_type} model for "
            f"{horizon}-day horizon "
            f"is not available."
        )


    model_info = horizon_models[horizon]

    model = model_info["model"]

    feature_columns = model_info["features"]


    # --------------------------------------------------------
    # CREATE INPUT
    # --------------------------------------------------------

    row = {

        "origin_port":
            origin_port,

        "destination_port":
            destination_port,

        "cargo_type":
            cargo_type,

        "bdi":
            bdi,

        "oil_price":
            oil_price,

        "commodity_price":
            commodity_price,

        "commodity_demand":
            commodity_demand,

        "weather_disruption":
            weather_disruption,

        "usd_index":
            usd_index,

        "year":
            date.year,

        "month":
            date.month,

        "day":
            date.day
    }


    # --------------------------------------------------------
    # CONGESTION FEATURE
    # --------------------------------------------------------

    if "port_congestion" in feature_columns:

        if port_congestion is None:

            raise ValueError(
                "Congestion value is required "
                "for congestion-aware model."
            )

        row["port_congestion"] = port_congestion


    X = pd.DataFrame(
        [row]
    )


    # Exact training feature order
    X = X[
        feature_columns
    ]


    # --------------------------------------------------------
    # MODEL PREDICTION
    # --------------------------------------------------------

    prediction = model.predict(
        X
    )[0]


    return (
        float(prediction),
        model_type
    )


# ============================================================
# HOME / HEALTH CHECK
# ============================================================

@app.route(
    "/",
    methods=["GET"]
)
def home():

    return jsonify({

        "status":
            "running",

        "service":
            "Freight Intelligence API",

        "version":
            "3.1",

        "freight_models":
            list(
                freight_models.keys()
            ),

        "freight_horizons":
            freight_horizons,

        "congestion_supported_ports":
            [
                "Paradip"
            ],

        "intelligence_modules":
            [
                "BDI",
                "BDI Forecast",
                "Oil Forecast",
                "Commodity Forecast",
                "Weather",
                "Marine Risk",
                "Environmental Risk",
                "Port Congestion Forecast",
                "Freight Forecast",
                "Market Entry Decision",
                "Vessel Optimization",
                "Forecast Vessel Optimization",
                "Unified Risk Engine",
                "Idle Scenario Engine"
            ]
    })


# ============================================================
# DASHBOARD
# ============================================================

@app.route(
    "/dashboard",
    methods=["GET"]
)
def dashboard():

    dashboard_path = os.path.join(
        os.path.dirname(
            os.path.dirname(
                os.path.abspath(__file__)
            )
        ),
        "dashboard.html"
    )


    if not os.path.exists(
        dashboard_path
    ):

        return jsonify({

            "status":
                "error",

            "message":
                "dashboard.html not found."

        }), 404


    return send_file(
        dashboard_path
    )


# ============================================================
# MAIN PREDICTION API
# ============================================================

@app.route(
    "/predict",
    methods=["POST"]
)
def predict():

    try:

        data = request.get_json()


        # ====================================================
        # REQUEST VALIDATION
        # ====================================================

        if not data:

            return jsonify({

                "status":
                    "error",

                "message":
                    "Request body is missing."

            }), 400


        # ====================================================
        # INPUTS
        # ====================================================

        origin_port = data.get(
            "origin_port",
            "Gladstone"
        )


        destination_port = data.get(
            "destination_port",
            "Paradip"
        )


        cargo_type = data.get(
            "cargo_type",
            "Coal"
        )


        cargo_quantity = safe_float(
            data.get(
                "cargo_quantity",
                50000
            )
        )


        date_string = data.get(
            "date"
        )


        # Optional route-specific current freight.
        #
        # We NEVER fabricate this value.
        #
        current_freight_rate = safe_float(
            data.get(
                "current_freight_rate"
            )
        )


        # ====================================================
        # DATE
        # ====================================================

        if date_string:

            try:

                base_date = pd.to_datetime(
                    date_string
                )

            except Exception:

                return jsonify({

                    "status":
                        "error",

                    "message":
                        (
                            "Invalid date format. "
                            "Use YYYY-MM-DD."
                        )

                }), 400

        else:

            base_date = pd.Timestamp.today()


        # ====================================================
        # INPUT VALIDATION
        # ====================================================

        if cargo_quantity is None:

            return jsonify({

                "status":
                    "error",

                "message":
                    (
                        "cargo_quantity must "
                        "be a valid number."
                    )

            }), 400


        if cargo_quantity <= 0:

            return jsonify({

                "status":
                    "error",

                "message":
                    (
                        "cargo_quantity must "
                        "be greater than 0."
                    )

            }), 400


        if not origin_port:

            return jsonify({

                "status":
                    "error",

                "message":
                    "origin_port is required."

            }), 400


        if not destination_port:

            return jsonify({

                "status":
                    "error",

                "message":
                    "destination_port is required."

            }), 400


        if not cargo_type:

            return jsonify({

                "status":
                    "error",

                "message":
                    "cargo_type is required."

            }), 400


        # ====================================================
        # BDI FORECAST
        # ====================================================

        try:

            bdi_data = forecast_bdi(
                forecast_days=30
            )

        except Exception as error:

            return jsonify({

                "status":
                    "error",

                "message":
                    f"BDI forecast failed: {error}"

            }), 500


        # ====================================================
        # OIL FORECAST
        # ====================================================

        try:

            oil_data = forecast_oil_prices()

        except Exception as error:

            return jsonify({

                "status":
                    "error",

                "message":
                    f"Oil forecast failed: {error}"

            }), 500


        # ====================================================
        # COMMODITY FORECAST
        # ====================================================

        try:

            commodity_data = (
                get_commodity_forecast(
                    cargo_type
                )
            )

        except Exception as error:

            return jsonify({

                "status":
                    "error",

                "message":
                    (
                        "Commodity forecast failed: "
                        f"{error}"
                    )

            }), 500


        # ====================================================
        # CURRENT VALUES
        # ====================================================

        current_bdi = safe_float(
            bdi_data.get(
                "current_bdi"
            )
        )


        current_oil = safe_float(
            oil_data.get(
                "current_oil_price"
            )
        )


        current_commodity = safe_float(
            commodity_data.get(
                "current_price"
            )
        )


        commodity_demand = safe_float(
            commodity_data.get(
                "demand"
            )
        )


        # ----------------------------------------------------
        # Neutral fallback only for model fields that require
        # numeric input.
        # ----------------------------------------------------

        if current_bdi is None:
            current_bdi = 0.0

        if current_oil is None:
            current_oil = 0.0

        if current_commodity is None:
            current_commodity = 0.0

        if commodity_demand is None:
            commodity_demand = 0.0


        # ====================================================
        # CONGESTION
        # ====================================================

        congestion_supported = (
            destination_has_congestion(
                destination_port
            )
        )


        congestion_data = None

        congestion_forecast = {}


        if congestion_supported:

            try:

                congestion_data = (
                    forecast_congestion(
                        "Paradip"
                    )
                )

                congestion_forecast = (
                    congestion_data.get(
                        "forecast",
                        {}
                    )
                )

            except Exception as error:

                print(
                    "Congestion forecast unavailable:",
                    error
                )

                congestion_data = None

                congestion_forecast = {}


        # ====================================================
        # FORECAST HORIZONS
        # ====================================================

        horizons = {

            7:
                "7_day",

            15:
                "15_day",

            30:
                "30_day"
        }


        forecast_results = {}


        # ====================================================
        # FORECAST LOOP
        # ====================================================

        for horizon, label in horizons.items():

            # ------------------------------------------------
            # TARGET DATE
            # ------------------------------------------------

            target_date = (

                base_date

                +
                pd.Timedelta(
                    days=horizon
                )
            )


            # ------------------------------------------------
            # BDI
            # ------------------------------------------------

            bdi_forecast = safe_float(

                bdi_data
                .get(
                    "forecast",
                    {}
                )
                .get(
                    label
                )
            )


            if bdi_forecast is None:

                bdi_forecast = current_bdi


            # ------------------------------------------------
            # OIL
            # ------------------------------------------------

            oil_forecast = safe_float(

                oil_data
                .get(
                    "forecast",
                    {}
                )
                .get(
                    label
                )
            )


            if oil_forecast is None:

                oil_forecast = current_oil


            # ------------------------------------------------
            # COMMODITY
            # ------------------------------------------------

            commodity_forecast = safe_float(

                commodity_data
                .get(
                    "forecast",
                    {}
                )
                .get(
                    label
                )
            )


            if commodity_forecast is None:

                commodity_forecast = current_commodity


            # ------------------------------------------------
            # WEATHER
            # ------------------------------------------------

            try:

                weather = get_weather(

                    destination_port,

                    target_date.strftime(
                        "%Y-%m-%d"
                    )
                )

            except Exception as error:

                print(
                    "Weather unavailable:",
                    error
                )

                weather = {}


            # ------------------------------------------------
            # WEATHER DISRUPTION
            # ------------------------------------------------

            weather_disruption = safe_int(

                weather.get(
                    "weather_disruption"
                )
            )


            if weather_disruption is None:

                weather_disruption = 0


            # ------------------------------------------------
            # USD INDEX
            # ------------------------------------------------

            # No fabricated live USD value.
            usd_index = 0.0


            # ------------------------------------------------
            # CONGESTION
            # ------------------------------------------------

            port_congestion = None

            congestion_used = False

            congestion_level = None

            congestion_reference_date = None


            if congestion_supported:

                congestion_result = (
                    congestion_forecast.get(
                        label
                    )
                )


                if congestion_result:

                    port_congestion = safe_float(

                        congestion_result.get(
                            "score"
                        )
                    )


                    congestion_level = (
                        congestion_result.get(
                            "level"
                        )
                    )


                    if port_congestion is not None:

                        congestion_used = True


                if congestion_data:

                    congestion_reference_date = (
                        congestion_data.get(
                            "reference_date"
                        )
                    )


            # ------------------------------------------------
            # FREIGHT PREDICTION
            # ------------------------------------------------

            predicted_freight, model_used = (
                predict_freight(

                    origin_port=
                        origin_port,

                    destination_port=
                        destination_port,

                    cargo_type=
                        cargo_type,

                    bdi=
                        bdi_forecast,

                    oil_price=
                        oil_forecast,

                    commodity_price=
                        commodity_forecast,

                    commodity_demand=
                        commodity_demand,

                    weather_disruption=
                        weather_disruption,

                    usd_index=
                        usd_index,

                    date=
                        target_date,

                    horizon=
                        horizon,

                    port_congestion=
                        port_congestion,

                    use_congestion=
                        congestion_used
                )
            )


            # ------------------------------------------------
            # WEATHER VALUES
            # ------------------------------------------------

            weather_code = safe_int(
                weather.get(
                    "weather_code"
                )
            )


            temperature = safe_float(
                weather.get(
                    "temperature"
                )
            )


            precipitation = safe_float(
                weather.get(
                    "precipitation"
                )
            )


            wind_speed = safe_float(
                weather.get(
                    "wind_speed"
                )
            )


            # ------------------------------------------------
            # MARINE
            # ------------------------------------------------

            marine_available = bool(

                weather.get(
                    "marine_available",
                    False
                )
            )


            wave_height = safe_float(
                weather.get(
                    "wave_height"
                )
            )


            wave_period = safe_float(
                weather.get(
                    "wave_period"
                )
            )


            wave_direction = safe_float(
                weather.get(
                    "wave_direction"
                )
            )


            # ------------------------------------------------
            # RISK
            # ------------------------------------------------

            marine_risk_score = safe_float(
                weather.get(
                    "marine_risk_score"
                )
            )


            marine_risk_level = (
                weather.get(
                    "marine_risk_level"
                )
            )


            environmental_risk_score = (
                safe_float(
                    weather.get(
                        "environmental_risk_score"
                    )
                )
            )


            environmental_risk_level = (
                weather.get(
                    "environmental_risk_level"
                )
            )


            # ------------------------------------------------
            # IMPORTANT DATA QUALITY RULE
            #
            # If marine data is unavailable, its risk score
            # must NOT be treated as a real Severe/100 signal.
            # ------------------------------------------------

            if not marine_available:

                marine_risk_score = None

                marine_risk_level = "Unavailable"


            # =================================================
            # SAVE FORECAST
            # =================================================

            forecast_results[label] = {

                "target_date":
                    target_date.strftime(
                        "%Y-%m-%d"
                    ),

                "predicted_freight_rate":
                    round(
                        predicted_freight,
                        4
                    ),

                "model_used":
                    model_used,


                "bdi": {

                    "current":
                        current_bdi,

                    "forecast":
                        bdi_forecast
                },


                "oil": {

                    "current":
                        current_oil,

                    "forecast":
                        oil_forecast
                },


                "commodity": {

                    "type":
                        commodity_data.get(
                            "commodity"
                        ),

                    "current":
                        current_commodity,

                    "forecast":
                        commodity_forecast
                },


                "congestion": {

                    "supported":
                        congestion_supported,

                    "used":
                        congestion_used,

                    "forecast_score":
                        port_congestion,

                    "level":
                        congestion_level,

                    "reference_date":
                        congestion_reference_date
                },


                "weather": {

                    "temperature":
                        temperature,

                    "precipitation":
                        precipitation,

                    "wind_speed":
                        wind_speed,

                    "weather_code":
                        weather_code,

                    "weather_disruption":
                        weather_disruption
                },


                "marine": {

                    "available":
                        marine_available,

                    "wave_height":
                        wave_height,

                    "wave_period":
                        wave_period,

                    "wave_direction":
                        wave_direction
                },


                "risk": {

                    "marine_score":
                        marine_risk_score,

                    "marine_level":
                        marine_risk_level,

                    "environmental_score":
                        environmental_risk_score,

                    "environmental_level":
                        environmental_risk_level
                }
            }


        # ====================================================
        # MARKET ENTRY DECISION
        # ====================================================

        market_entry_decisions = {}


        for horizon, label in horizons.items():

            item = forecast_results.get(
                label,
                {}
            )


            bdi_item = item.get(
                "bdi",
                {}
            )

            oil_item = item.get(
                "oil",
                {}
            )

            commodity_item = item.get(
                "commodity",
                {}
            )

            congestion_item = item.get(
                "congestion",
                {}
            )

            weather_item = item.get(
                "weather",
                {}
            )

            risk_item = item.get(
                "risk",
                {}
            )


            decision_result = evaluate_market_entry(

                current_freight=
                    current_freight_rate,

                future_freight=
                    safe_float(
                        item.get(
                            "predicted_freight_rate"
                        )
                    ),

                current_bdi=
                    safe_float(
                        bdi_item.get(
                            "current"
                        )
                    ),

                future_bdi=
                    safe_float(
                        bdi_item.get(
                            "forecast"
                        )
                    ),

                current_oil=
                    safe_float(
                        oil_item.get(
                            "current"
                        )
                    ),

                future_oil=
                    safe_float(
                        oil_item.get(
                            "forecast"
                        )
                    ),

                current_commodity=
                    safe_float(
                        commodity_item.get(
                            "current"
                        )
                    ),

                future_commodity=
                    safe_float(
                        commodity_item.get(
                            "forecast"
                        )
                    ),

                congestion_score=
                    safe_float(
                        congestion_item.get(
                            "forecast_score"
                        )
                    ),

                weather_disruption=
                    safe_float(
                        weather_item.get(
                            "weather_disruption"
                        )
                    ),

                environmental_score=
                    safe_float(
                        risk_item.get(
                            "environmental_score"
                        )
                    ),

                marine_score=
                    safe_float(
                        risk_item.get(
                            "marine_score"
                        )
                    )
            )


            market_entry_decisions[label] = {

                "target_date":
                    item.get(
                        "target_date"
                    ),

                **decision_result
            }


        primary_market_entry = (
            market_entry_decisions.get(
                "7_day"
            )
        )


        # ====================================================
        # CURRENT VESSEL OPTIMIZATION
        # ====================================================

        vessel_result = optimize_vessel(

            cargo_quantity=
                cargo_quantity,

            destination_port=
                destination_port,

            cargo_type=
                cargo_type,

            origin=
                origin_port
        )


        # ====================================================
        # FORECAST VESSEL OPTIMIZATION
        # ====================================================

        forecast_vessel_result = {}


        try:

            forecast_vessel_result = (
                optimize_vessel_with_rate_forecast(

                    cargo_quantity=
                        cargo_quantity,

                    destination_port=
                        destination_port,

                    cargo_type=
                        cargo_type,

                    origin=
                        origin_port
                )
            )

        except Exception as error:

            print(
                "Forecast vessel optimization unavailable:",
                error
            )

            forecast_vessel_result = {}


        # ====================================================
        # DECISION ENGINE
        # ====================================================

        primary_forecast = forecast_results.get(
            "7_day",
            {}
        )


        # ====================================================
        # MARKET MOVEMENT
        # ====================================================

        market_move_pct = None


        if current_freight_rate is not None:

            future_primary_freight = safe_float(

                primary_forecast.get(
                    "predicted_freight_rate"
                )
            )


            if (
                future_primary_freight is not None
                and current_freight_rate != 0
            ):

                market_move_pct = (

                    (
                        future_primary_freight
                        -
                        current_freight_rate
                    )
                    /
                    current_freight_rate
                ) * 100


        # ====================================================
        # PRIMARY RISK SIGNALS
        # ====================================================

        primary_congestion = safe_float(

            primary_forecast
            .get(
                "congestion",
                {}
            )
            .get(
                "forecast_score"
            )
        )


        primary_weather = safe_float(

            primary_forecast
            .get(
                "weather",
                {}
            )
            .get(
                "weather_disruption"
            )
        )


        primary_marine = safe_float(

            primary_forecast
            .get(
                "risk",
                {}
            )
            .get(
                "marine_score"
            )
        )


        primary_environmental = safe_float(

            primary_forecast
            .get(
                "risk",
                {}
            )
            .get(
                "environmental_score"
            )
        )


        # ====================================================
        # UNIFIED RISK
        # ====================================================

        risk_result = unified_risk(

            weather=
                primary_weather,

            marine=
                primary_marine,

            environmental=
                primary_environmental,

            congestion=
                primary_congestion,

            market_move_pct=
                market_move_pct
        )


        # ====================================================
        # IDLE SCENARIO
        # ====================================================

        idle_result = {

            "status":
                "insufficient_data",

            "message":
                (
                    "Idle scenario requires "
                    "current and future vessel "
                    "freight rates."
                )
        }


        try:

            # ------------------------------------------------
            # Recommended current vessel
            # ------------------------------------------------

            recommended_vessel = (
                vessel_result.get(
                    "recommended_vessel"
                )
            )


            # ------------------------------------------------
            # Vessel DWT
            # ------------------------------------------------

            vessel_capacity = None


            if recommended_vessel:

                vessel_profile = (
                    VESSEL_PROFILES.get(
                        recommended_vessel
                    )
                )


                if vessel_profile:

                    vessel_capacity = safe_float(

                        vessel_profile.get(
                            "dwt"
                        )
                    )


            # ------------------------------------------------
            # Current vessel rate
            #
            # The optimization result stores rates inside
            # comparison[recommended_vessel].
            # ------------------------------------------------

            current_vessel_freight = None


            if (
                recommended_vessel
                and isinstance(
                    vessel_result,
                    dict
                )
            ):

                comparison = vessel_result.get(
                    "comparison",
                    {}
                )


                recommended_details = (
                    comparison.get(
                        recommended_vessel,
                        {}
                    )
                )


                current_vessel_freight = (
                    safe_float(
                        recommended_details.get(
                            "freight_rate"
                        )
                    )
                )


            # ------------------------------------------------
            # Future vessel rate
            #
            # Use 30-day KOBC forecast because the idle
            # scenario is explicitly comparing current vs
            # future vessel benchmark.
            # ------------------------------------------------

            future_vessel_freight = None


            forecast_30 = (

                forecast_vessel_result.get(
                    "30_day"
                )
                if isinstance(
                    forecast_vessel_result,
                    dict
                )
                else None
            )


            if isinstance(
                forecast_30,
                dict
            ):

                future_comparison = (
                    forecast_30.get(
                        "comparison",
                        {}
                    )
                )


                # Prefer the same recommended vessel
                # for apples-to-apples comparison.
                if recommended_vessel:

                    future_vessel_details = (
                        future_comparison.get(
                            recommended_vessel,
                            {}
                        )
                    )


                    future_vessel_freight = (
                        safe_float(
                            future_vessel_details.get(
                                "freight_rate"
                            )
                        )
                    )


            # ------------------------------------------------
            # Run idle scenario only when all required
            # real benchmark values are available.
            # ------------------------------------------------

            if (
                vessel_capacity is not None
                and current_vessel_freight is not None
                and future_vessel_freight is not None
            ):

                idle_result = idle_scenario(

                    vessel_capacity_mt=
                        vessel_capacity,

                    cargo_quantity_mt=
                        cargo_quantity,

                    current_freight=
                        current_vessel_freight,

                    future_freight=
                        future_vessel_freight,

                    congestion_score=
                        primary_congestion
                )


        except Exception as error:

            print(
                "Idle scenario unavailable:",
                error
            )


            idle_result = {

                "status":
                    "error",

                "message":
                    str(error)
            }


        # ====================================================
        # FINAL RESPONSE
        # ====================================================

        response = {

            "status":
                "success",


            "base_date":
                base_date.strftime(
                    "%Y-%m-%d"
                ),


            "route": {

                "origin_port":
                    origin_port,

                "destination_port":
                    destination_port
            },


            "cargo": {

                "type":
                    cargo_type,

                "quantity_mt":
                    cargo_quantity
            },


            # =================================================
            # FREIGHT MODEL LOGIC
            # =================================================

            "freight_model_logic": {

                "destination":
                    destination_port,

                "congestion_supported":
                    congestion_supported,

                "model_rule":
                    (
                        "Congestion-aware model"
                        if congestion_supported
                        else
                        "Base model - congestion skipped"
                    )
            },


            # =================================================
            # FREIGHT FORECAST
            # =================================================

            "forecast":
                forecast_results,


            # =================================================
            # CURRENT VESSEL OPTIMIZATION
            # =================================================

            "vessel_optimization":
                vessel_result,


            # =================================================
            # FORECAST VESSEL OPTIMIZATION
            # =================================================

            "forecast_vessel_optimization":
                forecast_vessel_result,


            # =================================================
            # MARKET ENTRY
            # =================================================

            "market_entry_decision": {

                "current_freight_rate_provided":
                    current_freight_rate is not None,

                "primary":
                    primary_market_entry,

                "horizons":
                    market_entry_decisions,

                "note":
                    (
                        "Explainable decision-support "
                        "layer; confidence is "
                        "signal-based, not statistical "
                        "model probability, and the "
                        "decision does not guarantee "
                        "profit."
                    )
            },


            # =================================================
            # UNIFIED RISK
            # =================================================

            "unified_risk":
                risk_result,


            # =================================================
            # IDLE SCENARIO
            # =================================================

            "idle_scenario":
                idle_result,


            # =================================================
            # MARKET DATA
            # =================================================

            "market_data": {

                "bdi_current":
                    current_bdi,

                "oil_current":
                    current_oil,

                "commodity_current":
                    current_commodity
            }
        }


        return jsonify(
            response
        )


    # ========================================================
    # GLOBAL API ERROR
    # ========================================================

    except Exception as error:

        return jsonify({

            "status":
                "error",

            "message":
                str(error)

        }), 500


# ============================================================
# START SERVER
# ============================================================

if __name__ == "__main__":

    app.run(

        host="0.0.0.0",

        port=5000,

        debug=True
    )