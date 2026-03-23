"""
check_threshold.py
------------------
Reads the Run ID from model_info.txt, loads accuracy from the LOCAL
mlruns/ folder (no MLflow server needed), and fails if below 0.85.
"""

import sys
import mlflow

THRESHOLD = 0.85

# Must match the URI used in train.py
mlflow.set_tracking_uri("mlruns")
client = mlflow.tracking.MlflowClient()

# ── Read Run ID ───────────────────────────────────────────────────────────────
try:
    with open("model_info.txt") as f:
        run_id = f.read().strip()
except FileNotFoundError:
    print("ERROR: model_info.txt not found.", file=sys.stderr)
    sys.exit(1)

if not run_id:
    print("ERROR: model_info.txt is empty.", file=sys.stderr)
    sys.exit(1)

print(f"Run ID   : {run_id}")

# ── Fetch accuracy from local mlruns/ ────────────────────────────────────────
try:
    run = client.get_run(run_id)
except Exception as e:
    print(f"ERROR: Could not load run — {e}", file=sys.stderr)
    sys.exit(1)

accuracy = run.data.metrics.get("accuracy")
if accuracy is None:
    print("ERROR: 'accuracy' metric not found in run.", file=sys.stderr)
    sys.exit(1)

print(f"Accuracy : {accuracy:.4f}")
print(f"Threshold: {THRESHOLD}")

# ── Gate ─────────────────────────────────────────────────────────────────────
if accuracy < THRESHOLD:
    print(
        f"\n❌ FAILED — accuracy {accuracy:.4f} is below {THRESHOLD}. "
        "Deployment aborted.",
        file=sys.stderr,
    )
    sys.exit(1)

print(f"\n✅ PASSED — accuracy {accuracy:.4f} meets the threshold. Deploying.")