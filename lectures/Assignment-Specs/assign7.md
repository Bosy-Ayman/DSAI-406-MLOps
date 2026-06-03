# Assignment 7

## Implementation 

You are the Lead MLOps Engineer at **Safe-Health**, a startup developing AI for patient risk prediction. You are tasked with re-engineering the company's delivery system into a **High-Integrity Promotion Pipeline**. The system must act as a quality filter, ensuring that computational resources are only spent on verified data and that only audited models reach the clinical production environment.

Your `workflow.yaml` must implement a **Directed Acyclic Graph (DAG)** with three distinct, dependent jobs:

1. **The Integrity Audit (Data & Code)**
   - Pull the dataset using **DVC** from a remote (mocked via a local directory).
   - Execute a script `check_data.py` to verify data schema and quality.
   - If the data fails validation or the `.dvc` files are out of sync, the pipeline must terminate immediately.

2. **The Forensic Build (Docker)**
   - Must run only after the **Integrity Audit** is successfully completed.
   - Only runs if the branch is `main` AND a specific commit keyword `[build-image]` is used.
   - Build a Docker image containing the environment and model.
   - If the build fails, use a failure condition to upload the build logs as a GitHub Actions Artifact for investigation.

3. **The Production Promotion (The Final Gate)**
   - Must run only after the **Forensic Build** is successfully completed.
   - This job is strictly restricted: it only runs when a Git Tag (e.g., `v1.0.2`) is pushed.
   - Simulate the promotion of the image to a Production Registry (e.g., `echo "Promoting v1.0.2 to Clinic..."`).

---

**Tasks:** While this assignment is for practice (not graded), a professional submission would include: 

1. `pipeline.yaml`: The complete workflow file.
2. `Dockerfile`: A multi-stage Dockerfile.
3. The "Evidence":
    - A screenshot of a successful promotion showing the full 3-job graph.
    - A screenshot of a skipped promotion (e.g., a push to a feature branch that correctly stopped after Job 1).
    - A screenshot of the Artifacts section showing a `build-crash-logs` file generated during an intentional failure.

