---
theme: neversink
class: 'text-center'
transition: slide-left
title: MLOps (DSAI 406)
author: Mohamed Ghalwash
year: Spring 2025-2026
venue: Zewail City
mdc: true
lecture: 4
slide:
  disableSlideNumbers: true
slide_info: false
---

# ML Engineering for Production <br> (DSAI 406)
## Lecture 4

Mohamed Ghalwash
<Email v="mghalwash@zewailcity.edu.eg" />

---
layout: fact
---

# Recording is NOT allowed 

---
layout: top-title
---

:: title :: 

# Automated Testing for ML

:: content :: 

In MLOps, we move beyond simple syntax checks. We need **three levels** of testing to ensure both the code and the model are healthy:

<div class="grid grid-cols-1 gap-4">

| Test Type | What it checks | Example |
| :--- | :--- | :--- |
| **Unit Tests** | Individual code components | `test_preprocess_nulls()`: Does the scaler handle NaNs? |
| **Integration Tests** | Data + Model pipeline | `test_input_shape()`: Does the model accept the current data? |
| **Validation Tests** | Model "Behavioral" Performance | `assert accuracy > 0.80`: Is the model good enough to deploy? |

</div>

---
layout: top-title
---

:: title :: 

# Automated Testing for ML

:: content :: 


```python
# tests/test_model_logic.py
import pytest
from src.model import load_model

def test_prediction_range():
    model = load_model("models/latest.pkl") # hmmmm?
    prediction = model.predict(test_sample)
    # Ensure probabilities are always between 0 and 1
    assert prediction >= 0 and prediction <= 1 

def test_overfitting_check():
    # A simple test to ensure loss isn't exactly zero
    assert metrics['train_loss'] > 1e-5
```

---
layout: section
---

# Use Cases 

---
layout: top-title
---

:: title :: 

# Step 1: Simple Trigger

:: content :: 

**The Goal**: Automatically train the model when code changes

<v-click>

```yaml
# .github/workflows/v1.yml
name: Simple CI
on: [push]

jobs:
  train-model:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: pip install -r requirements.txt
      - run: python train.py
```

</v-click>

<v-click>

**The Issue**: This is "blind" training. It runs the code, but we don't know if the model is actually better than the previous one, and we aren't saving the results anywhere
</v-click>

---
layout: top-title
---

:: title :: 

# Step 2: Adding Observability (The MLflow Connection)

:: content :: 

<v-click>

```yaml
# .github/workflows/v2.yml
# ... (same trigger)
    steps:
      - uses: actions/checkout@v4
      - run: pip install -r requirements.txt mlflow
      - name: Train and Log
        env:
          MLFLOW_TRACKING_URI: ${{ secrets.MLFLOW_TRACKING_URI }}
        run: python train.py --epochs 1 # Validation Test
```
</v-click>

<v-click>

**The Issue**: Great, we are logging! But we are just "blindly" pushing code. What if the model in this push is worse than the one currently in production? We need to fetch the best model to compare or deploy
</v-click>


---
layout: top-title
---

:: title :: 

# Step 3: Fetching the "Best" Model

:: content :: 

<v-click>

```yaml
# .github/workflows/v3.yml
# ...
    steps:
      - uses: actions/checkout@v4
      # ... (install steps)
      - name: Fetch Best Model
        env:
          MLFLOW_TRACKING_URI: ${{ secrets.MLFLOW_TRACKING_URI }}
        run: |
          # This script finds the best model and saves its URI to a file
          python -c "
          import mlflow
          client = mlflow.tracking.MlflowClient()
          exp = client.get_experiment_by_name('Assignment3_Mohamed')
          runs = client.search_runs(exp.experiment_id, order_by=['metrics.accuracy DESC'], max_results=1)
          with open('best_model_uri.txt', 'w') as f:
              f.write(runs[0].info.artifact_uri + '/model')
```

</v-click>

<v-click>

**The Issue**: This YAML validates the model but does not build the docker image 
</v-click>

---
layout: top-title
---

:: title :: 

# Step 4: Building Docker 

:: content :: 

<v-click>

```yaml
# .github/workflows/v3.yml
# ...
    steps:
      - uses: actions/checkout@v4
      # ... (install steps)
      - name: Fetch Best Model
        run: python get_best_model.py
      - name: Docker Login
        uses: docker/login-action@v3
        with:
          username: ${{ secrets.DOCKER_USERNAME }}
          password: ${{ secrets.DOCKER_PASSWORD }}

      - name: Build and Push Docker Image
        run: |
          MODEL_URI=$(cat best_model_uri.txt)
          docker build --build-arg MODEL_PATH=$MODEL_URI -t ${{ secrets.DOCKER_USERNAME }}/ml-app:latest .
          docker push ${{ secrets.DOCKER_USERNAME }}/ml-app:latest
```

</v-click>

<v-click>

**The Issue**: This YAML is getting huge. If the "Train" step fails, the "Docker" step still tries to run because they are in the same list of steps. We need to separate Validation from Deployment. 
</v-click>

---
layout: top-title
---

:: title :: 

# Step 5: Separation of Concerns (Multi-Job)

:: content :: 

<v-click>

```yaml
# .github/workflows/v4.yml
jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - run: python train.py --smoke-test
  
  deploy:
    runs-on: ubuntu-latest
    steps:
      - run: docker build ...
```
</v-click>

<v-click>

**The Issue**: Parallelism! GitHub runs jobs in parallel by default. The deploy job will start before the validate job finishes. We might deploy a broken model!
</v-click>

---
layout: top-title
---

:: title :: 

# Step 6: The Final Pipeline (Dependencies)

:: content :: 

```yaml
# .github/workflows/final.yml
name: Production MLOps Pipeline
on:
  push:
    branches: [main]

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - name: Smoke Test & Pytest
        run: pytest tests/ && python train.py --epochs 1

  deploy:
    needs: validate # <--- THE FIX: Wait for validation to pass 🟢
    runs-on: ubuntu-latest
    steps:
      - name: Fetch Best Model
        run: python get_best_model.py
      - name: Build and Push Docker
        run: |
          docker build --build-arg MODEL_URI=$(cat uri.txt) -t app:latest .
          docker push app:latest
```

---
layout: top-title
---

:: title :: 

# Docker 

:: content ::

```dockerfile
  # 1. Start with a lightweight Python base
  FROM python:3.10-slim

  # 2. Define the Build Argument
  # This will be passed from your GitHub Action
  ARG MODEL_PATH

  # 3. Set environment variables
  ENV PYTHONUNBUFFERED=1
  ENV MODEL_DIR=/opt/ml/model

  # 4. Install system dependencies & MLflow
  RUN apt-get update && apt-get install -y --no-install-recommends \
      build-essential \
      && rm -rf /var/lib/apt/lists/*

  COPY requirements.txt .
  RUN pip install --no-cache-dir -r requirements.txt
  RUN pip install mlflow

  # 5. Fetch the Model from MLflow during Build
  # This ensures the "brain" is baked into the image
  RUN mkdir -p ${MODEL_DIR}
  RUN mlflow artifacts download --artifact-uri ${MODEL_PATH} --dst-path ${MODEL_DIR}

  # 6. Copy your inference/API code
  COPY src/ /app/
  WORKDIR /app

  # 7. Expose the port for your API (e.g., FastAPI or Flask)
  EXPOSE 8000

  # 8. Start the service
  CMD ["python", "serve.py"]
```


---
layout: top-title
---

:: title :: 

# From Experiment to Production

:: content :: 

Once the PR is approved, the **CD Pipeline** takes over. But where are the pieces?

<div class="grid grid-cols-3 gap-6 pt-4">

<div class="p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
  <h4 class="font-bold mb-2">1. The Blueprint</h4>
  <p class="text-xs">The <b>Dockerfile</b> is in your Git repo. It defines the OS, Python version, and system dependencies.</p>
</div>

<div class="p-4 bg-purple-50 dark:bg-purple-900/20 rounded-lg">
  <h4 class="font-bold mb-2">2. The Brain</h4>
  <p class="text-xs">The <b>Model Weights</b> are pulled from <b>MLflow</b>. We use a script to find the <code>Best Model</code> or <code>Production</code> tag.</p>
</div>

<div class="p-4 bg-green-50 dark:bg-green-900/20 rounded-lg">
  <h4 class="font-bold mb-2">3. The Container</h4>
  <p class="text-xs">Docker builds the image, downloads the model inside it, and starts the API service.</p>
</div>

</div>

<div class="mt-8">

```python {all|3-5}
# The MLflow Fetch Script: "Getting the Brain"
import mlflow
# Filter to get the best performing model from the registry
best_run = mlflow.search_runs(experiment_ids=["1"], order_by=["metrics.accuracy DESC"])[0]
model_uri = f"runs:/{best_run.info.run_id}/model"
# Load into the Dockerized API
model = mlflow.pyfunc.load_model(model_uri)
```

</div>


---
layout: top-title
---

:: title :: 

# Connecting the Dots: Docker + MLflow + CI

:: content :: 

Every tool we have learned so far—**Docker**, **DVC**, and **MLflow**—now converges into a single automated pipeline. This is where MLOps becomes a "system" rather than just a collection of scripts.

* 🐳 **Docker:** The CI Runner uses your **Dockerfile** to ensure the test environment perfectly matches your development environment. No "it worked on my machine."
* 🗂️ **DVC:** The CI pipeline pulls the specific version of the data from remote storage to run validation tests.
* 📈 **MLflow:** The CI process logs the results of the "Test Run" to your tracking server. You can compare CI performance against your local manual experiments.

<div class="mt-6 p-4 bg-blue-500 bg-opacity-10 border-l-4 border-blue-500">
  <strong>The Pipeline Workflow:</strong> 
  <br><code>Git Push</code> ➔ <code>Build Container</code> ➔ <code>Pull Data (DVC)</code> ➔ <code>Run Tests (Pytest)</code> ➔ <code>Log to MLflow</code> ➔ <code>Deployment Approval</code>
</div>


---
layout: top-title
---

:: title :: 

# TensorBoard: The Micro-Manager
### Zooming into the Training Loop

:: content :: 

While MLflow looks at the End Result, TensorBoard looks at the Process.

- **Real-time**: Watch the loss curve live. If it goes to NaN, kill the job.

- **Histograms**: View weight distributions to see if your gradients are "vanishing."

- **Embedding Projector**: Visualize high-dimensional data (like Word2Vec) in 3D.

```python 
from torch.utils.tensorboard import SummaryWriter

writer = SummaryWriter('logs/run_1')

for epoch in range(100):
    loss = train_step()
    # Log scalars to plot a curve
    writer.add_scalar('Loss/train', loss, epoch)
    
    # Log images to see what the model "sees"
    writer.add_image('prediction_sample', img_grid, epoch)

writer.close()
```

---
layout: top-title
---

:: title :: 

# Docker Compose: The Conductor
### Running your whole "Lab" at once

:: content :: 

Your ML project now has multiple moving parts:

- The Trainer (Your PyTorch code).
- The MLflow Server (To view results).
- The TensorBoard UI.

Instead of 3 terminal windows, we use Docker Compose to orchestrate them in one command.

---
layout: top-title
---

:: title :: 

# Data: Why Git is Fundamentally Broken for Data

:: content :: 

Git was built for **source code**, not **big data**

- **Binary Blobs:** Git is designed for text line-diffs. A `.parquet` or `.h5` file is a "black box" to Git.
- **Repo Bloat:** Every time you change a 100MB dataset, Git stores a *full new copy* in the `.git` folder.
- **The Link Problem:** How do you prove which specific version of the data created `model_v1.pt`?

<div class="grid grid-cols-2 gap-10 mt-10">
  <div class="border-l-4 border-primary p-4 bg-gray-500 bg-opacity-10">
    <h4 class="text-primary">DevOps</h4>
    <p>Code Version A ➔ Binary A</p>
  </div>
  <div class="border-l-4 border-green-500 p-4 bg-gray-500 bg-opacity-10">
    <h4 class="text-green-500">MLOps</h4>
    <p>Code A + Data B ➔ Model C</p>
  </div>
</div>

---
layout: section
---

# Data Version Control (DVC)
### Git for Data

---
layout: top-title
---

:: title :: 

# How DVC Works

:: content :: 

- DVC keeps the **Heavy Data** in external storage and keeps a **Lightweight Pointer** in Git

<br>

<div class="grid grid-cols-2 gap-4">

<div>

#### The Command

```bash
# Track the file
dvc add data/raw.csv

# Link to Git
git add data/raw.csv.dvc
git commit -m "Add raw data"
```

</div>
<div>

#### The Pointer (.dvc)
```yaml
# Actual content of raw.csv.dvc
outs:
- md5: a1b2c3d4e5f6g7h8...
  size: 1073741824
  path: raw.csv
```

</div>
</div>

<v-click>

<br>


> When a teammate runs git pull, they get the Pointer. When they run `dvc pull`, DVC fetches the exact 1GB file matching that MD5 hash.

</v-click>

---
layout: top-title
---

:: title :: 

# Git: The Source of Truth
### If it isn't in Git, it didn't happen.

:: content :: 

In MLOps, Git tracks the **Logic** (Code, Dockerfiles, Configs), but **never** the heavy lifting.

* ✅ **Track these:** `.py` scripts, `Dockerfile`, `requirements.txt`, `.github/workflows/`.
* ❌ **Ignore these:** `.pkl` models, `.csv` data, `venv/` folders, `.log` files.

<div class="grid grid-cols-2 gap-4 mt-6">
  <div class="bg-gray-800 p-4 rounded shadow">
    <h4 class="text-green-400 font-mono">.gitignore</h4>
    <pre class="text-xs">
data/
models/
__pycache__/
.env
.DS_Store</pre>
  </div>
  <div class="flex flex-col justify-center">
    <p class="text-sm">
      <b>The Rule:</b> If a file is >50MB or changes every time you run a script (like a log), it belongs in <b>DVC</b> or an <b>Artifact Store</b>, not Git.
    </p>
  </div>
</div>

---

# Git Flow for ML Teams
### Collaboration without the "Merge Chaos"

Undergraduates often work on `main`. In MLOps, we use **Feature Branches** to experiment.

1. **`main`**: The "Production" code. It must always be runnable.
2. **`feature/add-random-forest`**: Where you experiment with new models.
3. **The Pull Request (PR)**: Where MLOps magic happens. 
   - *In 2 weeks, we will make GitHub automatically run tests on every PR.*

<v-click>

### 💡 The "Model-Code" Link
Every commit hash in Git (e.g., `a7b2c3d`) should represent a specific state of your project. If you deploy a model, you must be able to say: 
> "This model was built from **Git Commit a7b2c3d** using **DVC Data Version v2**."

</v-click>
