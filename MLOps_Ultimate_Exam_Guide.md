# 🎯 DSAI-406 MLOps — Ultimate Exam Guide

> **One document. Everything you need. Organized by topic, not by lecture.**
> Includes: ALL lecture content + ALL assignment code + ALL hidden "between the lines" knowledge + 60+ tricky professor-style questions embedded inline.

---

# PART 1: WHY MLOPS EXISTS

## 1.1 The Reproducibility Crisis (Assignment 1)

You tried to run someone else's ML code. What happened?
- **Dependency Hell** — PyTorch version mismatch, missing scikit-learn
- **Random Seeds** — Without `torch.manual_seed()` / `random_state=42`, different accuracy each run
- **Hardcoded Paths** — `/home/mohamed/data` doesn't exist on your machine
- **No `requirements.txt`** — Impossible to recreate the environment
- **Would it survive on a server at 3 AM?** — No! Network timeouts, missing deps

> **This is WHY the entire course exists.** Every tool solves a problem from Assignment 1.

## 1.2 Hidden Technical Debt (NeurIPS 2015, Google)

ML code is only a **tiny fraction** of a real-world ML system. The surrounding infrastructure is massive:
- Data collection & verification
- Feature extraction & process management
- Configuration, monitoring, serving infrastructure

**Goal:** Not new functionality, but enabling future improvements and reducing errors.
**MLOps = Automation + Shipping**

## 1.3 The "Ops" Family

| Ops Type | Focus | Key Tasks |
|----------|-------|-----------|
| **DevOps** | Software velocity | Git versioning, unit/integration tests, deploying binaries |
| **DataOps** | Data quality & agility | DVC versioning, data validation, periodic/streaming data |
| **MLOps** | ML + DevOps + Data | Git + DVC + Model Registry, data + model quality, deploying prediction pipelines, handling data drift |

## 1.4 What is MLOps?

Process of automating ML using DevOps methodologies. Tasks:
1. **Versioning** — Git + DVC + Model Registry
2. **Testing** — Unit + Integration + Data Validation + Model Quality
3. **Deployment** — Prediction pipeline (not just a binary)
4. **Maintenance** — Models decay → Data Drift monitoring

## 1.5 Key Roles

| Role | Focus |
|------|-------|
| **Data Scientist** | Builds models, focuses on accuracy |
| **ML Engineer** | Productionizes models, focuses on reliability |
| **ML Researcher** | Advances state of the art |

## 1.6 MLOps Topics

CI/CD, Cloud Computing, AutoML, Containers, Edge Computing, Model Portability

### ⚠️ TRICKY EXAM QUESTIONS

**Q: What's the difference between DevOps and MLOps?**
A: DevOps automates software (Code → Binary). MLOps automates ML (Code + Data → Model). MLOps has extra: data versioning, model drift, models decay over time.

**Q: Why does Assignment 1 exist?**
A: It's the MOTIVATION for the entire course. Every tool solves a specific Assignment 1 problem.

**Q: Can a model work in dev but fail in production?**
A: Yes! "It works on my machine" ≠ works everywhere. Hidden technical debt.

---

# PART 2: ENVIRONMENT & REPRODUCIBILITY

## 2.1 Python Environment Management

### Conda vs Pip

| Feature | pip + venv | Conda/Mamba |
|---------|-----------|-------------|
| Focus | Python packages only | Python + Non-Python (C++, CUDA, R) |
| ML Use Case | Simple web APIs | **Standard for Data Science** (GPU/CUDA) |

**Rule:** NEVER use your "Base" Python. Always isolate.

### Essential Commands
```bash
conda create --name ENVNAME python=3.7    # Create
conda activate ENVNAME                      # Activate
conda install XXX / pip install XXX         # Install
conda deactivate                            # Deactivate
conda env remove --name ENVNAME --all       # Clean up
```

### Freezing Your Environment

| Method | Command | Output |
|--------|---------|--------|
| **Pip** | `pip freeze > requirements.txt` | `pandas==2.1.0` |
| **Conda** | `conda env export --no-builds > environment.yml` | `dependencies: - python=3.9` |

> In Docker, prefer `requirements.txt` — faster and simpler.

## 2.2 Git — Version Control & Security

### What to Track vs Ignore
- ✅ Track: `.py`, `Dockerfile`, `requirements.txt`, `.github/workflows/`
- ❌ Ignore: `.pkl` models, `.csv` data, `venv/`, `.log`, `__pycache__/`, `.env`
- Rule: If file > 50MB or changes every run → use DVC, NOT Git

### 🔑 THE PASSWORD QUESTION (Professor's Favorite!)

> **Q: If you commit a file containing `password=12345` and push to GitHub, will GitHub block the push?**
> **A: NO!** Git and GitHub will HAPPILY push your password. Git does not check file contents.

GitHub has optional features:
- **Secret Scanning** — alerts AFTER the push (doesn't block)
- **Push Protection** — can block, but opt-in and limited patterns

**This is why we use:**
- `${{ secrets.NAME }}` in GitHub Actions (encrypted, never in logs)
- `.env` files (local only, in `.gitignore`)
- NEVER hardcode credentials

### .gitignore — What It Does and Doesn't Do

| What It Does ✅ | What It Doesn't ❌ |
|-----------------|-------------------|
| Prevents **untracked** files from being added | Does NOT remove **already-tracked** files |
| Works on patterns (`*.pkl`, `data/`) | Does NOT encrypt or protect files |

**Q: I added `secrets.txt` to `.gitignore` AFTER I already committed it. Is it safe?**
A: **No!** Still in Git history. Must run `git rm --cached secrets.txt` AND rewrite history.

### .env Files Pattern
```bash
# .env (NEVER committed to Git!)
MLFLOW_TRACKING_URI=http://mlflow-server:5000
DOCKER_PASSWORD=SuperSecret123
```
In code: `os.getenv("MLFLOW_TRACKING_URI")` reads from environment.

### .gitignore vs .dockerignore
- `.gitignore` tells Git which files to ignore
- `.dockerignore` tells Docker which files NOT to send to build context

## 2.3 Docker — Containerization

### Image vs Container

| Concept | Analogy | Details |
|---------|---------|---------|
| **Image** | Recipe / Blueprint | Read-only template built from Dockerfile |
| **Container** | Running dish / Instance | Live, writable instance of an image |

You can run **many containers** from **one image**. Each is isolated.

### Anatomy of a Dockerfile
```dockerfile
# 1. Base image
FROM python:3.10-slim

# 2. Working directory
WORKDIR /app

# 3. Copy requirements FIRST (layer caching!)
COPY requirements.txt .

# 4. Install dependencies (BUILD time)
RUN pip install --no-cache-dir -r requirements.txt

# 5. Copy the rest of the code
COPY . .

# 6. Command to run (RUNTIME)
CMD ["python", "train.py"]
```

### Layer Caching: Why Order Matters

Docker builds in layers. If you change code, you don't want to re-download all libraries.
- ❌ Slow: Copy everything → pip install
- ✅ MLOps Way: Copy requirements.txt → pip install → Copy code

### RUN vs CMD vs ENTRYPOINT

| Instruction | When | Purpose | Overridable? |
|-------------|------|---------|-------------|
| `RUN` | Build time (`docker build`) | Creates permanent layer | N/A |
| `CMD` | Runtime (`docker run`) | Default startup command | Yes — replaced by docker run args |
| `ENTRYPOINT` | Runtime (`docker run`) | Main program | No — args appended |

```dockerfile
FROM python:3.10-slim
WORKDIR /app
RUN date > /app/build_time.txt       # Runs ONCE during build
CMD ["cat", "/app/build_time.txt"]   # Reads frozen file at runtime
```

**Q: Build at 10 AM. `RUN date > time.txt`. Run container at 3 PM. What time shows?**
A: **10 AM.** `RUN` executes at build time. Result is baked into image layer.

### EXPOSE Misconception
```dockerfile
EXPOSE 8501
```
**Q: Does `EXPOSE` actually publish the port?**
A: **NO!** `EXPOSE` is documentation only. You need: `docker run -p 8501:8501 myimage`

### Docker ARG vs ENV
```dockerfile
ARG MODEL_PATH              # Build-time only (from --build-arg)
ENV MODEL_DIR=/opt/ml/model # Available at both build AND runtime
```
`ARG` disappears after build. `ENV` persists into the running container.

### Docker Storage

**Q: What happens to files created inside a container when it stops?**
A: **LOST** unless you used volumes or bind mounts.

| Type | Description |
|------|-------------|
| **Bind Mounts** | Maps host folder (`-v /host:/container`) |
| **Volumes** | Docker-managed persistent storage |

### Other Docker Knowledge

- **Docker Registry** = Any server storing images (generic term)
- **Docker Hub** = Docker's public registry (like GitHub for images)
- **The `.` in `docker build -t myimage .`** = build context (sends all files to daemon)
- **`--no-cache-dir`** in pip = prevents caching downloads (smaller image)
- **`python:3.10-slim`** = removes unnecessary packages (100MB vs 900MB+)

---

# PART 3: EXPERIMENT TRACKING & DATA VERSIONING

## 3.1 MLflow — The Three Pillars

| Pillar | Purpose | Details |
|--------|---------|---------|
| **1. Tracking** | Record & query experiments | Log code, data, config, results |
| **2. Models** | Standard packaging format | "Flavors" — works on Docker, Spark, Cloud |
| **3. Registry** | Central lifecycle hub | Promote: Staging → Production |

### MLflow Code Pattern (Assignment 3)
```python
import mlflow
import mlflow.pytorch

mlflow.set_tracking_uri("sqlite:///mlflow.db")     # or "http://localhost:5000"
mlflow.set_experiment("Assignment3_YourName")

def train_classifier(run_name, epochs, batch_size, lr):
    with mlflow.start_run(run_name=run_name):
        # 1. Log Parameters ("Input" config)
        mlflow.log_param("epochs", epochs)
        mlflow.log_param("batch_size", batch_size)
        mlflow.log_param("learning_rate", lr)

        # 2. Set Tags (for searching/filtering)
        mlflow.set_tag("student_id", "YOUR_ID")
        mlflow.set_tag("model_type", "CNN_Classifier")

        # 3. Training Loop
        for epoch in range(epochs):
            mlflow.log_metric("loss", epoch_loss, step=epoch)
            mlflow.log_metric("accuracy", epoch_acc, step=epoch)

        # 4. Save Model
        mlflow.pytorch.log_model(model, "cnn_model")

# 5 experiments with different hyperparameters
experiments = [
    {"run_name": "Run_1_Baseline",    "epochs": 5, "batch_size": 128, "lr": 0.001},
    {"run_name": "Run_2_High_LR",     "epochs": 5, "batch_size": 128, "lr": 0.05},
    {"run_name": "Run_3_Low_LR",      "epochs": 5, "batch_size": 128, "lr": 0.0001},
    {"run_name": "Run_4_Small_Batch", "epochs": 5, "batch_size": 32,  "lr": 0.001},
    {"run_name": "Run_5_Large_Batch", "epochs": 5, "batch_size": 512, "lr": 0.001},
]
for exp in experiments:
    train_classifier(**exp)
```
Launch UI: `mlflow ui --port 5000`

### mlflow.autolog() (not in slides but exam-relevant!)
```python
mlflow.autolog()    # Automatically logs params, metrics, model!
model.fit(X_train, y_train)
```
Works with: PyTorch, TensorFlow, Scikit-learn, XGBoost, LightGBM.

### Model Registry Lifecycle (not in slides!)
```
None → Staging → Production → Archived
```
```python
mlflow.register_model("runs:/abc123/model", "MyModel")
client.transition_model_version_stage("MyModel", version=1, stage="Production")
```

### MLflow Storage

| Component | Default | Production |
|-----------|---------|------------|
| Tracking data | `./mlruns/` | PostgreSQL database |
| Artifacts | `./mlruns/` | S3, GCS, Azure Blob |
| Tracking URI | `file:./mlruns` | `http://mlflow-server:5000` |

### Model Flavors

| Flavor | Module | Use Case |
|--------|--------|----------|
| `mlflow.sklearn` | Scikit-learn | Traditional ML |
| `mlflow.pytorch` | PyTorch | Deep learning |
| `mlflow.tensorflow` | TensorFlow | Deep learning |
| `mlflow.pyfunc` | Generic | Custom models |

### ⚠️ TRICKY EXAM QUESTIONS

**Q: What happens if you call `log_metric()` outside `with mlflow.start_run():`?**
A: Fails or creates implicit run. All logging MUST be inside the run context.

**Q: Can you log the same metric multiple times?**
A: Yes! Use `step=epoch` to create learning curves.

**Q: Difference between `log_param` and `log_metric`?**
A: Params = inputs (set once: LR, epochs). Metrics = outputs (can change: loss per epoch).

**Q: What is `set_tag` for?**
A: Labels for searching/filtering. Don't affect training.

## 3.2 TensorBoard vs MLflow

| Tool | Focus | Use Case |
|------|-------|----------|
| **MLflow** | End result (experiment-level) | Comparing runs, model registry |
| **TensorBoard** | Training process (step-level) | Real-time loss curves, histograms |

```python
from torch.utils.tensorboard import SummaryWriter
writer = SummaryWriter('logs/run_1')
for epoch in range(100):
    loss = train_step()
    writer.add_scalar('Loss/train', loss, epoch)
    writer.add_image('prediction_sample', img_grid, epoch)
writer.close()
```

## 3.3 Data Version Control (DVC)

### Why Git is Broken for Data
- Git stores full copies of binary files (no line-diffs)
- 100MB dataset × 10 versions = 1GB in `.git/`
- DevOps: Code A → Binary A
- **MLOps: Code A + Data B → Model C**

### How DVC Works
```bash
dvc add data/raw.csv         # Track the file
git add data/raw.csv.dvc     # Link to Git
git commit -m "Add raw data"
```

The `.dvc` Pointer File:
```yaml
outs:
- md5: a1b2c3d4e5f6g7h8...
  size: 1073741824
  path: raw.csv
```

`git pull` gets the pointer. `dvc pull` fetches the actual file.

### DVC in CI/CD
```yaml
steps:
  - uses: actions/checkout@v4      # Get .dvc pointers
  - run: pip install dvc[s3]       # Install DVC
  - run: dvc pull                  # Download actual data
  - run: python train.py           # Train
```

### ⚠️ TRICKY EXAM QUESTIONS

**Q: Does `git pull` download DVC-tracked data?**
A: NO! Only gets `.dvc` pointers. Need `dvc pull` for actual data.

**Q: Why must checkout come before `dvc pull`?**
A: Because `dvc pull` needs the `.dvc` pointer files tracked in Git.

---

# PART 4: CI/CD WITH GITHUB ACTIONS

## 4.1 CI/CD Concepts
- **CI:** Every `git push` → automated build and test
- **CD:** Every successful build → ready to deploy
- **Goal:** No model should reach production without automated tests

## 4.2 Tools for CI/CD

| Tool | Best For |
|------|----------|
| **GitHub Actions** | Built-in, free for public repos, startups |
| **GitLab CI/CD** | Private enterprise & security |
| **Jenkins** | Legacy systems & customization |
| **Managed Cloud** | Scaling & massive data |
| **Kubeflow Pipelines** | Kubernetes-native MLOps |

> "Tools change, but the YAML logic stays the same."

## 4.3 YAML Pipeline Anatomy
```yaml
# .github/workflows/NAME.yml
name: ...          # (Optional) Name in GitHub Actions tab
on: [...]          # (Required) Trigger events
jobs:              # (Required) Map of jobs (parallel by default!)
  job_id:
    runs-on: ubuntu-latest
    steps:
      - name: ...             # (Optional) Step name
        run: ...              # Execute shell command
        uses: ...             # Use pre-built action
        with:                 # Pass inputs to action
          param: value
```

## 4.4 Trigger Events

| Trigger | Example |
|---------|---------|
| `push` | `branches: [main]` or `branches-ignore: [main]` |
| `pull_request` | `branches: [main]` |
| `workflow_dispatch` | Manual "Run workflow" button in UI |
| `schedule` | Cron-based |

> Tip: `push: branches: [main]` for Deployment. `pull_request: branches: [main]` for Testing.

## 4.5 File Location & Activation
`.github/workflows/your-pipeline.yml` — folders must be lowercase, extension `.yml` or `.yaml`

```bash
mkdir -p .github/workflows
cp your-pipeline.yml .github/workflows/
git add .
git commit -m "adding CI/CD pipeline"
git push
```

## 4.6 Job Structure

| Key | Required? | Purpose |
|-----|-----------|---------|
| `runs-on` | Yes | VM type (`ubuntu-latest`) |
| `steps` | Yes | Sequential tasks |
| `needs` | No | Job dependencies |
| `if` | No | Conditional execution |
| `env` | No | Environment variables |

### Example: Single Job with Linting
```yaml
jobs:
  test_code:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Linting with flake8
        run: |
          pip install flake8
          flake8 .
```

## 4.7 End-to-End Pipeline
```yaml
name: MLOps End-to-End Pipeline
on:
  push:
    branches: [ dev ]
  pull_request:
    branches: [ main ]

jobs:
  test_and_validate:
    runs-on: ubuntu-latest
    steps: ...

  build_and_deploy:
    needs: test_and_validate   # Jobs run in PARALLEL by default!
    runs-on: ubuntu-latest
    steps: ...
```

## 4.8 Three Levels of ML Testing

| Test Type | What it Checks | Example |
|-----------|---------------|---------|
| **Unit Tests** | Individual components | `test_preprocess_nulls()` |
| **Integration Tests** | Data + Model pipeline | `test_input_shape()` |
| **Validation Tests** | Model performance | `assert accuracy > 0.80` |

```python
def test_prediction_range():
    model = load_model("models/latest.pkl")
    prediction = model.predict(test_sample)
    assert prediction >= 0 and prediction <= 1

def test_overfitting_check():
    assert metrics['train_loss'] > 1e-5
```

## 4.9 Building the Pipeline — 6 Steps

### Step 1: Simple Trigger
```yaml
name: Simple CI
on: [push]
jobs:
  train-model:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.10'
      - run: pip install -r requirements.txt
      - run: python train.py
```
❌ Issue: No comparison, no saving results.

### Step 2: Adding Observability (MLflow)
```yaml
      - run: pip install -r requirements.txt mlflow
      - name: Train and Log
        env:
          MLFLOW_TRACKING_URI: ${{ secrets.MLFLOW_TRACKING_URI }}
        run: python train.py
```

### Step 3: Fetching Best Model
```python
# get_best_model.py
import mlflow
client = mlflow.tracking.MlflowClient()
exp = client.get_experiment_by_name('...')
runs = client.search_runs(exp.experiment_id,
    order_by=['metrics.accuracy DESC'], max_results=1)
with open('best_model_uri.txt', 'w') as f:
    f.write(runs[0].info.artifact_uri + '/model')
```

### Step 4: Building Docker
```yaml
      - name: Docker Login
        uses: docker/login-action@v3
        with:
          username: ${{ secrets.DOCKER_USERNAME }}
          password: ${{ secrets.DOCKER_PASSWORD }}
      - name: Build and Push
        run: |
          MODEL_URI=$(cat best_model_uri.txt)
          docker build --build-arg MODEL_PATH=$MODEL_URI -t ${{ secrets.DOCKER_USERNAME }}/ml-app:latest .
          docker push ${{ secrets.DOCKER_USERNAME }}/ml-app:latest
```

### Step 5: Separation of Concerns
```yaml
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
❌ Issue: Jobs run in **PARALLEL**! Deploy starts before validate!

### Step 6: Final Pipeline with Dependencies
```yaml
on:
  push:
    branches: [main]
jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - name: Dry Run & Pytest
        run: pytest tests/ && python train.py --epochs 1
  deploy:
    needs: validate          # THE FIX!
    runs-on: ubuntu-latest
    steps:
      - name: Fetch the best model
        run: python get_best_model.py
      - name: Build docker
        run: |
          docker build --build-arg MODEL_PATH=$(cat best_model_uri.txt) -t app:latest .
          docker push app:latest
```

## 4.10 Dockerfile with Build Arguments (from Lecture 5)
```dockerfile
FROM python:3.10-slim
ARG MODEL_PATH
ENV MODEL_DIR=/opt/ml/model
COPY requirements.txt .
RUN apt-get update && apt-get install -y --no-install-recommends build-essential
RUN pip install --no-cache-dir -r requirements.txt
RUN mkdir -p ${MODEL_DIR}
RUN mlflow artifacts download --artifact-uri ${MODEL_PATH} --dst-path ${MODEL_DIR}
WORKDIR /app
COPY src/ ./
CMD ["python", "main.py"]
```

## 4.11 GHA Secrets
- Store in Settings → Secrets
- Access: `${{ secrets.SECRET_NAME }}`
- ❌ WRONG: `secrets.MLFLOW_URI`
- ✅ CORRECT: `${{ secrets.MLFLOW_URI }}`

## 4.12 Environment Variables Scope (hidden knowledge!)

| Scope | Visibility |
|-------|-----------|
| Workflow-level `env:` | All jobs and steps |
| Job-level `env:` | All steps in that job |
| Step-level `env:` | Only that step |

**Q: Can a step modify a workflow-level env variable?**
A: **NO!** Read-only at runtime. Use `echo "KEY=value" >> $GITHUB_ENV`.

## 4.13 Passing Data Between Steps
```yaml
# Method 1: GITHUB_ENV (persists across steps)
- run: echo "MODEL_ID=run_123" >> $GITHUB_ENV
- run: echo $MODEL_ID    # Works!

# Method 2: GITHUB_OUTPUT
- id: get-id
  run: echo "model_id=run_123" >> $GITHUB_OUTPUT
- run: echo ${{ steps.get-id.outputs.model_id }}
```

### ⚠️ TRICKY EXAM QUESTIONS

**Q: Do jobs run sequentially or in parallel by default?**
A: **PARALLEL!** Use `needs:` to make them sequential.

**Q: What happens if a step fails and the next has no `if:`?**
A: Next step SKIPPED because of the hidden `if: success()` default.

**Q: Can you access a file from Job A in Job B without artifacts?**
A: **NO!** Each job is a separate VM with an empty disk.

**Q: What does `exit 1` do?**
A: Causes the step to FAIL (non-zero exit code), stopping the pipeline.

---

# PART 5: ADVANCED CI/CD — CONDITIONALS, TRICKS & DEBUGGING

## 5.1 Key Rules: Job and Step Isolation

1. Each **Job** = separate VM (empty disk, no shared memory)
2. Each **Step** = separate shell (local variables die when step ends)
3. Communication between **Steps** → `env` or local files
4. Communication between **Jobs** → Artifacts (upload/download)
5. Global `env` blocks are **READ-ONLY** at runtime

## 5.2 Midterm Trick 1: Buggy YAML

❌ **Buggy:**
```yaml
jobs:
  train:
    runs-on: ubuntu-latest
    steps:
      - run: pip install -r requirements.txt
      - name: Checkout Code
      - name: Train
        env:
          MLFLOW_URI: secrets.MLFLOW_URI
        run: python train.py
      - name: Set Model Version
        run: VERSION="v1.2.3"
      - name: Tag Model
        run: echo "Tagging model as $VERSION"
```

✅ **Fixed:**
```yaml
jobs:
  train:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout Code            # Fix 1: checkout FIRST
        uses: actions/checkout@v4       # Fix 2: had no uses:
      - run: pip install -r requirements.txt
      - name: Train
        env:
          MLFLOW_URI: ${{ secrets.MLFLOW_URI }}   # Fix 3: correct syntax
        run: python train.py
      - name: Tag Model
        env:
          VERSION: "v1.2.3"             # Fix 4: var dies between steps
        run: echo "Tagging model as $VERSION"
```

**Bugs:** Missing checkout, checkout had no `uses:`, wrong secrets syntax, variable died between steps.

## 5.3 Midterm Trick 2: Job Data Sharing

❌ **Broken:**
```yaml
jobs:
  train:
    runs-on: ubuntu-latest
    steps:
      - run: echo "RUN_12345" > model_id.txt
  deploy:
    needs: train
    runs-on: ubuntu-latest
    steps:
      - run: cat model_id.txt   # ❌ FILE NOT FOUND!
```

✅ **Fixed:**
```yaml
jobs:
  train:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: echo "RUN_12345" > model_id.txt
      - uses: actions/upload-artifact@v4
        with:
          name: model-id-storage
          path: model_id.txt
  deploy:
    needs: train
    runs-on: ubuntu-latest
    steps:
      - uses: actions/download-artifact@v4
        with:
          name: model-id-storage
      - run: cat model_id.txt   # ✅ Works!
```

## 5.4 Midterm Trick 3: Docker Build vs Run
```dockerfile
RUN date > /app/build_time.txt    # Build time: runs ONCE, saved in layer
CMD ["cat", "/app/build_time.txt"] # Runtime: reads the "frozen" file
```

## 5.5 Status Functions

| Function | Behavior |
|----------|----------|
| `success()` | **(Hidden default)** Run only if no previous step failed |
| `failure()` | Run only if previous step failed |
| `cancelled()` | Run only if human clicked "Cancel" |
| `always()` | Run **no matter what** (cleanup GPU!) |

## 5.6 THE HIDDEN `success()` — CRITICAL CONCEPT

What you write:
```yaml
- name: step1
  run: ...
- name: step2
  run: ...
```

What GHA actually sees:
```yaml
- name: step1
  if: success()     # HIDDEN!
  run: ...
- name: step2
  if: success()     # HIDDEN!
  run: ...
```

**As soon as you write a custom `if:`, the hidden `success()` is DISABLED!**

```yaml
# ❌ WRONG — publish runs even if compile/test failed!
  - name: publish
    if: github.ref == 'refs/heads/main'
    run: ./publish.sh

# ✅ CORRECT
  - name: publish
    if: success() && github.ref == 'refs/heads/main'
    run: ./publish.sh
```

## 5.7 Selective Training (Gatekeeper Logic)

3 conditions — ALL must be true:
```yaml
if: >
  needs.code-check.result == 'success' &&
  github.ref_name == 'main' &&
  contains(github.event.head_commit.message, '[run-train]')
```

## 5.8 Full Gatekeeper Pipeline (from Code.md + Assignment 6)
```yaml
name: Gatekeeper CI/CD Pipeline
on:
  push:
    branches: ["*"]
jobs:
  code-check:
    name: Linter
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: echo "No issues found"

  model-training:
    name: Training Job
    needs: code-check
    runs-on: ubuntu-latest
    if: >
      needs.code-check.result == 'success' &&
      github.ref_name == 'main' &&
      contains(github.event.head_commit.message, '[run-train]')
    steps:
      - uses: actions/checkout@v4
      - name: Run training
        run: |
          echo "Training started..."
          exit 1                           # Simulate failure
      - name: Create error logs
        if: failure()                      # Only on failure
        run: echo "Training failed" > error_logs.txt
      - name: Upload logs
        if: failure()
        uses: actions/upload-artifact@v4
        with:
          name: error_logs
          path: error_logs.txt
      - name: Cleanup
        if: always()                       # ALWAYS runs
        run: echo "Cleaning up .."

  training-status:
    name: Status Report
    runs-on: ubuntu-latest
    needs: model-training
    if: always()                           # Even if training skipped
    steps:
      - run: |
          if [ "${{ needs.model-training.result }}" = "success" ]; then
            echo "STATUS: SUCCESS"
          elif [ "${{ needs.model-training.result }}" = "failure" ]; then
            echo "STATUS: FAILURE"
          else
            echo "STATUS: SKIPPED"
          fi
```

## 5.9 Full ML CI-CD Pipeline (from Code.md)
```yaml
name: ML CI-CD Pipeline
on: [push]
jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.10"
      - run: pip install -r requirements.txt
      - run: flake8 src/

  train:
    needs: lint
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.10"
      - run: pip install -r requirements.txt
      - run: python train.py
      - uses: actions/upload-artifact@v4
        with:
          name: model
          path: model.pkl

  deploy:
    needs: train
    runs-on: ubuntu-latest
    if: success() && github.ref == 'refs/heads/main'
    steps:
      - uses: actions/checkout@v4
      - uses: actions/download-artifact@v4
        with:
          name: model
      - run: docker build -t myapp:latest .
      - run: echo "${{ secrets.DOCKER_PASSWORD }}" | docker login -u "${{ secrets.DOCKER_USERNAME }}" --password-stdin
      - run: |
          docker tag myapp:latest myrepo/myapp:latest
          docker push myrepo/myapp:latest
```

## 5.10 Assignment 5: Multi-Job Pipeline

**train.py** (writes `model_info.txt`):
```python
import mlflow, mlflow.sklearn
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score

mlflow.set_tracking_uri(os.getenv("MLFLOW_TRACKING_URI", "file:./mlruns"))
mlflow.set_experiment("assignment5")

with mlflow.start_run() as run:
    clf = RandomForestClassifier(n_estimators=100, random_state=42)
    clf.fit(X_train, y_train)
    accuracy = accuracy_score(y_test, clf.predict(X_test))
    mlflow.log_param("n_estimators", 100)
    mlflow.log_metric("accuracy", accuracy)
    mlflow.sklearn.log_model(clf, artifact_path="model")

    with open("model_info.txt", "w") as f:
        f.write(f"{run.info.run_id}\n")
        f.write(f"{accuracy:.4f}\n")
```

**check_threshold.py:**
```python
import sys
THRESHOLD = 0.85
with open("model_info.txt") as f:
    lines = f.read().strip().splitlines()
accuracy = float(lines[1].strip())
if accuracy < THRESHOLD:
    sys.exit(1)    # EXIT CODE 1 = FAILS THE PIPELINE
print("✅ PASSED")
```

**Dockerfile with ARG:**
```dockerfile
FROM python:3.10-slim
ARG RUN_ID
ENV RUN_ID=${RUN_ID}
RUN pip install --no-cache-dir mlflow scikit-learn
WORKDIR /app
RUN mkdir -p /app/model && echo "${RUN_ID}" > /app/model/run_id.txt
CMD ["python", "-c", "import os; print(f'Run ID: {os.environ[\"RUN_ID\"]}')"]
```

**Pipeline YAML:**
```yaml
name: ML Validation and Deployment Pipeline
on:
  push:
    branches: [main]
jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.10"
      - run: pip install -r requirements.txt
      - name: Train model
        env:
          MLFLOW_TRACKING_URI: ${{ secrets.MLFLOW_TRACKING_URI }}
        run: python train.py
      - uses: actions/upload-artifact@v4
        with:
          name: model-artifacts
          path: model_info.txt
  deploy:
    needs: validate
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.10"
      - run: pip install -r requirements.txt
      - uses: actions/download-artifact@v4
        with:
          name: model-artifacts
          path: .
      - run: python check_threshold.py
      - run: |
          RUN_ID=$(head -1 model_info.txt)
          docker build --build-arg RUN_ID="${RUN_ID}" -t ml-model:${RUN_ID} .
```

## 5.11 Assignment 7: 3-Job DAG Pipeline (Audit → Build → Promote)

### 1. `check_data.py` (Data Schema & Range Check)
```python
import os
import sys
import pandas as pd
import argparse

def main():
    parser = argparse.ArgumentParser(description="Integrity Audit - Schema and Quality Checks")
    parser.add_argument("--data", type=str, required=True, help="Path to the dataset CSV file")
    args = parser.parse_args()

    print(f"Starting Integrity Audit on file: {args.data}")

    # Check if the data file exists
    if not os.path.exists(args.data):
        print(f"[-] ERROR: Data file {args.data} does not exist!")
        sys.exit(1)

    # Read dataset
    try:
        df = pd.read_csv(args.data)
    except Exception as e:
        print(f"[-] ERROR: Failed to read CSV data. Reason: {e}")
        sys.exit(1)

    # Schema Check (Required Columns)
    required_cols = {"id", "age", "blood_pressure", "cholesterol", "outcome"}
    current_cols = set(df.columns)
    missing_cols = required_cols - current_cols

    if missing_cols:
        print(f"[-] SCHEMA ERROR: Missing required columns: {missing_cols}")
        sys.exit(1)
    print("[+] Schema Check: PASSED")

    # Data Quality Checks (Nulls and Range Validations)
    null_counts = df.isnull().sum().sum()
    if null_counts > 0:
        print(f"[-] QUALITY ERROR: Found {null_counts} missing/null values in data!")
        sys.exit(1)
    
    invalid_age = df[df["age"] <= 0]
    if not invalid_age.empty:
        print(f"[-] QUALITY ERROR: Invalid age records found: \n{invalid_age}")
        sys.exit(1)

    print("[+] Quality Checks: PASSED")
    print("[+] Integrity Audit Completed Successfully. Status: APPROVED")

if __name__ == "__main__":
    main()
```

### 2. `Dockerfile` (Multi-stage Forensic Build)
```dockerfile
# STAGE 1: Builder Stage
FROM python:3.10-slim AS builder
WORKDIR /build
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# STAGE 2: Runner Stage (Production minimal environment)
FROM python:3.10-slim AS runner
WORKDIR /app
COPY --from=builder /root/.local /root/.local
COPY serve.py .
ENV PATH=/root/.local/bin:$PATH
EXPOSE 8080
CMD ["python", "serve.py"]
```

### 3. `.github/workflows/pipeline.yaml` (The 3-Job DAG)
```yaml
name: High-Integrity Promotion Pipeline

on:
  push:
    branches:
      - '**'
    tags:
      - 'v*'

jobs:
  integrity-audit:
    name: Integrity Audit (Data & Code)
    runs-on: ubuntu-latest
    steps:
      - name: Checkout Code
        uses: actions/checkout@v4

      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.10'

      - name: Install Dependencies
        run: pip install dvc pandas

      - name: Initialize Mock DVC & Pull Dataset
        run: |
          git config --global user.email "mlops-bot@safehealth.com"
          git config --global user.name "SafeHealth MLOps Bot"
          dvc init --no-scm -f
          mkdir -p /tmp/dvc-remote
          dvc remote add -d local-remote /tmp/dvc-remote
          echo "id,age,blood_pressure,cholesterol,outcome" > data.csv
          echo "1,45,120,200,0" >> data.csv
          dvc add data.csv
          dvc push
          rm data.csv
          dvc pull data.csv.dvc

      - name: Run Schema and Quality Audits
        run: python check_data.py --data data.csv

  forensic-build:
    name: Forensic Build (Docker)
    needs: integrity-audit
    runs-on: ubuntu-latest
    # Only run on main branch with [build-image] OR when tag is pushed
    if: >-
      (github.ref == 'refs/heads/main' && contains(github.event.head_commit.message, '[build-image]')) ||
      startsWith(github.ref, 'refs/tags/v')
    steps:
      - name: Checkout Code
        uses: actions/checkout@v4

      - name: Build Docker Image
        run: |
          docker build -t safehealth-predictor:latest . > docker_build.log 2>&1
          echo "[+] Docker Build succeeded!"

      - name: Generate Build Crash Logs on Failure
        if: failure()
        run: |
          echo "=== ERROR SYSTEM DUMP ===" > build_crash.log
          cat docker_build.log >> build_crash.log

      - name: Upload Build Artifact on Failure
        if: failure()
        uses: actions/upload-artifact@v4
        with:
          name: build-crash-logs
          path: build_crash.log
          retention-days: 7

  production-promotion:
    name: Production Promotion (The Final Gate)
    needs: forensic-build
    runs-on: ubuntu-latest
    # Strictly restricted: only runs when a Git Tag (v*) is pushed
    if: startsWith(github.ref, 'refs/tags/v')
    steps:
      - name: Extract Tag Version
        run: echo "TAG_VERSION=${GITHUB_REF#refs/tags/}" >> $GITHUB_ENV

      - name: Promote Image to Clinic Production Registry
        run: |
          echo "=== CLINICAL PRODUCTION REGISTRY PROMOTION ==="
          echo "Promoting safehealth-predictor:${{ env.TAG_VERSION }} to Clinic production cluster..."
```

## 5.12 Assignment 9: Buggy YAML Exercise (Find 9 Errors!)

```yaml
name: test
on:
  push:
jobs:
  lint:
    runs-on: ubuntu-latest
  steps:                               # Bug 1: wrong indentation level
    - name: setup python
      uses: actions/setup-python@v3
      with:
        python: version:"3.10"         # Bug 2: python-version: "3.10"
    - name: lint
      run: flake src/                  # Bug 3: flake8 src/
  train:
    needs: lint
    runs-on: ubuntu-latest
    steps:
      - name: checkout code
        uses: actions/checkout@v4
        uses: actions/setup-python@v3  # Bug 4: missing - name:
        with:
          python: version:"3.10"       # Bug 5: same syntax error
      - name: install dependencies
        runs: pip install -r requirement.txt  # Bug 6: runs→run, requirement→requirements
      - name: train model
        run: python train.py
  deploy:
    needs: train
    runs-on: ubuntu-latest
    if: success() && github.ref == 'refs/heads/main'
    steps:
      - uses: actions/checkout@v3
      - uses: actions/download-artifact@v3
        with: model                    # Bug 7: with:\n  name: model
      - run: docker build -t docker myapp:latest .  # Bug 8: extra 'docker'
      - run: docker tag myapp:latest myrepo/app:latest
      - run: docker push myrepo/myapp:latest  # Bug 9: app vs myapp mismatch
```

### ⚠️ TRICKY EXAM QUESTIONS

**Q: `branches: [main]` vs `branches-ignore: [main]`?**
A: `branches` = ONLY on main. `branches-ignore` = ALL branches EXCEPT main.

**Q: Custom `if:` on a step — does it check for previous failures?**
A: **NO!** Custom `if:` overrides hidden `success()`. Fix: `if: success() && ...`

**Q: Set variable in one step, read in next?**
A: Not with shell vars (each step is new shell). Use `echo "KEY=val" >> $GITHUB_ENV`.

---

# PART 6: KUBERNETES — CONTAINER ORCHESTRATION

## 6.1 Motivation: PersonaCanvas

A platform with: Web App, AI Model, Printing, Payment, Shipping.
**Should all be in one container? NO!**

Why separate:
- **Efficient Resources:** GPU only for AI, CPU for web
- **Independent Scaling:** Scale web during demand
- **Fault Isolation:** One crash ≠ entire system down
- **Communication:** REST APIs between services

## 6.2 What is Kubernetes?

- Open-source platform for container orchestration
- Coordinates cluster of computers as a single unit
- K8s = "K-ubernete-s" (8 letters between K and s)
- **K8s is the "OS" for the modern cloud-native data center**

## 6.3 Architecture: Key Concepts

| Concept | Definition |
|---------|-----------|
| **Pod** | Smallest unit. 1+ containers sharing network (IP) & storage. **95% of time: 1 Pod = 1 Container** |
| **Node** | Worker machine (VM or Physical). Where Pods live |
| **Kubelet** | Agent on each Node — manages Node, communicates with Control Plane |
| **Service** | Stable entry point. Fixed address + load balancer (Pods die & restart with new IPs) |
| **Volume** | Persistent storage. Local or remote (S3, GDrive) |
| **Cluster** | Set of Nodes managed by central Control Plane |

## 6.4 Control Plane (Main Node)

| Component | Role |
|-----------|------|
| **API Server** | Central entry point. Validates & processes requests |
| **etcd** | Cluster's database. Stores all state |
| **Scheduler** | Matches Pods to best available Node (GPU, RAM) |
| **Controller Manager** | Ensures Current State matches Desired State |

- **Self-healing:** Node goes down → Controller replaces pods on another Node
- **HA:** Production uses 2-3 Master Nodes
- **If etcd goes down → cluster "freezes"**

## 6.5 Network Stability

- Pods are **ephemeral** — replacement gets different IP
- **Services** provide Permanent Virtual IP — stable "front door"
- **Internal Service (ClusterIP):** Inside cluster (web → AI)
- **External Service (NodePort):** Exposed to world

> **KEY: Never talk to a Pod IP. Always talk to a Service!**

## 6.6 Interacting with K8s

| Approach | Method | Best For |
|----------|--------|----------|
| **Imperative** | `kubectl` commands | Testing, debugging |
| **Declarative** | YAML files | Production, teamwork |

> **Rule:** Use `kubectl` to **inspect**, use YAML to **configure**.

```bash
minikube start          # Start cluster
kubectl cluster-info    # Check status
kubectl get nodes       # See nodes
```

## 6.7 Deployment YAML — Step by Step

### Lecture 7 (Simple, no resources):
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: personacanvas-frontend
spec:
  replicas: 3
  selector:
    matchLabels:
      app: web-ui
  template:
    metadata:
      labels:
        app: web-ui
    spec:
      containers:
      - name: streamlit-app
        image: almond/streamlit-k8s-demo:latest
        ports:
        - containerPort: 8501
```

### Lecture 8 Part 1 — Metadata:
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: personacanvas-frontend
  labels:
    owner: company-x
    app: streamlit-web
    tier: frontend
    version: 1.1
```
- `kubectl delete deployment personacanvas-frontend` — delete by name
- `kubectl get deployments -l tier=frontend` — filter by label

### Lecture 8 Part 2 — Spec:
```yaml
spec:
  replicas: 3
  selector:
    matchLabels:
      app: streamlit-web
  template:
    metadata:
      labels:
        app: streamlit-web
    spec:
      containers:
      - name: ...
        image: ...
        ports: ...
        resources: ...
```

### Lecture 8 Full (with resources):
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: personacanvas-frontend
  labels:
    app: streamlit-web
    tier: frontend
spec:
  replicas: 3
  selector:
    matchLabels:
      app: streamlit-web
  template:
    metadata:
      labels:
        app: streamlit-web
    spec:
      containers:
      - name: streamlit-container
        image: your-username/streamlit:latest
        ports:
        - containerPort: 8501
        resources:
          requests:           # Minimum guaranteed
            cpu: "250m"       # 0.25 core
            memory: "256Mi"
          limits:             # Maximum allowed
            cpu: "500m"       # Throttled if exceeded
            memory: "512Mi"   # KILLED if exceeded (OOM)
```

> **CRITICAL:**
> - CPU limit exceeded → K8s **SLOWS DOWN** the CPU (not killed)
> - Memory limit exceeded → K8s **IMMEDIATELY KILLS** the process (OOM)

### AI Backend with GPU:
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: personacanvas-backend
  labels:
    app: image-generator
    tier: backend
spec:
  replicas: 1
  selector:
    matchLabels:
      app: image-generator
  template:
    metadata:
      labels:
        app: image-generator
    spec:
      containers:
      - name: generator-core
        image: your-docker-username/image-gen:latest
        ports:
        - containerPort: 5000
        resources:
          requests:
            memory: "4Gi"
            cpu: "2000m"
            nvidia.com/gpu: 1
          limits:
            memory: "8Gi"
            cpu: "4000m"
            nvidia.com/gpu: 1
```

## 6.8 Service YAML

### Lecture 7 (Simple):
```yaml
apiVersion: v1
kind: Service
metadata:
  name: frontend-service
spec:
  type: NodePort
  selector:
    app: web-ui
  ports:
    - protocol: TCP
      port: 80
      targetPort: 8501
```

### Lecture 8 (Full with NodePort):
```yaml
apiVersion: v1
kind: Service
metadata:
  name: streamlit-service
spec:
  type: NodePort
  selector:
    app: streamlit-web          # MUST match Deployment label!
  ports:
    - name: web
      protocol: TCP
      port: 80                  # INTERNAL cluster port
      targetPort: 8501          # POD/container port
      nodePort: 30085           # EXTERNAL port (30000-32767)
```

**Traffic Flow:**
1. User → `http://<Server-IP>:30085`
2. NodePort catches request
3. Service finds Pods labeled `app: streamlit-web`
4. Forwards to port 8501 in Pod
5. Streamlit responds

## 6.9 kubectl Commands
```bash
kubectl apply -f deployment.yaml       # Apply (create or update)
kubectl get pods                        # Check pod status
kubectl get deployments                 # Check deployments
kubectl get service streamlit-service   # Check service
kubectl get nodes -o wide               # Node details
kubectl get deployments -l tier=frontend # Filter by label
kubectl scale deployment backend --replicas=10  # Scale up
kubectl delete pod <pod-name>           # Test self-healing
kubectl set image deployment/backend container=new-image:v2  # Rolling update
```

## 6.10 Service Types

| Type | Access | Use Case |
|------|--------|----------|
| **ClusterIP** (default) | Internal only (pod-to-pod) | Backend AI service |
| **NodePort** | External on port 30000-32767 | Frontend web app |
| **LoadBalancer** | Cloud provider LB | Production |

Assignment 9: Frontend = NodePort, Backend = ClusterIP.
Frontend calls backend: `http://backend-service:5000`

## 6.11 Hidden K8s Knowledge

### Liveness vs Readiness Probes

| Probe | Question | On Failure |
|-------|----------|-----------|
| **Liveness** | Is container alive? | K8s **kills and restarts** it |
| **Readiness** | Is container ready? | K8s **removes from Service** (no traffic) |

```yaml
livenessProbe:
  httpGet:
    path: /health
    port: 5000
  initialDelaySeconds: 30
  periodSeconds: 10
```

### K8s Secrets (NOT encrypted by default!)
```yaml
apiVersion: v1
kind: Secret
metadata:
  name: mlflow-credentials
type: Opaque
data:
  username: YWRtaW4=          # base64 encoded, NOT encrypted!
  password: cGFzc3dvcmQ=
```

### ConfigMaps
```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: model-config
data:
  MODEL_VERSION: "v2.1"
  BATCH_SIZE: "32"
```
**Secrets** = passwords. **ConfigMaps** = everything else.

### Other Hidden Concepts

| Concept | Detail |
|---------|--------|
| **Namespaces** | Logical isolation (`kubectl get pods -n production`) |
| **RollingUpdate** (default) | Gradually replaces pods — no downtime |
| **Recreate** | Kills all old, creates new — has downtime |
| `kubectl apply` | Idempotent (create or update) |
| `kubectl create` | Fails if already exists |
| `imagePullPolicy: Always` | Pull image every time Pod starts |

**Q: Push new image with same tag. Will K8s auto-update?**
A: **NO!** Must use `imagePullPolicy: Always`, change tag, or `kubectl rollout restart`.

**Q: What happens to container filesystem data when Pod restarts?**
A: **GONE** unless using PersistentVolume.

### ⚠️ TRICKY EXAM QUESTIONS

**Q: CPU limit exceeded?** A: Throttled (slowed), NOT killed.

**Q: Memory limit exceeded?** A: **IMMEDIATELY KILLED** (OOM).

**Q: Can Pods communicate by Pod IP?** A: Technically yes, but **NEVER do this**. Use Services.

**Q: Valid nodePort range?** A: 30000-32767.

**Q: Delete a Pod managed by Deployment?** A: K8s auto-creates new one (self-healing).

**Q: etcd goes down?** A: Cluster "freezes."

**Q: `requests` vs `limits`?** A: requests = guaranteed minimum (scheduling). limits = max allowed (enforced).

## 6.12 Assignment 8: Kubernetes Frontend Deployment

### 1. `deployment.yaml` (Frontend Deployment)
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: personacanvas-frontend
  labels:
    app: streamlit-web
    tier: frontend
spec:
  replicas: 3
  selector:
    matchLabels:
      app: streamlit-web
  template:
    metadata:
      labels:
        app: streamlit-web
    spec:
      containers:
      - name: streamlit-container
        image: almond/streamlit-k8s-demo:latest
        ports:
        - containerPort: 8501
        resources:
          requests:
            cpu: "250m"
            memory: "256Mi"
          limits:
            cpu: "500m"
            memory: "512Mi"
```

### 2. `service.yaml` (NodePort Service Setup)
```yaml
apiVersion: v1
kind: Service
metadata:
  name: frontend-service
spec:
  type: NodePort
  selector:
    app: streamlit-web # Must match labels in deployment
  ports:
    - name: web
      protocol: TCP
      port: 80         # Internal cluster port
      targetPort: 8501 # Container Port Streamlit is running on
      nodePort: 30085  # External access port (30000-32767)
```

**Step-by-Step CLI Execution Commands:**
```bash
minikube start                                      # Start Cluster
kubectl apply -f deployment.yaml                    # Create 3 replicas
kubectl apply -f service.yaml                       # Expose via NodePort 30085
kubectl get pods                                    # Verify status "Running"
minikube service frontend-service                   # Launch app in browser
```

---

# PART 7: KUBEFLOW & PRODUCTION MONITORING

## 7.1 Why GHA + K8s Isn't Enough

| Problem | GHA | Kubeflow |
|---------|-----|---------|
| **Data Moving** | 1TB to external runner = impossible | Runs where data lives |
| **Hardware** | Standard CPUs | Native K8s GPU scheduling |
| **Caching** | Full restart on failure | Step-level caching |
| **Hyperparameter Tuning** | Linear queue | Natural parallel explosion |

> Use **GHA** for CI (code integrity). Use **Kubeflow** for MLOps (science reproducibility).

## 7.2 GHA vs Kubeflow Side-by-Side

| Feature | GHA | Kubeflow |
|---------|-----|---------|
| Primary Goal | Building & Testing | Managing ML Factory |
| Infrastructure | General Cloud VMs | Inside K8s Cluster |
| Data Handling | Upload/Download artifacts | Mounts Persistent Volumes |
| State & Failure | Restarts from Step 1 | Step-Level Caching |
| Trigger | Code Push (Git events) | Data Event (file saved) |

## 7.3 Three Scenarios

### Scenario 1: Data Sharing (1TB Protein Sequences)
- **GHA:** Upload 1TB as artifact → download in next job = impossible
- **Kubeflow:** Data stays on shared Persistent Volume → next step reads directly

### Scenario 2: Resource Sharing (OOM)
- **GHA:** Both jobs start → OOM kills one (60GB + 8GB > 64GB)
- **Kubeflow:** Queues Job B in PENDING until Job A releases resources

### Scenario 3: Caching
- **GHA:** Restart whole job (re-run 1hr data fetch)
- **Kubeflow:** Skip completed steps from cache, resume at failure point

## 7.4 Kubeflow Platform Components

| Component | Purpose |
|-----------|---------|
| **Notebooks** | Jupyter/VS Code as scalable Pods |
| **Pipelines** | Multi-step workflows (Data → Train → Deploy) |
| **Katib** | Automated hyperparameter tuning (AutoML) |
| **KServe** | Model serving with "Scale-to-Zero" |

## 7.5 Kubeflow Python SDK

**Define Components:**
```python
from kfp import dsl, compiler

# Each @dsl.component runs in its own container/Pod
@dsl.component(base_image='python:3.9')
def preprocess_data(data_path: str, cleaned_data: dsl.OutputPath(str)):
    # dsl.OutputPath writes to shared Persistent Volume
    with open(cleaned_data, 'w') as f:
        f.write("/mnt/data/cleaned_sequences.bin")

@dsl.component(base_image='pytorch/pytorch:latest', packages_to_install=['mlflow'])
def train_model(cleaned_data_path: dsl.InputPath(str), epochs: int, lr: float):
    # dsl.InputPath reads from same shared volume
    mlflow.log_param("learning_rate", lr)
```

**Define Pipeline:**
```python
@dsl.pipeline(name="personacanvas-research-lifecycle")
def research_pipeline(data_path: str = "s3://.../raw-v1", lr: float = 0.01):
    # Task 1: Preprocess (High-RAM)
    prep_task = preprocess_data(data_path=data_path)
    prep_task.set_memory_limit('60Gi')
    prep_task.set_cpu_limit('4')

    # Task 2: Train (GPU) — waits if Task 1 takes all RAM
    train_task = train_model(
        cleaned_data_path=prep_task.outputs['cleaned_data'],
        epochs=10, lr=lr)
    train_task.set_gpu_limit(1)       # nvidia.com/gpu
    train_task.set_memory_limit('8Gi')

    # Caching: If train fails, re-run skips prep_task

# Compile: Python → Kubeflow YAML
if __name__ == "__main__":
    compiler.Compiler().compile(research_pipeline, 'research_pipeline.yaml')
```

**Key SDK Concepts:**
- `@dsl.component` → each function runs in its own container
- `dsl.OutputPath` → writes to shared Persistent Volume
- `dsl.InputPath` → reads from same volume
- `.set_memory_limit()` / `.set_gpu_limit()` → resource declarations
- `compiler.Compiler().compile()` → converts Python → YAML

## 7.6 Production Monitoring

> *"If we can measure, then we can compare. And if we can compare, only then can we improve."*

### Three Dimensions

| Dimension | Focus | Metrics |
|-----------|-------|---------|
| **1. Service** | Infrastructure | Prediction latency, performance cliffs, cost |
| **2. Data** | Input/Output | Quality checks, data drift, concept drift |
| **3. Model** | Logic | Real-time actuals, delayed actuals, proxy measures |

### Types of Drift

| Drift Type | Definition | Example |
|------------|-----------|---------|
| **Data Drift (Prompt Drift)** | Input distribution shifts | Simple → complex 50+ keyword prompts |
| **Concept Drift** | Input-output relationship changes | Model trained for "art" but users want "photos" |

### The "Silent Failure" Scenario
- Infrastructure perfect (200 OK, stable GPU, low queue)
- But users complain about degraded quality
- Root causes: Prompt Drift + Concept Drift

### Closed-Loop System
1. **Automated Evaluation:** Sidecar container computes CLIP scores. Alert if < 0.25
2. **Human-in-the-Loop (HITL):** Low-confidence → labeling UI → 👍/👎 → Gold Standard dataset
3. **Triggered Retraining:** 1000 new examples → Kubeflow auto-triggers fine-tuning

## 7.7 The Complete MLOps Lifecycle
```
Foundations (DevOps, Git, Conda)
  → Reproducibility (Docker, DVC, MLflow)
    → Automation (CI/CD, GitHub Actions)
      → Orchestration (K8s, Nodes, Pods)
        → Networking (Services, Deployments)
          → Operations (Kubeflow, Monitoring)
```

> **GHA** = Software Architect: "Is the code tested? Does Docker build?"
> **Kubeflow** = Research Scientist: "Is the model accurate? Can we train on GPUs?"
> **GHA builds the Engine (CI). Kubeflow Drives the experiment (MLOps).**

### ⚠️ TRICKY EXAM QUESTIONS

**Q: Data Drift vs Concept Drift?**
A: Data Drift = inputs changed. Concept Drift = meaning of "correct output" changed.

**Q: Can a model fail silently with all infra metrics green?**
A: **YES!** Silent Failure — system healthy but predictions degraded.

**Q: Why can't standard K8s replace Kubeflow?**
A: K8s manages "always-on" services. Lacks: DAG orchestration, step-level caching, data lineage, data-event triggers.

**Q: Why do we need BOTH MLflow AND DVC?**
A: MLflow = experiments (params, metrics, models). DVC = data versions. Together: Code (Git) + Data (DVC) + Experiments (MLflow) = full reproducibility.

**Q: Why BOTH GHA AND Kubeflow?**
A: GHA = CI/CD (code quality). Kubeflow = ML operations (training, GPU scheduling). They complement each other.

**Q: Full pipeline — which tool for each step?**
A: Git Push → DVC Pull → Pytest → MLflow → Docker → K8s/Kubeflow → Monitoring

**Q: What is idempotency?**
A: Running multiple times gives same result. `kubectl apply` = idempotent. `kubectl create` = NOT.

**Q: What is training-serving skew?**
A: Training features differ from serving features → silent production failures.

**Q: Why `random_state=42`?**
A: Reproducibility! Without fixed seed, random operations produce different results each run.

---

> *"You are no longer just building models. You are engineering the systems that bring science to life."*
