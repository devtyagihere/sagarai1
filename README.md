
# freight-intelligence
AI-powered freight forecasting and intelligent ship-booking decision platform

# React + Vite

This template provides a minimal setup to get React working in Vite with HMR and some Oxlint rules.

Currently, two official plugins are available:

- [@vitejs/plugin-react](https://github.com/vitejs/vite-plugin-react/blob/main/packages/plugin-react) uses [Oxc](https://oxc.rs)
- [@vitejs/plugin-react-swc](https://github.com/vitejs/vite-plugin-react/blob/main/packages/plugin-react-swc) uses [SWC](https://swc.rs/)

## React Compiler

The React Compiler is not enabled on this template because of its impact on dev & build performances. To add it, see [this documentation](https://react.dev/learn/react-compiler/installation).

## Expanding the Oxlint configuration

If you are developing a production application, we recommend using TypeScript with type-aware lint rules enabled. Check out the [TS template](https://github.com/vitejs/vite/tree/main/packages/create-vite/template-react-ts) for information on how to integrate TypeScript and Oxlint's TypeScript related rules in your project.

# AI-Powered Freight Booking Decision Intelligence Platform
## Module: Shipping & Vessel Intelligence Engine (Member 3)

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Pytest](https://img.shields.io/badge/pytest-passing-brightgreen.svg)](https://docs.pytest.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-Production%20Ready-009688.svg)](https://fastapi.tiangolo.com/)
[![License](https://img.shields.io/badge/license-MIT-purple.svg)](LICENSE)

---

## 📌 Project Overview & Role Scope

This module is a core domain engine of the **AI-Powered Freight Booking Decision Intelligence Platform** developed for Smart India Hackathon (SIH Problem Statement SIH26006 — Ministry of Steel). 

The platform aids bulk importers and exporters (such as SAIL) in deciding whether to **BOOK NOW**, **WAIT**, or **NEGOTIATE** maritime dry-bulk freight fixtures for overseas cargo movement to the East Coast of India.

### 🎯 Scope & Responsibilities (Member 3)
This module is strictly responsible for:
1. **Vessel Type Feasibility Engine**: Multi-dimensional capacity, draft, LOA, beam, and berth compatibility analysis.
2. **Cargo Compatibility Service**: Physical handling, stowage factor verification, and strict differentiation of dry bulk vs. geared break-bulk steel products.
3. **Port Constraint Analysis**: Dynamic evaluation of port limits (Paradip, Visakhapatnam, Gangavaram, Gopalpur, Dhamra, Haldia, Sagar-Sandheads, Rotterdam, etc.).
4. **Transparent Vessel Recommendation & Scoring**: Multi-factor weighted suitability ranking and justified operational reasoning.
5. **Route Distance & Voyage Duration Estimation**: Geodesic transit distance (Nautical Miles) and duration calculations.
6. **Data Quality & Verification Auditing**: Tracking data integrity (`verified`, `estimated`, `demo`, `missing`).

> ⚠️ **Out of Scope for this Module**: ML freight price forecasting, finding real-time available commercial spot fixtures, and the final macro BOOK/WAIT/NEGOTIATE timing decision engine.

---

## 🏗️ Architecture & Component Flow

```
                                  [ User / API Request ]
                                             │
                                             ▼
                               ┌───────────────────────────┐
                               │     ShippingRequest       │
                               │   (Pydantic Validation)   │
                               └─────────────┬─────────────┘
                                             │
                      ┌──────────────────────┼──────────────────────┐
                      ▼                      ▼                      ▼
             ┌─────────────────┐   ┌──────────────────┐   ┌──────────────────┐
             │   DataLoader    │   │  CargoService    │   │   RouteService   │
             │ vessels.csv     │   │ cargo_types.csv  │   │ Geodesic (NM)    │
             │ ports.csv       │   │ Steel Breakbulk  │   │ Voyage Duration  │
             └────────┬────────┘   └─────────┬────────┘   └─────────┬────────┘
                      │                      │                      │
                      └──────────────────────┼──────────────────────┘
                                             │
                                             ▼
                               ┌───────────────────────────┐
                               │     FeasibilityEngine     │
                               │  - Capacity & Utilization │
                               │  - Cargo Compatibility    │
                               │  - Origin Draft/LOA/Beam  │
                               │  - Dest Draft/LOA/Beam    │
                               └─────────────┬─────────────┘
                                             │
                                             ▼
                               ┌───────────────────────────┐
                               │       ScoringEngine       │
                               │  - Utilization (40%)      │
                               │  - Port Confidence (30%)  │
                               │  - Cargo Match (20%)      │
                               │  - Efficiency (10%)       │
                               └─────────────┬─────────────┘
                                             │
                                             ▼
                               ┌───────────────────────────┐
                               │   RecommendationEngine    │
                               │  - Prioritize FEASIBLE    │
                               │  - Rank by Score          │
                               │  - Structured Reasoning   │
                               └─────────────┬─────────────┘
                                             │
                                             ▼
                               ┌───────────────────────────┐
                               │     ShippingResponse      │
                               │ (JSON-Ready Output & API) │
                               └───────────────────────────┘
```

---

## 📁 Folder Structure

```text
Shipping/
├── app/
│   ├── __init__.py                  # Package exports
│   ├── main.py                      # Public API analyze_shipping_request & CLI
│   ├── demo_server.py               # FastAPI backend & interactive dashboard server
│   ├── models/
│   │   ├── __init__.py              # Model exports
│   │   ├── port.py                  # Port entity and constraints model
│   │   ├── vessel.py                # Vessel specifications and analysis schema
│   │   └── request.py               # ShippingRequest, ShippingResponse, and Estimates
│   ├── services/
│   │   ├── __init__.py              # Service exports
│   │   ├── data_loader.py           # CSV parser, cache, and name normalizer
│   │   ├── cargo_service.py         # Cargo compatibility and steel handling
│   │   ├── feasibility.py           # 4-stage feasibility validation engine
│   │   ├── scoring.py               # Weighted multi-criteria scoring
│   │   ├── recommendation.py        # Candidate ranking and decision justification
│   │   └── route_service.py         # Distance (NM) and voyage duration estimator
│   └── utils/
│       ├── __init__.py
│       └── constants.py             # Enums: FeasibilityStatus, DataQualityStatus, etc.
│
├── data/
│   ├── vessels.csv                  # Handysize, Handymax, Supramax, Panamax, Capesize
│   ├── ports.csv                    # Indian East Coast & global bulk port constraints
│   └── cargo_types.csv              # Dry bulk, grain, bauxite, differentiated steel
│
├── examples/
│   └── sample_requests.json         # Realistic test scenarios (SAIL, Coal, Steel, etc.)
│
├── templates/
│   └── index.html                   # Interactive modern web dashboard UI
│
├── tests/
│   ├── __init__.py
│   ├── conftest.py                  # Pytest configuration & sys.path setup
│   ├── test_cargo.py                # Cargo compatibility & steel tests
│   ├── test_feasibility.py          # Capacity, draft, length, beam limit tests
│   ├── test_recommendation.py       # Recommendation selection & scoring tests
│   ├── test_route.py                # Distance, voyage duration & deadline tests
│   └── test_integration.py          # Case-insensitivity & JSON validation tests
│
├── config.py                        # Centralized paths, scoring weights & constants
├── pytest.ini                       # Pytest execution configuration
├── requirements.txt                 # Project dependencies
├── .gitignore                       # Git ignore rules
└── README.md                        # Documentation
```

---

## 📊 Maritime Datasets & Realism Rules

### 1. Data Quality Statuses
Every entry across ports, vessels, and cargoes maintains a verification status:
- `verified`: Formally verified against official Port Authority handbooks, BIMCO, or Baltic Exchange standards.
- `estimated`: Derived from satellite AIS or secondary industry sources.
- `demo`: Synthetic test data for edge-case simulation.
- `missing`: Physical parameters are not yet recorded or verified.

### 2. Feasibility States
Rather than a naive boolean, the engine assigns granular statuses:
- `feasible`: All constraints pass with verified, reliable operational data.
- `conditionally_feasible`: No physical violation detected, but one or more constraints rely on estimated or unverified data.
- `not_feasible`: At least one physical or commercial limit (payload, draft, LOA, beam, gear) is violated.
- `insufficient_data`: Port or vessel records are completely missing or unidentifiable.

---

## ⚙️ Installation & Setup

### Prerequisites
- Python 3.11+
- Git

### 1. Clone & Setup Virtual Environment
```bash
# Clone the repository
git clone https://github.com/aditiverma12134/test.git
cd test

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

---

## 🚀 How to Run

### 1. Interactive Demo Web Dashboard
Launch the FastAPI-powered interactive web application:
```bash
python -m app.demo_server
```
- Open browser at: **`http://127.0.0.1:8000`**
- Interactive Swagger API docs: **`http://127.0.0.1:8000/docs`**

### 2. Command Line Interface (CLI)
Run single-query evaluations from the terminal:
```bash
python -m app.main --cargo iron_ore --quantity 75000 --origin Paradip --destination Rotterdam --deadline 30
```

Run scenarios directly from a JSON file:
```bash
python -m app.main --file examples/sample_requests.json
```

### 3. Python API Integration
```python
from app.main import analyze_shipping_request

result = analyze_shipping_request(
    cargo_type="iron_ore",
    cargo_quantity_tonnes=75000,
    origin_port="Paradip",
    destination_port="Rotterdam",
    shipping_deadline_days=30
)

print(f"Recommended Vessel: {result['recommendation']['recommended_vessel']}")
print(f"Confidence: {result['recommendation']['recommendation_confidence']}")
print(f"Estimated Transit: {result['route_estimate']['estimated_duration_days']} days")
```

---

## 🧪 Running Tests

Execute the comprehensive test suite with Pytest:
```bash
pytest -v
```

All 22 unit and integration tests cover:
- Capacity fit, over-capacity rejections, and low utilization alerts
- Draft, LOA, and beam constraint rejections (e.g. Haldia shallow draft limits)
- Differentiated steel break-bulk requirements (geared cranes on Handysize vs gearless Panamax)
- Multi-criteria score breakdown and candidate ranking
- Geodesic distance (NM) and voyage transit day calculations
- Case-insensitivity and Pydantic request validation

---

## 📥 Input & Output Specification

### Input Format
```json
{
  "cargo_type": "iron_ore",
  "cargo_quantity_tonnes": 75000,
  "origin_port": "Paradip",
  "destination_port": "Rotterdam",
  "shipping_deadline_days": 30
}
```

### Output Format
```json
{
  "request": {
    "cargo_type": "iron_ore",
    "cargo_quantity_tonnes": 75000.0,
    "origin_port": "Paradip",
    "destination_port": "Rotterdam",
    "shipping_deadline_days": 30.0
  },
  "vessel_analysis": [
    {
      "vessel_class": "Handysize",
      "feasibility_status": "not_feasible",
      "checks": {
        "capacity": false,
        "cargo": true,
        "origin_draft": true,
        "origin_length": true,
        "origin_beam": true,
        "destination_draft": true,
        "destination_length": true,
        "destination_beam": true
      },
      "capacity_utilization": 1.875,
      "score": null,
      "score_breakdown": null,
      "warnings": [],
      "rejection_reasons": [
        "Insufficient cargo capacity: parcel of 75,000t exceeds maximum deadweight of 39,999t."
      ],
      "data_status": "verified"
    },
    {
      "vessel_class": "Panamax",
      "feasibility_status": "feasible",
      "checks": {
        "capacity": true,
        "cargo": true,
        "origin_draft": true,
        "origin_length": true,
        "origin_beam": true,
        "destination_draft": true,
        "destination_length": true,
        "destination_beam": true
      },
      "capacity_utilization": 0.8824,
      "score": 96.5,
      "score_breakdown": {
        "capacity_utilization": 36.86,
        "port_confidence": 30.0,
        "cargo_compatibility": 20.0,
        "operational_efficiency": 9.6
      },
      "warnings": [],
      "rejection_reasons": [],
      "data_status": "verified"
    }
  ],
  "recommendation": {
    "recommended_vessel": "Panamax",
    "status": "recommended",
    "recommendation_confidence": "high",
    "reasoning": [
      "Optimal parcel capacity: 75,000t fits within Panamax range (65,000t - 84,999t).",
      "High payload utilization (88.2%), maximizing commercial freight efficiency.",
      "Full cargo compatibility for 'iron_ore' with vessel hold/gear configuration.",
      "Complies with origin port (Paradip) draft and berth limits (draft 14.5m <= max 17.1m).",
      "Complies with destination port (Rotterdam) navigational limits (draft 14.5m <= max 24.0m).",
      "Highest composite suitability score (96.5/100) among evaluated candidate classes."
    ],
    "message": null
  },
  "route_estimate": {
    "origin_port": "Paradip",
    "destination_port": "Rotterdam",
    "distance_estimate": {
      "value": 4174.7,
      "unit": "nautical_miles",
      "method": "geographic_estimate"
    },
    "estimated_duration_days": 12.4,
    "deadline_met": true,
    "warning": "Geographic distance is an idealized great-circle estimate. Actual maritime route and duration may differ significantly due to navigational straits, TSS routing, canal transit, and weather conditions."
  },
  "data_quality": {
    "overall_status": "partially_verified",
    "origin_port_status": "verified",
    "destination_port_status": "verified",
    "vessel_data_status": "estimated",
    "unverified_elements": [
      "Vessel class 'Mini-Bulker' status is estimated"
    ]
  }
}
```

---

## ⚖️ Limitations & Operational Notice

> **IMPORTANT DISCLAIMER**  
> *"This MVP recommends vessel classes based on available vessel specifications and port constraints. It does not identify real-time available ships and does not replace professional maritime operational planning."*

- **Geographic Distance**: Distances are computed via geodesic great-circle lines. Commercial sea-lane waypoints (e.g. Suez Canal, Malacca Strait, Cape of Good Hope) and weather routing must be integrated in future phases for precise bunkering estimates.
- **Tidal Drafts**: Port drafts reflect published standard datum. Dynamic tidal windows and dredging status must be verified with harbor masters prior to formal charter fixture.

---

## 🔮 Future Improvements

1. **SeaRoute Polylines**: Integration with maritime sea-lane graph routing (e.g., Searoute) to route around landmasses and calculate exact canal tolls.
2. **AIS Live Congestion Feeds**: Dynamic waiting-time estimation at anchorage for East Coast ports (Paradip, Gangavaram, Vizag).
3. **Integration with Price Forecaster (Member 1)**: Coupling recommended vessel class directly with Baltic sub-index forecasts (BPI, BCI, BSI).
4. **Integration with Decision Engine (Member 2)**: Feeding voyage duration, capacity utilization, and physical feasibility into the final BOOK / WAIT / NEGOTIATE optimizer.

