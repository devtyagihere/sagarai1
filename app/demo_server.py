"""Demo web server and interactive API for the Shipping & Vessel Intelligence Engine."""

from pathlib import Path
from typing import Any, Dict, List, Optional
from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field
import uvicorn

from app.main import analyze_shipping_request
from app.services.data_loader import default_data_loader
from config import BASE_DIR

# Phase 2 — market services (graceful import)
try:
    from app.services.market_service import default_market_service
    from app.services.freight_forecasting import default_forecasting_service
    _MARKET_AVAILABLE = True
except ImportError:
    _MARKET_AVAILABLE = False

# Phase 3 — port ops, risk, economics (graceful import)
try:
    from app.services.port_operations import default_port_ops_service
    from app.services.risk_service import default_risk_service
    from app.services.vessel_economics import default_vessel_economics_service
    _PHASE3_AVAILABLE = True
except ImportError:
    _PHASE3_AVAILABLE = False

app = FastAPI(
    title="Shipping & Vessel Intelligence Engine API",
    description=(
        "Maritime decision support engine: vessel feasibility, port limits, "
        "route estimation, market data (BDI/oil), ML freight rate forecasting, "
        "port congestion, risk scoring, and vessel economics."
    ),
    version="3.0.0",
)

TEMPLATE_PATH = BASE_DIR / "templates" / "index.html"


class AnalyzeRequestPayload(BaseModel):
    cargo_type: str = Field(..., example="iron_ore")
    cargo_quantity_tonnes: float = Field(..., example=75000)
    origin_port: str = Field(..., example="Paradip")
    destination_port: str = Field(..., example="Rotterdam")
    shipping_deadline_days: Optional[float] = Field(None, example=30)


# ──────────────────────────────────────────────────────────────────────────────
# EXISTING ENDPOINTS (Phase 1 — unchanged)
# ──────────────────────────────────────────────────────────────────────────────

@app.get("/", response_class=HTMLResponse)
def serve_dashboard():
    """Serve the interactive decision intelligence dashboard UI."""
    if not TEMPLATE_PATH.exists():
        raise HTTPException(status_code=404, detail="Dashboard template not found.")
    with open(TEMPLATE_PATH, "r", encoding="utf-8") as f:
        return HTMLResponse(content=f.read())


@app.post("/api/analyze")
def api_analyze(payload: AnalyzeRequestPayload) -> Dict[str, Any]:
    """Execute complete vessel feasibility, scoring, recommendation, route analysis, and market intelligence."""
    try:
        result = analyze_shipping_request(
            cargo_type=payload.cargo_type,
            cargo_quantity_tonnes=payload.cargo_quantity_tonnes,
            origin_port=payload.origin_port,
            destination_port=payload.destination_port,
            shipping_deadline_days=payload.shipping_deadline_days,
        )
        return result
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@app.get("/api/ports")
def get_ports() -> List[dict]:
    """List all registered loading and discharge ports with verified constraints."""
    default_data_loader.load_all()
    ports = default_data_loader.get_all_ports()
    return [p.model_dump() for p in ports]


@app.get("/api/vessels")
def get_vessels() -> List[dict]:
    """List all vessel classes and their physical parameters."""
    default_data_loader.load_all()
    vessels = default_data_loader.get_vessels()
    return [v.model_dump() for v in vessels]


@app.get("/api/cargo-types")
def get_cargo_types() -> List[dict]:
    """List all registered cargo types and classification rules."""
    default_data_loader.load_all()
    return default_data_loader.get_all_cargo_types()


# ──────────────────────────────────────────────────────────────────────────────
# PHASE 2 ENDPOINTS — Market Data & Freight Forecasting
# ──────────────────────────────────────────────────────────────────────────────

def _check_market_available() -> None:
    if not _MARKET_AVAILABLE:
        raise HTTPException(
            status_code=503,
            detail="Market data services unavailable. Ensure scikit-learn is installed and market CSVs are present.",
        )


@app.get("/api/market/snapshot")
def get_market_snapshot(
    cargo_type: Optional[str] = Query(None, description="Optional cargo type for commodity price (e.g. iron_ore)")
) -> Dict[str, Any]:
    """
    Return current market snapshot: BDI, WTI oil price, and optional commodity price.

    DATA DISCLAIMER: All data is SYNTHETIC — generated for educational purposes only.
    """
    _check_market_available()
    try:
        snapshot = default_market_service.get_market_snapshot(cargo_type)
        return snapshot.model_dump()
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Market data error: {exc}")


@app.get("/api/market/bdi")
def get_bdi() -> Dict[str, Any]:
    """
    Return Baltic Dry Index (BDI) indicator with trend, direction and % change.

    DATA DISCLAIMER: SYNTHETIC data — not real trading data.
    """
    _check_market_available()
    try:
        bdi = default_market_service.get_bdi_indicator()
        return bdi.model_dump()
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"BDI data error: {exc}")


@app.get("/api/market/forecast")
def get_freight_forecast(
    origin: str = Query(..., description="Origin port (e.g. Paradip)"),
    destination: str = Query(..., description="Destination port (e.g. Rotterdam)"),
    cargo_type: str = Query(..., description="Cargo type (e.g. iron_ore)"),
    vessel_type: str = Query("Panamax", description="Vessel class (e.g. Panamax)"),
    distance_nm: float = Query(4800.0, description="Route distance in nautical miles"),
) -> Dict[str, Any]:
    """
    Generate ML freight rate forecast for 7 / 15 / 30 day horizons using Random Forest.

    Model is trained on SYNTHETIC historical data. Returns current rate + forecasts + direction.

    DATA DISCLAIMER: SYNTHETIC training data. Not suitable for real commercial decisions.
    """
    _check_market_available()
    try:
        # Ensure model is trained
        default_forecasting_service.train()
        forecast = default_forecasting_service.forecast(
            origin=origin,
            destination=destination,
            cargo_type=cargo_type,
            vessel_type=vessel_type,
            distance_nm=distance_nm,
        )
        if forecast is None:
            raise HTTPException(status_code=422, detail="Unable to generate forecast: insufficient training data.")
        return forecast.model_dump()
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Forecast error: {exc}")


@app.get("/api/market/model-evaluation")
def get_model_evaluation() -> Dict[str, Any]:
    """
    Return honest ML model evaluation metrics (MAE, RMSE, R²) from holdout test set.

    Model: RandomForestRegressor trained on SYNTHETIC freight history.
    Metrics reflect synthetic data patterns only.
    """
    _check_market_available()
    try:
        evaluation = default_forecasting_service.train()
        return evaluation.model_dump()
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Model evaluation error: {exc}")


# ──────────────────────────────────────────────────────────────────────────────
# PHASE 3 ENDPOINTS — Port Operations, Risk, Vessel Economics
# ──────────────────────────────────────────────────────────────────────────────

def _check_phase3_available() -> None:
    if not _PHASE3_AVAILABLE:
        raise HTTPException(
            status_code=503,
            detail="Phase 3 services unavailable. Check port_operations.csv and service imports.",
        )


@app.get("/api/port-operations/{port_name}")
def get_port_congestion(port_name: str) -> Dict[str, Any]:
    """
    Return operational congestion metrics for a specific port.

    Distinction: This shows OPERATIONAL congestion (vessels waiting, avg wait time).
    Physical constraints (draft/LOA) are handled by /api/analyze feasibility.

    DATA: SYNTHETIC — labeled throughout.
    """
    _check_phase3_available()
    try:
        result = default_port_ops_service.get_port_congestion(port_name)
        if result is None:
            raise HTTPException(
                status_code=404,
                detail=f"Port '{port_name}' not found in operations dataset."
            )
        return result.model_dump()
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Port operations error: {exc}")


@app.get("/api/port-operations")
def get_all_port_congestion() -> List[Dict[str, Any]]:
    """
    Return operational congestion metrics for all ports in the dataset.

    DATA: SYNTHETIC — labeled throughout.
    """
    _check_phase3_available()
    try:
        ports = default_port_ops_service.all_ports()
        # Enrich with congestion_level classification
        results = []
        for p in ports:
            cong = default_port_ops_service.get_port_congestion(str(p["port_name"]))
            if cong:
                results.append(cong.model_dump())
        return results
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Port operations error: {exc}")


@app.get("/api/risk")
def get_route_risk(
    origin: str = Query(..., description="Origin port name"),
    destination: str = Query(..., description="Destination port name"),
) -> Dict[str, Any]:
    """
    Compute weather and marine risk score for the route (0-100 scale).

    Risk levels: LOW / LOW-MODERATE / MODERATE / HIGH / VERY HIGH

    Formula documented in RiskService.
    DATA: SYNTHETIC — formula-based with regional parameters.
    """
    _check_phase3_available()
    try:
        result = default_risk_service.assess(origin, destination)
        return result.model_dump()
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Risk assessment error: {exc}")


@app.get("/api/vessel-economics")
def get_vessel_economics(
    origin: str = Query(..., description="Origin port"),
    destination: str = Query(..., description="Destination port"),
    cargo_type: str = Query(..., description="Cargo type (e.g. iron_ore)"),
    cargo_quantity_tonnes: float = Query(..., description="Cargo quantity in metric tonnes"),
    shipping_deadline_days: Optional[float] = Query(None, description="Optional deadline in days"),
) -> Dict[str, Any]:
    """
    Return voyage cost comparison across all vessel classes for the given route.

    Formulas:
      voyage_cost = daily_rate_usd × voyage_days
      cost_per_mt = voyage_cost / cargo_quantity_tonnes

    Only feasible vessels are recommended. Incompatible vessels shown with status=NOT_FEASIBLE.

    DATA: Daily rates are SYNTHETIC indicative values.
    """
    _check_phase3_available()
    try:
        from app.main import analyze_shipping_request
        result = analyze_shipping_request(
            cargo_type=cargo_type,
            cargo_quantity_tonnes=cargo_quantity_tonnes,
            origin_port=origin,
            destination_port=destination,
            shipping_deadline_days=shipping_deadline_days,
        )
        economics = result.get("vessel_economics")
        if economics is None:
            raise HTTPException(status_code=422, detail="Could not compute vessel economics.")
        return economics
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc))


def run_demo(host: str = "127.0.0.1", port: int = 8000) -> None:
    """Launch the demo server locally."""
    print(f"\n=======================================================")
    print(f"🚢 Shipping & Vessel Intelligence Engine v3.0")
    print(f"👉 Open in browser: http://{host}:{port}")
    print(f"📖 Swagger API Docs: http://{host}:{port}/docs")
    print(f"=======================================================\n")
    uvicorn.run(app, host=host, port=port)


if __name__ == "__main__":
    run_demo()
