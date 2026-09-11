"""
Integrated Decision Engine — Phase 4.

Combines ALL upstream module outputs into a single transparent
CHARTER NOW / WAIT / NEGOTIATE recommendation.

════════════════════════════════════════════════════════════════════════
FACTOR SCORING FRAMEWORK
════════════════════════════════════════════════════════════════════════

Seven factors, each scored 0-100 (higher = more favourable to charter now):

  Factor                 Weight   Source
  ─────────────────────  ──────   ──────────────────────────────────────────
  1. freight_trend        0.20    FreightForecast.forecast_change_percent
                                  Falling rate -> good to charter (score 75-100)
                                  Stable       -> neutral       (score ~50)
                                  Rising rate  -> wait          (score 0-40)

  2. bdi_trend            0.15    MarketIndicator.direction (BDI)
                                  'down'   -> lower market  -> charter now (80)
                                  'stable' -> neutral                      (50)
                                  'up'     -> rising market -> wait        (20)

  3. oil_trend            0.10    MarketIndicator.direction (WTI oil)
                                  'down'   -> cheaper ops -> charter now   (80)
                                  'stable' -> neutral                      (50)
                                  'up'     -> costlier ops -> wait         (20)

  4. commodity_trend      0.10    MarketIndicator.direction (commodity)
                                  'up'     -> rising demand -> charter now (80)
                                  'stable' -> neutral                      (50)
                                  'down'   -> demand soft  -> wait         (20)
                                  None     -> no commodity data            (50, unavailable)

  5. port_congestion      0.15    PortCongestion.congestion_score (0-100)
                                  Inverted: low congestion = high score
                                  score = 100 - congestion_score (worst port)

  6. risk                 0.15    RiskAssessment.overall_risk_score (0-100)
                                  Inverted: low risk = high score
                                  score = 100 - overall_risk_score

  7. vessel_economics     0.15    Cheapest feasible cost_per_mt_usd
                                  Compare against median across all vessels:
                                  < 60% of median -> 90 (very cheap)
                                  60-80%           -> 75
                                  80-100%          -> 60
                                  > 100% (expensive)-> 30
                                  None (no feasible)-> 0

  TOTAL WEIGHTS = 1.00

════════════════════════════════════════════════════════════════════════
DECISION THRESHOLDS
════════════════════════════════════════════════════════════════════════
  overall_score >= 65  ->  CHARTER NOW
  40 <= score   < 65   ->  NEGOTIATE
  score         < 40   ->  WAIT

════════════════════════════════════════════════════════════════════════
CONFIDENCE LOGIC
════════════════════════════════════════════════════════════════════════
  HIGH     : factors_available == 7 AND feasible_vessel AND
             (model R2 >= 0.70 OR forecast unavailable)
  MODERATE : factors_available >= 5 AND feasible_vessel
  LOW      : factors_available < 5 OR no feasible vessel

════════════════════════════════════════════════════════════════════════
DATA: All inputs sourced from SYNTHETIC datasets.
      This is an educational demonstration, not a commercial tool.
════════════════════════════════════════════════════════════════════════
"""

from __future__ import annotations

from statistics import mean
from typing import Any, Dict, List, Optional

from app.models.decision import DecisionResult, FactorScore
from config import (
    DECISION_CHARTER_THRESHOLD,
    DECISION_NEGOTIATE_THRESHOLD,
    DECISION_WEIGHTS,
    MARKET_DATA_SOURCE,
)


# ─────────────────────────────────────────────────────────────────────────────
# Internal helper: direction string -> score
# ─────────────────────────────────────────────────────────────────────────────

def _direction_to_score_bullish(direction: str) -> float:
    """
    For BDI and Oil trends:
      'down'   -> 80  (falling cost / index = good to charter)
      'stable' -> 50
      'up'     -> 20  (rising cost = wait)
    """
    return {"down": 80.0, "stable": 50.0, "up": 20.0}.get(direction.lower(), 50.0)


def _direction_to_score_commodity(direction: str) -> float:
    """
    For commodity price:
      'up'     -> 80  (rising commodity = cargo owner wants to ship urgently)
      'stable' -> 50
      'down'   -> 20  (soft commodity = less shipping urgency)
    """
    return {"up": 80.0, "stable": 50.0, "down": 20.0}.get(direction.lower(), 50.0)


def _freight_trend_score(change_pct: float) -> float:
    """
    Convert freight rate forecast % change to a 0-100 score.
    Falling rates favour chartering now; rising rates favour waiting.

    change_pct < -10%  -> 95  (rates falling sharply — charter now, lock in current)
    -10% to -5%        -> 80
    -5%  to  0%        -> 65
     0%  to  5%        -> 45
     5%  to 10%        -> 30
    > 10%              -> 15  (rates rising sharply — wait for peak to pass)
    """
    if change_pct < -10:
        return 95.0
    elif change_pct < -5:
        return 80.0
    elif change_pct < 0:
        return 65.0
    elif change_pct < 5:
        return 45.0
    elif change_pct < 10:
        return 30.0
    else:
        return 15.0


def _economics_score(
    cheapest_cost: Optional[float],
    all_costs: List[float],
) -> float:
    """
    Score vessel economics relative to median cost across all classes.
    Lower cost_per_mt = more favourable to charter.
    """
    if cheapest_cost is None or not all_costs:
        return 0.0
    median_cost = mean(all_costs)
    if median_cost == 0:
        return 50.0
    ratio = cheapest_cost / median_cost
    if ratio < 0.60:
        return 90.0
    elif ratio < 0.80:
        return 75.0
    elif ratio <= 1.00:
        return 60.0
    else:
        return 30.0


def _clamp(v: float, lo: float = 0.0, hi: float = 100.0) -> float:
    return max(lo, min(hi, v))


# ─────────────────────────────────────────────────────────────────────────────
# Decision Engine
# ─────────────────────────────────────────────────────────────────────────────

class DecisionEngine:
    """
    Integrates all upstream module outputs into a final charter decision.

    Usage:
        engine = DecisionEngine()
        result = engine.decide(
            market_intelligence=...,   # from _build_market_intelligence()
            port_operations=...,       # from _build_port_operations()
            risk_assessment=...,       # from _build_risk_assessment()
            vessel_economics=...,      # from _build_vessel_economics()
            recommended_vessel=...,    # from RecommendationEngine
            analysis_items=...,        # list of VesselAnalysisItem
        )
    """

    def decide(
        self,
        market_intelligence: Optional[Dict[str, Any]],
        port_operations: Optional[Dict[str, Any]],
        risk_assessment: Optional[Dict[str, Any]],
        vessel_economics: Optional[Dict[str, Any]],
        recommended_vessel: Optional[str],
        analysis_items: Optional[List[Any]] = None,
    ) -> DecisionResult:
        """
        Compute the integrated decision score and recommendation.

        All arguments are the already-serialised dicts returned by
        the Phase 2 / 3 helper functions in app/main.py.
        None means the upstream module could not produce a result.
        """

        factors: List[FactorScore] = []
        reasons: List[str] = []

        w = DECISION_WEIGHTS   # shorthand

        # ── FACTOR 1 — Freight Trend (weight 0.20) ───────────────────────────
        freight_score = self._factor_freight_trend(
            market_intelligence, w["freight_trend"], factors, reasons
        )

        # ── FACTOR 2 — BDI Trend (weight 0.15) ──────────────────────────────
        self._factor_bdi_trend(
            market_intelligence, w["bdi_trend"], factors, reasons
        )

        # ── FACTOR 3 — Oil Price Trend (weight 0.10) ─────────────────────────
        self._factor_oil_trend(
            market_intelligence, w["oil_trend"], factors, reasons
        )

        # ── FACTOR 4 — Commodity Trend (weight 0.10) ─────────────────────────
        self._factor_commodity_trend(
            market_intelligence, w["commodity_trend"], factors, reasons
        )

        # ── FACTOR 5 — Port Congestion (weight 0.15) ─────────────────────────
        self._factor_port_congestion(
            port_operations, w["port_congestion"], factors, reasons
        )

        # ── FACTOR 6 — Weather / Marine Risk (weight 0.15) ───────────────────
        self._factor_risk(
            risk_assessment, w["risk"], factors, reasons
        )

        # ── FACTOR 7 — Vessel Economics (weight 0.15) ────────────────────────
        feasible_vessel_available = self._factor_vessel_economics(
            vessel_economics, recommended_vessel, w["vessel_economics"],
            factors, reasons
        )

        # ── Overall Score ───────────────────────────────────────────────────
        overall = _clamp(sum(f.contribution for f in factors))
        overall = round(overall, 2)

        # ── Decision Action ─────────────────────────────────────────────────
        if overall >= DECISION_CHARTER_THRESHOLD:
            action = "CHARTER NOW"
        elif overall >= DECISION_NEGOTIATE_THRESHOLD:
            action = "NEGOTIATE"
        else:
            action = "WAIT"

        reasons.append(
            f"Overall decision score: {overall:.1f}/100 "
            f"(threshold: ≥{DECISION_CHARTER_THRESHOLD} → CHARTER NOW, "
            f"≥{DECISION_NEGOTIATE_THRESHOLD} → NEGOTIATE, "
            f"<{DECISION_NEGOTIATE_THRESHOLD} → WAIT)."
        )

        # ── Confidence ──────────────────────────────────────────────────────
        factors_available = sum(1 for f in factors if f.data_available)
        model_r2 = self._extract_r2(market_intelligence)
        confidence, conf_rationale = self._confidence(
            factors_available, feasible_vessel_available, model_r2
        )

        # ── No Feasible Vessel Override ──────────────────────────────────────
        if not feasible_vessel_available:
            # Cannot charter if no vessel can physically make the voyage
            if action == "CHARTER NOW":
                action = "NEGOTIATE"
                reasons.append(
                    "Action downgraded from CHARTER NOW to NEGOTIATE: "
                    "no vessel class currently passes all feasibility checks."
                )

        return DecisionResult(
            action=action,
            confidence=confidence,
            overall_score=overall,
            recommended_vessel=recommended_vessel,
            feasible_vessel_available=feasible_vessel_available,
            factor_scores=factors,
            factors_available=factors_available,
            factors_total=7,
            reasons=reasons,
            confidence_rationale=conf_rationale,
            data_source=MARKET_DATA_SOURCE,
        )

    # ─────────────────────────────────────────────────────────────────────────
    # Factor builders
    # ─────────────────────────────────────────────────────────────────────────

    def _factor_freight_trend(
        self,
        mi: Optional[Dict],
        weight: float,
        factors: List[FactorScore],
        reasons: List[str],
    ) -> Optional[float]:
        """Factor 1: Freight Trend based on ML forecast direction."""
        try:
            ff = mi["freight_forecast"]
            change_pct = float(ff["forecast_change_percent"])
            direction = str(ff["forecast_direction"])
            score = _clamp(_freight_trend_score(change_pct))
            contribution = round(score * weight, 3)
            signal = (
                f"Freight rates forecast to move {direction} "
                f"({change_pct:+.1f}% over 30d) — "
                + ("charter now to lock in current rate." if change_pct <= 0
                   else "rates rising, consider waiting.")
            )
            reasons.append(f"[Freight Trend] {signal}")
            factors.append(FactorScore(
                factor_name="freight_trend",
                raw_value=round(change_pct, 2),
                raw_label=direction,
                score=round(score, 1),
                weight=weight,
                contribution=contribution,
                signal=signal,
                data_available=True,
            ))
            return change_pct
        except (TypeError, KeyError, ValueError):
            # Freight data unavailable — use neutral
            score = 50.0
            contribution = round(score * weight, 3)
            factors.append(FactorScore(
                factor_name="freight_trend",
                raw_value=None,
                raw_label=None,
                score=score,
                weight=weight,
                contribution=contribution,
                signal="Freight forecast unavailable — neutral score applied.",
                data_available=False,
            ))
            return None

    def _factor_bdi_trend(
        self,
        mi: Optional[Dict],
        weight: float,
        factors: List[FactorScore],
        reasons: List[str],
    ) -> None:
        """Factor 2: Baltic Dry Index trend direction."""
        try:
            bdi = mi["market_snapshot"]["bdi"]
            direction = str(bdi["direction"])
            current_val = float(bdi["current_value"])
            change_pct = float(bdi["change_percent"])
            score = _clamp(_direction_to_score_bullish(direction))
            contribution = round(score * weight, 3)
            signal = (
                f"BDI is {direction} ({current_val:.0f}, {change_pct:+.1f}%) — "
                + ("favourable for chartering." if direction == "down"
                   else "rising index suggests higher future costs." if direction == "up"
                   else "stable index, neutral signal.")
            )
            reasons.append(f"[BDI Trend] {signal}")
            factors.append(FactorScore(
                factor_name="bdi_trend",
                raw_value=round(change_pct, 2),
                raw_label=direction,
                score=round(score, 1),
                weight=weight,
                contribution=contribution,
                signal=signal,
                data_available=True,
            ))
        except (TypeError, KeyError, ValueError):
            factors.append(FactorScore(
                factor_name="bdi_trend",
                raw_value=None, raw_label=None,
                score=50.0, weight=weight,
                contribution=round(50.0 * weight, 3),
                signal="BDI data unavailable — neutral score.",
                data_available=False,
            ))

    def _factor_oil_trend(
        self,
        mi: Optional[Dict],
        weight: float,
        factors: List[FactorScore],
        reasons: List[str],
    ) -> None:
        """Factor 3: Oil price trend direction."""
        try:
            oil = mi["market_snapshot"]["oil_price"]
            direction = str(oil["direction"])
            current_val = float(oil["current_value"])
            change_pct = float(oil["change_percent"])
            score = _clamp(_direction_to_score_bullish(direction))
            contribution = round(score * weight, 3)
            signal = (
                f"WTI oil at ${current_val:.1f}/bbl, {direction} ({change_pct:+.1f}%) — "
                + ("lower bunker costs support chartering." if direction == "down"
                   else "rising oil increases voyage costs — consider delay." if direction == "up"
                   else "stable oil prices, neutral impact.")
            )
            reasons.append(f"[Oil Price] {signal}")
            factors.append(FactorScore(
                factor_name="oil_trend",
                raw_value=round(change_pct, 2),
                raw_label=direction,
                score=round(score, 1),
                weight=weight,
                contribution=contribution,
                signal=signal,
                data_available=True,
            ))
        except (TypeError, KeyError, ValueError):
            factors.append(FactorScore(
                factor_name="oil_trend",
                raw_value=None, raw_label=None,
                score=50.0, weight=weight,
                contribution=round(50.0 * weight, 3),
                signal="Oil price data unavailable — neutral score.",
                data_available=False,
            ))

    def _factor_commodity_trend(
        self,
        mi: Optional[Dict],
        weight: float,
        factors: List[FactorScore],
        reasons: List[str],
    ) -> None:
        """Factor 4: Commodity price trend for the cargo type."""
        try:
            comm = mi["market_snapshot"]["commodity_price"]
            if comm is None:
                raise ValueError("No commodity indicator")
            direction = str(comm["direction"])
            current_val = float(comm["current_value"])
            change_pct = float(comm["change_percent"])
            score = _clamp(_direction_to_score_commodity(direction))
            contribution = round(score * weight, 3)
            signal = (
                f"Commodity price {direction} (${current_val:.1f}/t, {change_pct:+.1f}%) — "
                + ("rising prices increase shipping urgency — charter now." if direction == "up"
                   else "falling commodity softens shipping demand." if direction == "down"
                   else "stable commodity market.")
            )
            reasons.append(f"[Commodity] {signal}")
            factors.append(FactorScore(
                factor_name="commodity_trend",
                raw_value=round(change_pct, 2),
                raw_label=direction,
                score=round(score, 1),
                weight=weight,
                contribution=contribution,
                signal=signal,
                data_available=True,
            ))
        except (TypeError, KeyError, ValueError):
            factors.append(FactorScore(
                factor_name="commodity_trend",
                raw_value=None, raw_label=None,
                score=50.0, weight=weight,
                contribution=round(50.0 * weight, 3),
                signal="Commodity data unavailable for this cargo type — neutral score.",
                data_available=False,
            ))

    def _factor_port_congestion(
        self,
        po: Optional[Dict],
        weight: float,
        factors: List[FactorScore],
        reasons: List[str],
    ) -> None:
        """Factor 5: Port congestion — worst of origin/destination."""
        try:
            # Use worst (highest) congestion score between origin and destination
            scores: List[float] = []
            for key in ("origin", "destination"):
                port = po.get(key)
                if port and port.get("congestion_score") is not None:
                    scores.append(float(port["congestion_score"]))

            if not scores:
                raise ValueError("No congestion scores available")

            worst_congestion = max(scores)
            congestion_level = po.get("combined_delay_risk", "UNKNOWN")
            # Invert: low congestion = high charter score
            score = _clamp(100.0 - worst_congestion)
            contribution = round(score * weight, 3)
            signal = (
                f"Port congestion: {congestion_level} (worst score {worst_congestion:.0f}/100) — "
                + ("low congestion, good timing for vessel arrival." if worst_congestion < 45
                   else "high congestion may cause delays, negotiate berth guarantees."
                   if worst_congestion >= 65 else "moderate congestion, plan buffer time.")
            )
            reasons.append(f"[Port Congestion] {signal}")
            factors.append(FactorScore(
                factor_name="port_congestion",
                raw_value=round(worst_congestion, 1),
                raw_label=congestion_level,
                score=round(score, 1),
                weight=weight,
                contribution=contribution,
                signal=signal,
                data_available=True,
            ))
        except (TypeError, KeyError, ValueError, AttributeError):
            factors.append(FactorScore(
                factor_name="port_congestion",
                raw_value=None, raw_label=None,
                score=50.0, weight=weight,
                contribution=round(50.0 * weight, 3),
                signal="Port congestion data unavailable — neutral score.",
                data_available=False,
            ))

    def _factor_risk(
        self,
        ra: Optional[Dict],
        weight: float,
        factors: List[FactorScore],
        reasons: List[str],
    ) -> None:
        """Factor 6: Weather + marine risk — inverted (lower risk = better to charter)."""
        try:
            risk_score = float(ra["overall_risk_score"])
            risk_level = str(ra["risk_level"])
            # Invert: low risk = high charter score
            score = _clamp(100.0 - risk_score)
            contribution = round(score * weight, 3)
            hazards = ra.get("key_hazards", [])
            hazard_str = "; ".join(hazards[:2]) if hazards else "none identified"
            signal = (
                f"Route risk: {risk_level} (score {risk_score:.0f}/100). "
                f"Key hazards: {hazard_str}. "
                + ("Low risk window — safe to charter now." if risk_score < 40
                   else "Significant risk — negotiate weather clauses or wait for safer window."
                   if risk_score >= 60 else "Moderate risk — standard maritime precautions advised.")
            )
            reasons.append(f"[Weather/Marine Risk] {signal}")
            factors.append(FactorScore(
                factor_name="risk",
                raw_value=round(risk_score, 1),
                raw_label=risk_level,
                score=round(score, 1),
                weight=weight,
                contribution=contribution,
                signal=signal,
                data_available=True,
            ))
        except (TypeError, KeyError, ValueError):
            factors.append(FactorScore(
                factor_name="risk",
                raw_value=None, raw_label=None,
                score=50.0, weight=weight,
                contribution=round(50.0 * weight, 3),
                signal="Risk assessment data unavailable — neutral score.",
                data_available=False,
            ))

    def _factor_vessel_economics(
        self,
        ve: Optional[Dict],
        recommended_vessel: Optional[str],
        weight: float,
        factors: List[FactorScore],
        reasons: List[str],
    ) -> bool:
        """
        Factor 7: Vessel economics — cheapest feasible cost vs median.
        Returns True if at least one feasible vessel is available.
        """
        try:
            comparison = ve.get("comparison", [])
            feasible = [
                c for c in comparison
                if c.get("feasibility_status") in ("feasible", "conditionally_feasible")
            ]
            all_costs = [float(c["cost_per_mt_usd"]) for c in comparison if c.get("cost_per_mt_usd")]
            cheapest_name = ve.get("cheapest_feasible_vessel")
            cheapest_cost: Optional[float] = None
            if cheapest_name:
                for c in comparison:
                    if c.get("vessel_class", "").lower() == cheapest_name.lower():
                        cheapest_cost = float(c["cost_per_mt_usd"])
                        break

            feasible_available = len(feasible) > 0
            score = _clamp(_economics_score(cheapest_cost, all_costs))
            if not feasible_available:
                score = 0.0

            contribution = round(score * weight, 3)

            if cheapest_cost is not None and feasible_available:
                signal = (
                    f"Cheapest feasible vessel: {cheapest_name} "
                    f"at ${cheapest_cost:.2f}/MT. "
                    + ("Highly cost-efficient voyage economics." if score >= 75
                       else "Acceptable voyage economics.")
                )
            elif not feasible_available:
                signal = "No feasible vessel found — economics score = 0."
            else:
                signal = "Vessel economics data available but cheapest vessel undetermined."

            reasons.append(f"[Vessel Economics] {signal}")
            factors.append(FactorScore(
                factor_name="vessel_economics",
                raw_value=round(cheapest_cost, 4) if cheapest_cost else None,
                raw_label=cheapest_name,
                score=round(score, 1),
                weight=weight,
                contribution=contribution,
                signal=signal,
                data_available=feasible_available or cheapest_cost is not None,
            ))
            return feasible_available

        except (TypeError, KeyError, ValueError, AttributeError):
            factors.append(FactorScore(
                factor_name="vessel_economics",
                raw_value=None, raw_label=None,
                score=0.0, weight=weight,
                contribution=0.0,
                signal="Vessel economics unavailable — score = 0.",
                data_available=False,
            ))
            return False

    # ─────────────────────────────────────────────────────────────────────────
    # Confidence
    # ─────────────────────────────────────────────────────────────────────────

    def _confidence(
        self,
        factors_available: int,
        feasible_vessel: bool,
        model_r2: Optional[float],
    ) -> tuple[str, str]:
        """Determine confidence level and rationale."""
        good_model = model_r2 is None or model_r2 >= 0.70

        if factors_available == 7 and feasible_vessel and good_model:
            return (
                "HIGH",
                (
                    f"All 7 factors available, feasible vessel confirmed"
                    + (f", ML model R²={model_r2:.2f}" if model_r2 is not None else "")
                    + "."
                ),
            )
        elif factors_available >= 5 and feasible_vessel:
            missing = 7 - factors_available
            return (
                "MODERATE",
                (
                    f"{factors_available}/7 factors available"
                    + (f" (ML R²={model_r2:.2f})" if model_r2 is not None else "")
                    + f", feasible vessel confirmed. {missing} factor(s) missing reduces certainty."
                ),
            )
        else:
            rationale_parts = []
            if factors_available < 5:
                rationale_parts.append(f"only {factors_available}/7 factors available")
            if not feasible_vessel:
                rationale_parts.append("no feasible vessel identified")
            if model_r2 is not None and model_r2 < 0.70:
                rationale_parts.append(f"ML model R²={model_r2:.2f} below 0.70")
            return (
                "LOW",
                "Low confidence: " + "; ".join(rationale_parts) + ".",
            )

    # ─────────────────────────────────────────────────────────────────────────
    # Helpers
    # ─────────────────────────────────────────────────────────────────────────

    def _extract_r2(self, mi: Optional[Dict]) -> Optional[float]:
        """Safely extract ML model R² from market intelligence dict."""
        try:
            return float(mi["model_evaluation"]["r2"])
        except (TypeError, KeyError, ValueError):
            return None


# Global singleton
default_decision_engine = DecisionEngine()
