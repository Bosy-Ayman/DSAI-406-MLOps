# Assignment 5

## Implementation 

**Objective**: Create a multi-job pipeline that validates a model and "deploys" it (via Docker) only if it meets specific performance criteria. You have a Python script `train.py` that trains a classifier and logs the accuracy to MLflow. Your goal is to automate the transition from development to production using a two-job GitHub Action.

1. The Validation Job (**validate**). Create a job that:
    - **Pulls Data**: Uses `dvc pull` to get the training dataset.
    - **Trains**: Runs python `train.py`.
    - **Observes**: Logs the run to an MLflow Tracking Server (use a secret for the URI).
    - **Exports**: If the model training is successful, it must create a file called `model_info.txt` containing the Run ID of the current MLflow run.
    - **Persists**: Use `actions/upload-artifact@v4` to save `model_info.txt`.
  
2. The Deployment Job (**deploy**). Create a second job that depends on the validation job. It must:
   - **Download**: Use `actions/download-artifact@v4` to retrieve `model_info.txt`.
   - **Logic**: Run a script `check_threshold.py` that reads the Run ID, checks the accuracy in MLflow, and fails the pipeline if accuracy is below 0.85.
   - **Containerize**: If the check passes, run a "Mock Build":
        `echo "Building Docker image for Run ID: $(cat model_info.txt)"`

3. The Dockerfile. Write a simple `Dockerfile` in your repo that:
   - Uses `python:3.10-slim` as the base.
   - Accepts an ARG RUN_ID.
   - Includes a command to "download" the model (you can use echo to simulate this if you don't have a public MLflow server).

**Tasks**
You need to submit the following: 
- The YAML: Provide the full `.github/workflows/pipeline.yml` file.
- The Evidence: * A screenshot of a Failed run (where accuracy was < 0.85).
- A screenshot of a Successful run (where accuracy was > 0.85) showing the deploy job completed.

- **Grading Rubric:**
  - Pipeline Architecture (30): all jobs are developed correctly
  - Data & Model Handover (30): Correct way to pass the `model_info.txt` from machine 1 to machine 2. 
  - Threshold Logic (20): Successfully halts the pipeline if the MLflow metric is below the target.
  - Security & Docker (20): Dockerfile correctly uses ARG for the model path/ID.
