# ============================================================
# MARKET ENTRY DECISION INTELLIGENCE
# ============================================================
#
# Purpose:
#   Convert forecast signals into a transparent charter timing
#   recommendation:
#
#       CHARTER_NOW / WAIT / MONITOR
#
# IMPORTANT:
#   This is a decision layer, not a separately trained ML model.
#   It does not invent historical charter decisions.
#   It combines the already-forecasted market signals and gives
#   an explainable recommendation.
# ============================================================

from typing import Any, Dict, Optional


HORIZONS = [7, 15, 30]


def _to_float(value: Any) -> Optional[float]:
    """Safely convert a value to float."""
    try:
        if value is None:
            return None
        return float(value)
    except (TypeError, ValueError):
        return None


def _clamp(value: float, low: float = -100.0, high: float = 100.0) -> float:
    return max(low, min(high, value))


def _freight_signal(
    current_freight: Optional[float],
    future_freight: Optional[float],
) -> float:
    """
    Positive score = freight expected to rise -> charter sooner.
    Negative score = freight expected to fall -> waiting may help.

    The score is normalized by percentage change rather than using
    an absolute freight-rate threshold.
    """
    if current_freight is None or future_freight is None or current_freight <= 0:
        return 0.0

    pct_change = ((future_freight - current_freight) / current_freight) * 100.0

    # 10% increase/decrease is treated as a strong signal.
    return _clamp(pct_change * 6.0, -60.0, 60.0)


def _market_signal(
    current_value: Optional[float],
    future_value: Optional[float],
    weight: float,
) -> float:
    """
    Generic market-cost signal.

    For BDI/oil:
      rising values -> generally upward freight/cost pressure
      falling values -> generally downward pressure

    This is deliberately a secondary signal; freight forecast remains
    the primary decision input.
    """
    if current_value is None or future_value is None or current_value == 0:
        return 0.0

    pct_change = ((future_value - current_value) / abs(current_value)) * 100.0
    return _clamp(pct_change * weight, -20.0, 20.0)


def _congestion_signal(congestion: Optional[float]) -> float:
    """
    High current/future congestion increases the value of securing
    cargo movement earlier.

    No congestion data = neutral signal.
    """
    if congestion is None:
        return 0.0

    if congestion >= 40:
        return 15.0
    if congestion >= 25:
        return 8.0
    if congestion >= 10:
        return 3.0
    return 0.0


def _risk_signal(
    weather_disruption: Optional[float],
    environmental_score: Optional[float],
    marine_score: Optional[float],
) -> float:
    """
    Operational-risk signal.

    High disruption/risk makes delaying a shipment less attractive,
    but the signal is capped so it cannot dominate the freight trend.
    """
    score = 0.0

    if weather_disruption is not None and weather_disruption >= 1:
        score += 8.0

    risk_scores = [
        x for x in (environmental_score, marine_score)
        if x is not None
    ]

    if risk_scores:
        avg_risk = sum(risk_scores) / len(risk_scores)

        if avg_risk >= 75:
            score += 10.0
        elif avg_risk >= 50:
            score += 6.0
        elif avg_risk >= 25:
            score += 3.0

    return min(score, 18.0)


def _classify(score: float) -> str:
    """
    Decision thresholds.

    Positive -> earlier chartering pressure.
    Negative -> waiting pressure.
    """
    if score >= 25:
        return "CHARTER_NOW"
    if score <= -25:
        return "WAIT"
    return "MONITOR"


def _confidence(score: float, available_signals: int) -> str:
    """
    Confidence reflects signal strength and data availability.
    It is not statistical model confidence.
    """
    magnitude = abs(score)

    if available_signals < 2:
        return "Low"

    if magnitude >= 40 and available_signals >= 4:
        return "High"

    if magnitude >= 25 and available_signals >= 3:
        return "Medium"

    return "Low"


def evaluate_market_entry(
    current_freight: Optional[float],
    future_freight: Optional[float],
    current_bdi: Optional[float] = None,
    future_bdi: Optional[float] = None,
    current_oil: Optional[float] = None,
    future_oil: Optional[float] = None,
    future_commodity: Optional[float] = None,
    current_commodity: Optional[float] = None,
    congestion_score: Optional[float] = None,
    weather_disruption: Optional[float] = None,
    environmental_score: Optional[float] = None,
    marine_score: Optional[float] = None,
) -> Dict[str, Any]:
    """
    Generate one explainable market-entry decision.

    Positive decision score:
        stronger reason to secure freight earlier.

    Negative decision score:
        stronger reason to wait for potentially cheaper freight.

    Commodity is intentionally a low-weight supporting signal because
    its relationship with freight depends on cargo/market conditions.
    """

    contributions = {}

    freight = _freight_signal(current_freight, future_freight)
    contributions["freight_trend"] = round(freight, 2)

    bdi = _market_signal(current_bdi, future_bdi, weight=1.5)
    contributions["bdi_trend"] = round(bdi, 2)

    oil = _market_signal(current_oil, future_oil, weight=1.0)
    contributions["oil_trend"] = round(oil, 2)

    commodity = _market_signal(
        current_commodity,
        future_commodity,
        weight=0.5,
    )
    contributions["commodity_trend"] = round(commodity, 2)

    congestion = _congestion_signal(congestion_score)
    contributions["port_congestion"] = round(congestion, 2)

    risk = _risk_signal(
        weather_disruption,
        environmental_score,
        marine_score,
    )
    contributions["operational_risk"] = round(risk, 2)

    score = _clamp(
        freight
        + bdi
        + oil
        + commodity
        + congestion
        + risk,
        -100,
        100,
    )

    available_signals = sum(
        value is not None
        for value in (
            current_freight,
            future_freight,
            current_bdi,
            future_bdi,
            current_oil,
            future_oil,
            congestion_score,
            weather_disruption,
            environmental_score,
            marine_score,
        )
    )

    decision = _classify(score)
    confidence = _confidence(score, available_signals)

    # Human-readable explanation.
    reasons = []

    if future_freight is not None and current_freight is not None:
        change = ((future_freight - current_freight) / current_freight) * 100
        if change > 3:
            reasons.append(
                f"forecast freight is rising by {change:.1f}%"
            )
        elif change < -3:
            reasons.append(
                f"forecast freight is falling by {abs(change):.1f}%"
            )
        else:
            reasons.append("forecast freight is relatively stable")

    if congestion_score is not None:
        if congestion_score >= 40:
            reasons.append("port congestion is severe")
        elif congestion_score >= 25:
            reasons.append("port congestion is elevated")

    if weather_disruption is not None and weather_disruption >= 1:
        reasons.append("weather disruption risk is elevated")

    if environmental_score is not None and environmental_score >= 75:
        reasons.append("environmental risk is high")

    if marine_score is not None and marine_score >= 75:
        reasons.append("marine risk is high")

    if not reasons:
        reasons.append("insufficient directional market signals")

    return {
        "decision": decision,
        "decision_score": round(score, 2),
        "confidence": confidence,
        "reason": "; ".join(reasons),
        "signal_contributions": contributions,
        "method": "Explainable multi-signal decision layer",
        "warning": (
            "This is a decision-support score, not a guaranteed "
            "price or profit prediction."
        ),
    }


def build_market_entry_analysis(
    current_freight: Optional[float],
    forecast_results: Dict[str, Dict[str, Any]],
) -> Dict[str, Any]:
    """
    Evaluate 7/15/30-day forecast horizons together.

    forecast_results is expected to contain keys:
        7_day, 15_day, 30_day

    Each horizon may contain:
        predicted_freight_rate
        bdi.current / bdi.forecast
        oil.current / oil.forecast
        commodity.current / commodity.forecast
        congestion.forecast_score
        weather.weather_disruption
        risk.environmental_score
        risk.marine_score
    """

    horizon_results = {}

    for horizon in HORIZONS:
        key = f"{horizon}_day"
        data = forecast_results.get(key)

        if not data:
            continue

        bdi = data.get("bdi", {})
        oil = data.get("oil", {})
        commodity = data.get("commodity", {})
        congestion = data.get("congestion", {})
        weather = data.get("weather", {})
        risk = data.get("risk", {})

        result = evaluate_market_entry(
            current_freight=current_freight,
            future_freight=_to_float(
                data.get("predicted_freight_rate")
            ),
            current_bdi=_to_float(bdi.get("current")),
            future_bdi=_to_float(bdi.get("forecast")),
            current_oil=_to_float(oil.get("current")),
            future_oil=_to_float(oil.get("forecast")),
            current_commodity=_to_float(
                commodity.get("current")
            ),
            future_commodity=_to_float(
                commodity.get("forecast")
            ),
            congestion_score=_to_float(
                congestion.get("forecast_score")
            ),
            weather_disruption=_to_float(
                weather.get("weather_disruption")
            ),
            environmental_score=_to_float(
                risk.get("environmental_score")
            ),
            marine_score=_to_float(
                risk.get("marine_score")
            ),
        )

        horizon_results[key] = {
            "target_date": data.get("target_date"),
            **result,
        }

    # Overall recommendation:
    # Use the nearest available horizon as the primary timing signal.
    if "7_day" in horizon_results:
        primary = horizon_results["7_day"]
    elif horizon_results:
        primary = next(iter(horizon_results.values()))
    else:
        return {
            "status": "unavailable",
            "reason": "No forecast horizons were available.",
            "horizons": {},
        }

    return {
        "status": "success",
        "primary_decision": primary["decision"],
        "primary_confidence": primary["confidence"],
        "primary_reason": primary["reason"],
        "primary_horizon": (
            "7_day" if "7_day" in horizon_results
            else next(iter(horizon_results))
        ),
        "horizons": horizon_results,
        "method": "Explainable multi-signal decision layer",
    }


if __name__ == "__main__":
    # Standalone smoke test using clearly labeled example values.
    # These are only for testing the decision logic, not market data.
    demo = build_market_entry_analysis(
        current_freight=2500.0,
        forecast_results={
            "7_day": {
                "target_date": "2026-09-17",
                "predicted_freight_rate": 2750.0,
                "bdi": {"current": 3500.0, "forecast": 3650.0},
                "oil": {"current": 90.0, "forecast": 92.0},
                "commodity": {"current": 135.0, "forecast": 136.0},
                "congestion": {"forecast_score": 45.0},
                "weather": {"weather_disruption": 1},
                "risk": {
                    "environmental_score": 60.0,
                    "marine_score": 40.0,
                },
            }
        },
    )

    print("=" * 70)
    print("MARKET ENTRY DECISION TEST")
    print("=" * 70)
    print(demo)
