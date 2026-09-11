"""
Synthetic market data generator for Maritime Freight Decision Support System.
All data is clearly labeled SYNTHETIC.
Run from project root: python generate_market_data.py
"""

import csv, random, math
from datetime import date, timedelta
from pathlib import Path

SEED = 42
random.seed(SEED)

OUT_DIR = Path(__file__).resolve().parent / "data" / "market"
OUT_DIR.mkdir(parents=True, exist_ok=True)

END_DATE   = date(2025, 9, 10)
START_DATE = END_DATE - timedelta(days=729)
N = 730

def daterange(start, end):
    d = start
    while d <= end:
        yield d
        d += timedelta(days=1)

def correlated_walk(start, sigma, alpha=0.02, low=None, high=None, n=730):
    values = [start]
    for _ in range(n - 1):
        prev  = values[-1]
        shock = random.gauss(0, sigma)
        drift = -alpha * (prev - start)
        new   = prev + drift + shock
        if low  is not None: new = max(low,  new)
        if high is not None: new = min(high, new)
        values.append(round(new, 2))
    return values

all_dates = list(daterange(START_DATE, END_DATE))

# --- BDI -------
bdi = correlated_walk(1500, 80, 0.03, 400, 4500)
bdi_rows = []
for i, d in enumerate(all_dates):
    bdi_rows.append({
        "date": d.isoformat(), "bdi": int(bdi[i]),
        "bci": int(bdi[i]*random.uniform(1.15,1.35)),
        "bsi": int(bdi[i]*random.uniform(0.65,0.85)),
        "bhsi": int(bdi[i]*random.uniform(0.45,0.65)),
        "data_source": "SYNTHETIC"
    })
with open(OUT_DIR/"bdi_history.csv","w",newline="") as f:
    w=csv.DictWriter(f,fieldnames=bdi_rows[0].keys()); w.writeheader(); w.writerows(bdi_rows)
print(f"bdi_history.csv  ({len(bdi_rows)} rows)")

# --- Oil -------
oil = correlated_walk(80.0, 2.5, 0.04, 55.0, 105.0)
oil_rows = []
for i, d in enumerate(all_dates):
    oil_rows.append({
        "date": d.isoformat(), "wti_usd_bbl": oil[i],
        "brent_usd_bbl": round(oil[i]+random.uniform(0.5,3.5),2),
        "data_source": "SYNTHETIC"
    })
with open(OUT_DIR/"oil_prices.csv","w",newline="") as f:
    w=csv.DictWriter(f,fieldnames=oil_rows[0].keys()); w.writeheader(); w.writerows(oil_rows)
print(f"oil_prices.csv   ({len(oil_rows)} rows)")

# --- Commodities -------
iron_ore  = correlated_walk(105.0,4.0,0.03,70.0,150.0)
coal      = correlated_walk(140.0,6.0,0.025,85.0,220.0)
grain     = correlated_walk(220.0,7.0,0.025,160.0,320.0)
bauxite   = correlated_walk(55.0,2.0,0.03,35.0,85.0)
fertilizer= correlated_walk(380.0,12.0,0.02,250.0,550.0)
comm_rows = []
for i, d in enumerate(all_dates):
    comm_rows.append({
        "date": d.isoformat(),
        "iron_ore_usd_t": iron_ore[i], "coal_usd_t": coal[i],
        "grain_usd_t": grain[i], "bauxite_usd_t": bauxite[i],
        "fertilizer_usd_t": fertilizer[i], "data_source": "SYNTHETIC"
    })
with open(OUT_DIR/"commodity_prices.csv","w",newline="") as f:
    w=csv.DictWriter(f,fieldnames=comm_rows[0].keys()); w.writeheader(); w.writerows(comm_rows)
print(f"commodity_prices.csv ({len(comm_rows)} rows)")

# --- Freight History -------
ROUTES = [
    ("Paradip","Rotterdam","iron_ore","Panamax",12.0,4800),
    ("Port Hedland","Qingdao","iron_ore","Capesize",7.5,4000),
    ("Port Hedland","Gangavaram","coal","Capesize",8.0,3800),
    ("Samarinda","Gangavaram","coal","Panamax",11.0,2200),
    ("Samarinda","Shanghai","coal","Supramax",14.0,2600),
    ("Paradip","Rotterdam","grain","Supramax",16.0,4800),
    ("Paradip","Singapore","steel_coils","Handysize",28.0,1900),
    ("Dhamra","Singapore","steel_coils","Handymax",24.0,2100),
    ("Richards Bay","Rotterdam","coal","Panamax",13.5,5200),
    ("Newcastle","Qingdao","coal","Panamax",12.5,4200),
    ("Baltimore","Rotterdam","grain","Handymax",22.0,3400),
    ("Norfolk","Rotterdam","grain","Panamax",18.5,3300),
    ("Paradip","Rotterdam","iron_ore","Handymax",18.0,4800),
    ("Visakhapatnam","Rotterdam","iron_ore","Panamax",12.5,4700),
    ("Port Hedland","Rotterdam","iron_ore","Capesize",6.5,8200),
]
bdi_d   = {d.isoformat(): bdi[i]      for i,d in enumerate(all_dates)}
oil_d   = {d.isoformat(): oil[i]      for i,d in enumerate(all_dates)}
ior_d   = {d.isoformat(): iron_ore[i] for i,d in enumerate(all_dates)}
coal_d  = {d.isoformat(): coal[i]     for i,d in enumerate(all_dates)}
grain_d = {d.isoformat(): grain[i]    for i,d in enumerate(all_dates)}

def comm_price(cargo, ds):
    if cargo in ("iron_ore","bauxite"): return ior_d[ds]
    if cargo == "coal":                 return coal_d[ds]
    return grain_d[ds]

freight_rows = []
weekly = [d for i,d in enumerate(all_dates) if i%7==0]
for d_obj in weekly:
    ds = d_obj.isoformat()
    bv, ov = bdi_d[ds], oil_d[ds]
    for (orig,dest,cargo,vessel,base,dist) in ROUTES:
        bdi_f = (bv/1500.0)**0.55
        oil_f = 1.0 - 0.0015*max(0.0, ov-75.0)
        rate  = round(base * bdi_f * oil_f * random.uniform(0.92,1.08), 2)
        rate  = max(3.0, rate)
        freight_rows.append({
            "date": ds, "origin": orig, "destination": dest,
            "cargo_type": cargo, "vessel_type": vessel,
            "freight_rate_usd_mt": rate, "bdi": int(bv),
            "oil_price": round(ov,2), "commodity_price": round(comm_price(cargo,ds),2),
            "distance_nm": dist, "data_source": "SYNTHETIC"
        })
with open(OUT_DIR/"freight_history.csv","w",newline="") as f:
    w=csv.DictWriter(f,fieldnames=freight_rows[0].keys()); w.writeheader(); w.writerows(freight_rows)
print(f"freight_history.csv  ({len(freight_rows)} rows, {len(ROUTES)} routes x {len(weekly)} weeks)")
print("Done. All data labeled SYNTHETIC.")
