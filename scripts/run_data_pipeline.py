import subprocess
import sys
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent
SCRIPTS_DIR = BASE_DIR / "scripts"


PIPELINE_STEPS = [
    "clean_freight_data.py",
    "process_eia_diesel.py",
    "merge_eia_with_freight.py",
    "build_fuel_features.py",
    "build_fuel_ml_datasets.py",
    "train_fuel_change_model.py",
    "generate_forecast.py",
    "build_trend_intelligence.py",
    "build_freight_intelligence.py",
]


def run_step(script_name):
    script_path = SCRIPTS_DIR / script_name

    print()
    print("=" * 70)
    print(f"RUNNING: {script_name}")
    print("=" * 70)

    result = subprocess.run(
        [sys.executable, str(script_path)],
        cwd=BASE_DIR
    )

    if result.returncode != 0:
        print()
        print(f"FAILED: {script_name}")
        print("Pipeline stopped.")
        sys.exit(result.returncode)

    print()
    print(f"COMPLETED: {script_name}")


print("=" * 70)
print("FREIGHT INTELLIGENCE DATA PIPELINE")
print("=" * 70)

for step in PIPELINE_STEPS:
    run_step(step)

print()
print("=" * 70)
print("DATA PIPELINE COMPLETE")
print("=" * 70)