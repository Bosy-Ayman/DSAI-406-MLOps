# Assignment 3

## Reading 

- Read [MLFlow Tutorial about Tracking API](https://mlflow.org/docs/latest/ml/tracking/) and [DL MLflow Tutorial](https://mlflow.org/docs/latest/ml/getting-started/deep-learning/)


## Implementation 

**Objective**: In this assignment, you will transition from "silent" training to **Observable ML**. You will instrument a PyTorch training script with **MLflow** to track, compare, and version your machine learning experiments. By the end, you will be able to prove which model configuration is superior.

- Phase 1: Ensure your environment is reproducible. You may use your Conda environment from previous labs or a Docker container.
    - **Install Dependencies:**
        ```bash
        pip install mlflow torch torchvision
        ```

    - **Launch the MLflow UI:**
    In a separate terminal window, start the tracking server:

        ```bash
        mlflow ui --port 5000
        ```
    Verify: Open http://localhost:5000 in your browser. You should see the MLflow dashboard.

- Phase 2: Modify your PyTorch training script to include the following **MLflow pillars**:
  - Set a unique experiment name: `mlflow.set_experiment("Assignment3_YourName")`.
  - Wrap your training logic in `with mlflow.start_run():` to ensure all logs are grouped together.
  - **Parameters:** Log at least three hyperparameters (e.g., `learning_rate`, `epochs`, `batch_size`).
  - **Tags:** Add a tag to identify your work: `mlflow.set_tag("student_id", "YOUR_ID")`.
  - **Live Logging:** Inside your training loop (at the end of every epoch), log the `loss` and `accuracy`.
  - **Goal:** This generates the "Learning Curve" graphs needed to analyze model convergence.
  - Use the **MLflow Model Flavor** to save your final model weights and environment details:

- Phase 3: Execute your training script at least **5 times**. In each run, vary one or more hyperparameters (e.g., try different learning rates: `0.1`, `0.01`, `0.001`, or adjust the `batch_size`). Analyze the MLflow UI to investigate:
    - **Convergence:** Which configuration reaches your target accuracy the fastest?
    - **Stability:** Does a high learning rate lead to unstable or "exploding" loss curves?
    - **Reproducibility:** Can you see the exact parameters that produced your best result?

-  Submission Requirements: Submit your notebook along with a short report (PDF) including the following **screenshots** from your MLflow UI:
   1.  **The Table View:** A list showing all 5 runs, sorted by your primary performance metric (e.g., Accuracy).
   2.  **The Comparison View:** A single chart showing the `Loss` or `Accuracy` curves of at least 3 different runs overlaid on each other.
   3.  **The Artifact Gallery:** A view of the "Artifacts" tab showing the saved model, the `MLmodel` metadata file, and the auto-generated environment files.
   4.  **Short Analysis:** Which run was the "Winner" and why? Did you notice any evidence of overfitting or underfitting in the curves?

