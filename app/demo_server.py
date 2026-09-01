"""Demo web server and interactive API for the Shipping & Vessel Intelligence Engine."""

from pathlib import Path
from typing import Any, Dict, List, Optional
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field
import uvicorn

from app.main import analyze_shipping_request
from app.services.data_loader import default_data_loader
from config import BASE_DIR

app = FastAPI(
    title="Shipping & Vessel Intelligence Engine API",
    description="Maritime decision support engine evaluating vessel feasibility, port limits, and route estimates.",
    version="1.0.0",
)

TEMPLATE_PATH = BASE_DIR / "templates" / "index.html"


class AnalyzeRequestPayload(BaseModel):
    cargo_type: str = Field(..., example="iron_ore")
    cargo_quantity_tonnes: float = Field(..., example=75000)
    origin_port: str = Field(..., example="Paradip")
    destination_port: str = Field(..., example="Rotterdam")
    shipping_deadline_days: Optional[float] = Field(None, example=30)


@app.get("/", response_class=HTMLResponse)
def serve_dashboard():
    """Serve the interactive decision intelligence dashboard UI."""
    if not TEMPLATE_PATH.exists():
        raise HTTPException(status_code=404, detail="Dashboard template not found.")
    with open(TEMPLATE_PATH, "r", encoding="utf-8") as f:
        return HTMLResponse(content=f.read())


@app.post("/api/analyze")
def api_analyze(payload: AnalyzeRequestPayload) -> Dict[str, Any]:
    """Execute complete vessel feasibility, scoring, recommendation, and route analysis."""
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


def run_demo(host: str = "127.0.0.1", port: int = 8000) -> None:
    """Launch the demo server locally."""
    print(f"\n=======================================================")
    print(f"🚢 Shipping & Vessel Intelligence Engine Demo Running")
    print(f"👉 Open in browser: http://{host}:{port}")
    print(f"📖 Swagger API Docs: http://{host}:{port}/docs")
    print(f"=======================================================\n")
    uvicorn.run(app, host=host, port=port)


if __name__ == "__main__":
    run_demo()
