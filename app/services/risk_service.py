"""
Weather & Marine Risk Service.

SCALE: 0 = very low risk → 100 = very high risk.

CLASSIFICATION:
   0 – 20  → LOW
  20 – 40  → LOW-MODERATE
  40 – 60  → MODERATE
  60 – 75  → HIGH
  75 – 100 → VERY HIGH

WEATHER RISK FORMULA:
  wind_score       = (wind_speed_bft / 12.0) × 100
  wave_score       = (wave_height_m  / 10.0) × 100   [10m = Beaufort 12 sea]
  storm_score      = storm_probability_pct              [0-100%]
  weather_risk     = wind_score × 0.35 + wave_score × 0.35 + storm_score × 0.30
  clamped [0,100]

MARINE RISK FORMULA:
  cyclone_score    = cyclone_risk_pct                   [0-100%]
  env_score        = environmental_sensitivity           [0-100]
  sea_state_score  = wmo_sea_state × (100/9)            [WMO 0-9 → 0-100]
  marine_risk      = cyclone_score × 0.50 + env_score × 0.25 + sea_state_score × 0.25
  clamped [0,100]

COMBINED:
  overall_risk = weather_risk × 0.55 + marine_risk × 0.45
  clamped [0,100]

REGION PROFILES: Based on known maritime geography.
  - Bay of Bengal: high cyclone risk (Jun-Nov), monsoon swell
  - South China Sea / Western Pacific: typhoon risk (Jun-Oct)
  - North Atlantic / North Sea: winter storm risk (Nov-Mar)
  - Indian Ocean (southern): moderate year-round
  - Other/generic: low-moderate

DATA: Formula-based with regional parameters — SYNTHETIC/DEMO.
      Not connected to live weather APIs.
"""

from datetime import date
from typing import List, Optional, Tuple

from app.models.operations import MarineRisk, RiskAssessment, WeatherRisk
from config import (
    RISK_LOW_THRESHOLD, RISK_LOW_MODERATE_THRESHOLD,
    RISK_MODERATE_THRESHOLD, RISK_HIGH_THRESHOLD,
    MARKET_DATA_SOURCE,
)

# ── Region classification ─────────────────────────────────────────────────────
# Map lower-case port names to maritime region codes
_PORT_REGION: dict = {
    # Bay of Bengal
    "paradip": "bay_of_bengal", "visakhapatnam": "bay_of_bengal",
    "gangavaram": "bay_of_bengal", "gopalpur": "bay_of_bengal",
    "dhamra": "bay_of_bengal", "haldia": "bay_of_bengal",
    "sagar-sandheads": "bay_of_bengal",
    # South China Sea / Western Pacific
    "singapore": "south_china_sea", "qingdao": "south_china_sea",
    "shanghai": "south_china_sea", "samarinda": "south_china_sea",
    "tanjung bara": "south_china_sea",
    # North Atlantic / North Sea
    "rotterdam": "north_atlantic", "baltimore": "north_atlantic",
    "norfolk": "north_atlantic", "ust-luga": "north_atlantic",
    # Australia / South Indian Ocean
    "port hedland": "south_indian_ocean", "newcastle": "south_indian_ocean",
    "hay point": "south_indian_ocean",
    # East Africa
    "maputo": "east_africa", "richards bay": "east_africa",
    # Far East / North Pacific
    "vostochny": "north_pacific",
    # Demo/unknown ports default to "generic"
}

def _region(port: str) -> str:
    return _PORT_REGION.get(port.strip().lower(), "generic")

# ── Monthly seasonal modifiers per region ─────────────────────────────────────
# Values are (wind_bft_base, wave_m_base, storm_prob_base, cyclone_risk_base)
_REGION_BASE: dict = {
    "bay_of_bengal":   (5.0, 2.5, 30.0, 45.0, 60.0, 6),   # wind,wave,storm,cyclone,env,wmo
    "south_china_sea": (4.5, 2.0, 25.0, 40.0, 55.0, 5),
    "north_atlantic":  (5.5, 3.0, 35.0, 5.0,  30.0, 6),
    "south_indian_ocean":(4.0, 2.0, 20.0, 15.0, 50.0, 4),
    "east_africa":     (3.5, 1.5, 15.0, 10.0, 65.0, 4),
    "north_pacific":   (4.0, 2.0, 20.0, 8.0,  35.0, 4),
    "generic":         (3.0, 1.5, 10.0, 5.0,  25.0, 3),
}

# Monthly multipliers for storm/cyclone:  Jan-Dec (index 1-12)
_STORM_SEASONAL = {
    "bay_of_bengal":   [0.3,0.2,0.3,0.4,0.7,0.9,1.0,1.0,1.0,0.8,0.7,0.4],
    "south_china_sea": [0.4,0.3,0.3,0.4,0.6,0.9,1.0,1.0,0.9,0.7,0.5,0.4],
    "north_atlantic":  [1.0,0.9,0.8,0.5,0.4,0.3,0.2,0.2,0.4,0.7,0.9,1.0],
    "south_indian_ocean":[0.5,0.5,0.4,0.3,0.2,0.2,0.2,0.2,0.3,0.3,0.4,0.5],
    "east_africa":     [0.3,0.3,0.4,0.5,0.4,0.3,0.3,0.3,0.4,0.5,0.4,0.3],
    "north_pacific":   [0.5,0.4,0.4,0.4,0.5,0.7,0.9,1.0,0.9,0.7,0.5,0.5],
    "generic":         [0.4,0.4,0.4,0.4,0.5,0.6,0.7,0.7,0.6,0.5,0.4,0.4],
}


def _classify_risk(score: float) -> str:
    if score < RISK_LOW_THRESHOLD:           return "LOW"
    if score < RISK_LOW_MODERATE_THRESHOLD:  return "LOW-MODERATE"
    if score < RISK_MODERATE_THRESHOLD:      return "MODERATE"
    if score < RISK_HIGH_THRESHOLD:          return "HIGH"
    return "VERY HIGH"

def _clamp(v: float, lo: float = 0.0, hi: float = 100.0) -> float:
    return max(lo, min(hi, v))


class RiskService:
    """
    Computes weather and marine risk for a maritime route.

    Inputs: origin port name, destination port name, optional assessment date.
    Output: RiskAssessment with documented formula breakdown.

    Data is SYNTHETIC/formula-based. No live weather API is queried.
    """

    def assess(
        self,
        origin: str,
        destination: str,
        assessment_date: Optional[date] = None,
    ) -> RiskAssessment:
        """Compute full risk assessment for the route origin → destination."""
        today = assessment_date or date.today()
        month_idx = today.month - 1   # 0-based for list lookup

        # Identify regions for both endpoints
        r_orig = _region(origin)
        r_dest = _region(destination)

        # Use the higher-risk region to drive assessment (conservative)
        region = self._higher_risk_region(r_orig, r_dest)
        base   = _REGION_BASE[region]
        wind_b, wave_b, storm_b, cyclone_b, env_b, wmo_b = base

        # Apply seasonal multiplier
        s_mult = _STORM_SEASONAL[region][month_idx]

        wind_bft    = _clamp(wind_b  * (0.8 + 0.4 * s_mult), 0, 12)
        wave_m      = _clamp(wave_b  * (0.8 + 0.4 * s_mult), 0, 10)
        storm_pct   = _clamp(storm_b * s_mult, 0, 100)
        cyclone_pct = _clamp(cyclone_b * s_mult, 0, 100)
        env_sens    = _clamp(env_b, 0, 100)
        wmo_state   = min(9, int(wmo_b * (0.8 + 0.3 * s_mult)))

        # ── Weather risk ──────────────────────────────────────────────────────
        wind_score  = (wind_bft / 12.0) * 100.0
        wave_score  = (wave_m   / 10.0) * 100.0
        storm_score = storm_pct
        weather_risk_score = _clamp(
            wind_score * 0.35 + wave_score * 0.35 + storm_score * 0.30
        )

        # ── Marine risk ───────────────────────────────────────────────────────
        sea_state_score = (wmo_state / 9.0) * 100.0
        marine_risk_score = _clamp(
            cyclone_pct * 0.50 + env_sens * 0.25 + sea_state_score * 0.25
        )

        # ── Overall ───────────────────────────────────────────────────────────
        overall = _clamp(weather_risk_score * 0.55 + marine_risk_score * 0.45)

        # ── Key hazards ───────────────────────────────────────────────────────
        hazards = self._build_hazards(
            wind_bft, wave_m, storm_pct, cyclone_pct, env_sens, wmo_state
        )

        wmo_descriptors = [
            "Calm (glassy)", "Calm (rippled)", "Smooth", "Slight",
            "Moderate", "Rough", "Very rough", "High", "Very high", "Phenomenal"
        ]

        formula_note = (
            "weather_risk = wind_score×0.35 + wave_score×0.35 + storm_score×0.30; "
            "marine_risk = cyclone×0.50 + env×0.25 + sea_state×0.25; "
            "overall = weather×0.55 + marine×0.45"
        )

        return RiskAssessment(
            route=f"{origin} → {destination}",
            month_assessed=today.strftime("%Y-%m"),
            weather_risk=WeatherRisk(
                wind_speed_bft=round(wind_bft, 1),
                wave_height_m=round(wave_m, 1),
                storm_probability_pct=round(storm_pct, 1),
                weather_risk_score=round(weather_risk_score, 1),
            ),
            marine_risk=MarineRisk(
                sea_state=wmo_descriptors[wmo_state],
                cyclone_risk_pct=round(cyclone_pct, 1),
                environmental_sensitivity=round(env_sens, 1),
                marine_risk_score=round(marine_risk_score, 1),
            ),
            overall_risk_score=round(overall, 1),
            risk_level=_classify_risk(overall),
            key_hazards=hazards,
            data_source=MARKET_DATA_SOURCE,
            formula_note=formula_note,
        )

    def _higher_risk_region(self, a: str, b: str) -> str:
        """Return whichever region has the higher base storm probability."""
        if _REGION_BASE[a][2] >= _REGION_BASE[b][2]:
            return a
        return b

    def _build_hazards(
        self, wind, wave, storm, cyclone, env, wmo
    ) -> List[str]:
        hazards = []
        if wind   >= 7:  hazards.append(f"Strong winds (Beaufort {wind:.0f})")
        if wave   >= 3:  hazards.append(f"Significant swell ({wave:.1f}m)")
        if storm  >= 30: hazards.append(f"Elevated storm probability ({storm:.0f}%)")
        if cyclone>= 25: hazards.append(f"Active cyclone/typhoon season ({cyclone:.0f}%)")
        if env    >= 50: hazards.append("High environmental sensitivity zone")
        if wmo    >= 6:  hazards.append(f"Rough sea state (WMO {wmo})")
        if not hazards:
            hazards.append("No significant hazards identified")
        return hazards


default_risk_service = RiskService()
