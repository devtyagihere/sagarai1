def unified_risk(
    weather=None,
    marine=None,
    environmental=None,
    congestion=None,
    market_move_pct=None
):
    signals = []
    weighted_sum = 0.0
    total_weight = 0.0

    def add_signal(name, value, weight):
        nonlocal weighted_sum, total_weight

        if value is None:
            return

        value = max(0.0, min(100.0, float(value)))
        weighted_sum += value * weight
        total_weight += weight

        signals.append({
            "signal": name,
            "score": round(value, 2),
            "weight": weight
        })

    add_signal("weather", weather, 0.25)
    add_signal("marine", marine, 0.20)
    add_signal("environmental", environmental, 0.15)
    add_signal("port_congestion", congestion, 0.25)

    if market_move_pct is not None:
        market_score = min(abs(float(market_move_pct)) * 5, 100)
        add_signal("market_movement", market_score, 0.15)

    if total_weight == 0:
        return {
            "status": "insufficient_data",
            "risk_score": None,
            "risk_level": "Unknown",
            "signals": []
        }

    risk_score = weighted_sum / total_weight

    if risk_score < 20:
        risk_level = "Low"
    elif risk_score < 40:
        risk_level = "Moderate"
    elif risk_score < 70:
        risk_level = "High"
    else:
        risk_level = "Severe"

    return {
        "status": "success",
        "risk_score": round(risk_score, 2),
        "risk_level": risk_level,
        "signals": signals
    }


def idle_scenario(
    vessel_capacity_mt,
    cargo_quantity_mt,
    current_freight,
    future_freight,
    congestion_score=None
):
    usable_capacity = float(vessel_capacity_mt) * 0.95
    cargo_quantity = float(cargo_quantity_mt)

    utilization = (cargo_quantity / usable_capacity) * 100
    utilization = min(utilization, 100)

    freight_change_pct = (
        (float(future_freight) - float(current_freight))
        / float(current_freight)
    ) * 100

    if utilization < 40:
        utilization_status = "Under-utilized"
        idle_risk = "High"
        action = "Prefer a smaller vessel or consolidate cargo."
    elif utilization < 60:
        utilization_status = "Moderate utilization"
        idle_risk = "Moderate"
        action = "Evaluate a smaller vessel before chartering."
    else:
        utilization_status = "Efficient utilization"
        idle_risk = "Low"
        action = "Vessel capacity is reasonably aligned with cargo."

    if congestion_score is not None and congestion_score >= 70:
        action += " Consider congestion-related waiting and delay exposure."

    if freight_change_pct > 5:
        action += " Rising freight supports earlier charter evaluation."
    elif freight_change_pct < -5:
        action += " Falling freight may justify waiting if operationally feasible."

    return {
        "status": "success",
        "vessel_capacity_mt": round(usable_capacity, 2),
        "cargo_quantity_mt": round(cargo_quantity, 2),
        "capacity_utilization_percent": round(utilization, 2),
        "utilization_status": utilization_status,
        "idle_risk": idle_risk,
        "freight_change_percent": round(freight_change_pct, 2),
        "recommended_action": action
    }


if __name__ == "__main__":
    print("DECISION ENGINE TEST")
    print("=" * 60)

    risk = unified_risk(
        weather=60,
        marine=40,
        environmental=20,
        congestion=80,
        market_move_pct=10
    )

    print("\nUnified Risk:")
    print(risk)

    idle = idle_scenario(
        vessel_capacity_mt=58328,
        cargo_quantity_mt=50000,
        current_freight=21434,
        future_freight=19180.28,
        congestion_score=80
    )

    print("\nIdle Scenario:")
    print(idle)