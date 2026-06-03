# 📚 DSAI-406 MLOps — Complete Study Summary

> **Course:** ML Engineering for Production (DSAI 406)
> **Instructor:** Dr. Mohamed Ghalwash — Zewail City of Science and Technology
> **Textbook:** *Practical MLOps*, Noah Gift & Alfredo Deza (2021)
> **Supplementary:** *Reliable Machine Learning*, Cathy Chen et al. (2022)

---

## Table of Contents

1. [Lecture 1 — Introduction to MLOps](#lecture-1--introduction-to-mlops)
2. [Lecture 2 — Reproducibility (Conda, Git, Docker)](#lecture-2--reproducibility)
3. [Lecture 3 — Experiment Tracking (MLflow)](#lecture-3--experiment-tracking-mlflow)
4. [Lecture 4 — CI/CD & GitHub Actions](#lecture-4--cicd--github-actions)
5. [Lecture 5 — Advanced CI/CD Pipelines & DVC](#lecture-5--advanced-cicd-pipelines--dvc)
6. [Lecture 6 — Conditional Execution & Midterm Tricks](#lecture-6--conditional-execution--midterm-tricks)
7. [Lecture 7 — Kubernetes (K8s) Fundamentals](#lecture-7--kubernetes-fundamentals)
8. [Lecture 8 — K8s Deployments, Services & Hands-On](#lecture-8--k8s-deployments-services--hands-on)
9. [Lecture 9 — Kubeflow Pipelines & Production Monitoring](#lecture-9--kubeflow-pipelines--production-monitoring)
10. [Assignment Summary & Key Takeaways](#assignment-summary--key-takeaways)
11. [The Complete MLOps Lifecycle](#the-complete-mlops-lifecycle)

---

## Lecture 1 — Introduction to MLOps

### Model Development Pipeline
The standard development flow:
```
Data (CSV) → Notebook → Feature Engineering → Model Training → Accuracy
```
- A small change in library version when deploying to production breaks **Reproducibility**

### Hidden Technical Debt (NeurIPS 2015, Google)
- ML systems require robust engineering beyond just algorithm development
- The ML code is only a small fraction of a real-world ML system
- Surrounding infrastructure includes: data collection, data verification, feature extraction, configuration, monitoring, serving infrastructure, process management tools
- **Goal:** Not to add new functionality, but to enable future improvements, reduce errors, and improve maintainability

> **MLOps = Automation + Shipping**

### The "Ops" Family

| Ops Type | Focus | Key Tasks |
|----------|-------|-----------|
| **DevOps** | Increase velocity of releasing high-quality software | Git versioning, unit/integration tests, deploying binaries/services |
| **DataOps** | Data quality & agility | DVC versioning, data validation, periodic/streaming/event-driven data |
| **MLOps** | Intersection of ML + DevOps + Data Engineering | Git + DVC + Model Registry, data validation + model quality, deploying prediction pipelines, handling data drift |

### What is MLOps?
- MLOps is the process of **automating machine learning using DevOps methodologies**
- Not only software engineering processes need automation, but also the **data** and **modeling**
- Additional monitoring for things like **data drift**
- **MLOps Tasks:**
  - Versioning: Git (Code) + DVC (Data) + Model Registry
  - Testing: Unit/Integration tests + Data Validation + Model Quality
  - Deployment: Prediction pipeline (not just a binary/service)
  - Maintenance: Models decay → Data Drift

### MLOps Topics
- Continuous improvement / integration / delivery
- Cloud Computing
- AutoML
- Containers
- Edge Computing
- Model Portability

### Key Roles
- **Data Scientist:** Builds models, focuses on accuracy
- **ML Engineer:** Productionizes models, focuses on reliability
- **ML Researcher:** Advances the state of the art

---

## Lecture 2 — Reproducibility

### Lessons from Assignment 1
- **Dependency Hell:** Student A has scikit-learn 1.2, Student B has 0.24
- **Python Versions:** 3.8 vs 3.11 changes everything
- **Path Issues:** Hardcoded paths don't transfer between machines
- **Ghost Data:** Unexplained files with no provenance

> **"If the software isn't reproducible with one command, MLOps doesn't exist."**

### Development Environments: Conda vs. Pip

| Feature | `pip` + `venv` | Conda / Mamba |
|---------|---------------|---------------|
| **Focus** | Python packages only | Python + Non-Python (C++, CUDA, R) |
| **ML Use Case** | Simple web APIs/microservices | The standard for Data Science (GPU/CUDA drivers) |

**Rule:** Never use your "Base" Python environment. Always isolate.

### Essential Conda Commands
```bash
conda create --name ENVNAME python=3.7    # Create
conda activate ENVNAME                      # Activate
conda install XXX / pip install XXX         # Install
conda deactivate                            # Deactivate
conda env remove --name ENVNAME --all       # Clean up
```

### Freezing Your Environment (for Docker)

| Method | Command | Output |
|--------|---------|--------|
| **Pip** | `pip freeze > requirements.txt` | `pandas==2.1.0` |
| **Conda** | `conda env export --no-builds > environment.yml` | `dependencies: - python=3.9` |

> **Tip:** In Docker, prefer `requirements.txt` — it's faster. For Conda, consider Micromamba in Docker.

### Containerization (Docker)

A **Docker Image** is a lightweight, standalone package that includes:
- Code
- Runtime (Python)
- System tools & libraries
- Settings

**Docker Components:**
- **Docker Engine:** `docker run ...`
- **Docker Build:** `docker build ...` (uses BuildKit)
- **Docker Compose:** Orchestrates multiple containers
- **Docker Daemon:** `sudo systemctl start docker`

### Anatomy of a Dockerfile
```dockerfile
# 1. Base image (OS + Python)
FROM python:3.9-slim

# 2. Working directory
WORKDIR /app

# 3. Copy requirements FIRST (layer caching!)
COPY requirements.txt .

# 4. Install dependencies (at BUILD time)
RUN pip install --no-cache-dir -r requirements.txt

# 5. Copy the rest of the code
COPY . .

# 6. The command to run at RUNTIME
CMD ["python", "train.py"]
```

### Layer Caching: Why Order Matters

> [!IMPORTANT]
> Docker builds in **layers**. If you change your code, you don't want to re-download all libraries.

❌ **Slow Way:** Copy everything first → pip install
✅ **MLOps Way:** Copy `requirements.txt` first → pip install → Copy code

> Docker caches the `RUN pip install` layer. As long as `requirements.txt` doesn't change, rebuilds take **seconds**, not minutes.

### Docker Storage

| Type | Description | Use Case |
|------|-------------|----------|
| **Bind Mounts** | Maps a host folder into the container (`-v /host:/container`) | Local development |
| **Volumes** | Docker-managed storage on disk | Production & DVC caching |

- Bind mounts are **host-dependent** — paths must exist
- Volumes are **local to the VM** — limit for multi-node

### Git Best Practices
- ✅ Track: `.py`, `Dockerfile`, `requirements.txt`, `.github/workflows/`
- ❌ Ignore (`.gitignore`): `.pkl` models, `.csv` data, `venv/`, `.log`, `__pycache__/`, `.env`
- **Rule:** If a file is >50MB or changes every run, use DVC or Artifact Store, **not Git**

---

## Lecture 3 — Experiment Tracking (MLflow)

### Why Not Excel for Tracking?
When you find a "perfect" model, two weeks later:
- Which version of the **data** was used?
- What was the **learning rate**?
- Which **Git commit** produced the logic?
- Manual tracking → `manual_tracker_v2_final_FINAL.xlsx` → **Human Error!**

### MLflow: The Three Pillars

| Pillar | Purpose | Details |
|--------|---------|---------|
| **1. Tracking** | Record & query experiments | Log code, data, config, results in one central place |
| **2. Models** | Standard packaging format | "Flavors" — works on Docker, Spark, Cloud |
| **3. Registry** | Central lifecycle hub | Promote models from Staging → Production |

MLflow is an **open-source platform** to manage the full ML lifecycle, ensuring each phase is **manageable**, **traceable**, and **reproducible**.

### MLflow Key Features

1. **Experiment Organization** — Table view to compare runs, filter by metrics, sort by training time
2. **Metric Visualization** — Interactive charts, compare multiple runs, zoom into specific epochs, identify overfitting/underfitting
3. **Artifact Storage** — Store `.pkl/.pt` (weights), `.png/.html` (confusion matrix), `.yaml/.json` (configs), `.txt` (requirements)
4. **Collaboration** — Client-Server architecture, shared tracking server, real-time visibility for teams

### MLflow with PyTorch — Code Pattern
```python
import mlflow

mlflow.set_experiment("Experiment Id/Name")

with mlflow.start_run():
    # 1. Tags: For searching (e.g., "show me all CNN runs")
    mlflow.set_tag("model_type", "CNN")
    
    # 2. Params: The "Input" config
    mlflow.log_params({
        "learning_rate": 0.01,
        "batch_size": 32,
        "optimizer": "Adam"
    })
    
    # 3. Metrics: The "Output" results
    mlflow.log_metric("final_accuracy", 0.98)

    # 4. Logging the model (instead of torch.save)
    mlflow.pytorch.log_model(model, name="model")
```

### TensorBoard vs. MLflow

| Tool | Focus | Use Case |
|------|-------|----------|
| **MLflow** | End result (experiment-level) | Comparing runs, model registry, artifacts |
| **TensorBoard** | Training process (step-level) | Real-time loss curves, weight histograms, embedding projector |

**TensorBoard Code:**
```python
from torch.utils.tensorboard import SummaryWriter
writer = SummaryWriter('logs/run_1')
for epoch in range(100):
    loss = train_step()
    writer.add_scalar('Loss/train', loss, epoch)
    writer.add_image('prediction_sample', img_grid, epoch)
writer.close()
```

---

## Lecture 4 — CI/CD & GitHub Actions

### CI/CD in MLOps
- **Continuous Integration (CI):** Every `git push` triggers automated build and test
  - Ensures code can build, test, validate **without manual work**
- **Continuous Delivery / Deployment (CD):** Every successful build is ready for deployment
  - Extend automated steps to production testing and release management

> **Goal:** No model should ever reach production without passing automated tests.

### Tools for CI/CD

| Tool | Best For |
|------|----------|
| **GitHub Actions** | Built-in, Free for public repos, startups |
| **GitLab CI/CD** | Private enterprise & security |
| **Jenkins** | Legacy systems & customization |
| **Managed Cloud (AWS/GCP)** | Scaling & massive data |
| **Kubeflow Pipelines** | Kubernetes-native MLOps |

### The Pull Request Lifecycle
```
git push → PR → CI Robot checks:
  1. Code Check (Lint & Unit Tests) — follows standards?
  2. Model Validation — "Smoke Test", accuracy > threshold?
```

### YAML Pipeline Anatomy

```yaml
# .github/workflows/NAME.yml
name: ...          # (Optional) Name shown in GitHub Actions tab
on: [...]          # (Required) Trigger events
jobs:              # (Required) Map of jobs (parallel by default)
  job_id:
    runs-on: ubuntu-latest    # (Required) Runner type
    steps:                     # (Required) Sequential tasks
      - name: ...             # (Optional) Step name
        run: ...              # Execute a shell command
        uses: ...             # Use a pre-built action
        with:                 # Pass inputs to action
          param: value
```

### Key YAML Configuration

**Trigger Events (`on:`):**
- `push` — with `branches:` or `branches-ignore:`
- `pull_request`
- `workflow_dispatch` — manual trigger
- `schedule` — cron-based

> [!TIP]
> Use `push: branches: [main]` for **Deployment**, use `pull_request: branches: [main]` for **Testing**

**File Location:** `.github/workflows/your-pipeline.yml`
- Folder names `.github` and `workflows` must be **lowercase**
- Extension: `.yml` or `.yaml`

**How to activate your workflow:**
```bash
mkdir -p .github/workflows
cp your-pipeline.yml .github/workflows/
git add .
git commit -m "adding CI/CD pipeline"
git push
```

### Structure Within a Job

| Key | Required? | Purpose |
|-----|-----------|---------|
| `runs-on` | Yes | VM type (e.g., `ubuntu-latest`) |
| `steps` | Yes | Sequential tasks |
| `needs` | No | Dependencies between jobs |
| `if` | No | Conditional execution |
| `env` | No | Environment variables |

**Example: A Single Job with Linting**
```yaml
# .github/workflows/NAME.yml
name: ...
on: [...]
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

### CI/CD End-to-End Pipeline
```yaml
name: MLOps End-to-End Pipeline

on:
  push:
    branches: [ dev ]
  pull_request:
    branches: [ main ]

jobs:
  # STEP 1: Continuous Integration (The "Is the code safe?" part)
  test_and_validate:
    runs-on: ubuntu-latest
    steps:
        ...
  # STEP 2: Continuous Delivery (The "Package and Ship" part)
  build_and_deploy:
    needs: test_and_validate  # why? → Because jobs run in parallel by default!
    runs-on: ubuntu-latest
    steps:
      ...
```

---

## Lecture 5 — Advanced CI/CD Pipelines & DVC

### Automated Testing for ML — Three Levels

| Test Type | What it Checks | Example |
|-----------|---------------|---------|
| **Unit Tests** | Individual code components | `test_preprocess_nulls()` — handle NaNs? |
| **Integration Tests** | Data + Model pipeline | `test_input_shape()` — model accepts current data? |
| **Validation Tests** | Model "behavioral" performance | `assert accuracy > 0.80` — good enough to deploy? |

### Validation Testing Code
```python
def test_prediction_range():
    model = load_model("models/latest.pkl")
    prediction = model.predict(test_sample)
    assert prediction >= 0 and prediction <= 1

def test_overfitting_check():
    assert metrics['train_loss'] > 1e-5
```

### From Experiment to Production — Three Pieces
1. **The Blueprint:** Dockerfile in Git (OS, Python, dependencies)
2. **The Brain:** Model weights from MLflow (best model / production tag)
3. **The Container:** Docker builds image, downloads model, starts API

### Building the Pipeline Step by Step

**Step 1: Simple Trigger** — Blind training on every push
- ❌ Issue: No comparison, no saving results

**Step 2: Adding Observability** — Log results to MLflow via env secrets
- ❌ Issue: Blindly pushing, no comparison with production model

**Step 3: Fetching Best Model** — Use `get_best_model.py`
```python
import mlflow
client = mlflow.tracking.MlflowClient()
exp = client.get_experiment_by_name('...')
runs = client.search_runs(
    exp.experiment_id,
    order_by=['metrics.accuracy DESC'],
    max_results=1)
with open('best_model_uri.txt', 'w') as f:
    f.write(runs[0].info.artifact_uri + '/model')
```
- ❌ Issue: No Docker image built

**Step 4: Building Docker** — Login, build with `--build-arg MODEL_PATH`, push
- ❌ Issue: YAML too huge, mixed validation & deployment

**Step 5: Separation of Concerns** — Split into validate + deploy jobs
- ❌ Issue: **Jobs run in parallel by default!** Deploy starts before validate finishes

**Step 6: Final Pipeline with Dependencies**
```yaml
jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - run: pytest tests/ && python train.py --epochs 1

  deploy:
    needs: validate    # ← THE FIX: Wait for validation
    runs-on: ubuntu-latest
    steps:
      - run: python get_best_model.py
      - run: |
          docker build --build-arg MODEL_PATH=$(cat best_model_uri.txt) -t app:latest .
          docker push app:latest
```

### Dockerfile with Build Arguments (ARG)
```dockerfile
FROM python:3.10-slim
ARG MODEL_PATH                    # Passed from GitHub Action
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

### Data Version Control (DVC) — "Git for Data"

**Why Git is Broken for Data:**
- Git is designed for text line-diffs — binary files are "black boxes"
- Repo bloat: Every data change = full new copy in `.git`
- No link between data version and model version

**DevOps:** Code Version A → Binary A
**MLOps:** Code A + Data B → Model C

**How DVC Works:**
- Heavy data → external storage; lightweight pointer → Git

```bash
dvc add data/raw.csv         # Track the file
git add data/raw.csv.dvc     # Link to Git
git commit -m "Add raw data"
```

**The `.dvc` Pointer File:**
```yaml
outs:
- md5: a1b2c3d4e5f6g7h8...
  size: 1073741824
  path: raw.csv
```

> When a teammate runs `git pull`, they get the **Pointer**. When they run `dvc pull`, DVC fetches the exact file matching that MD5 hash.

### Connecting the Dots: The Full Pipeline Workflow
```
Git Push → Pull Data (DVC) → Run Tests (Pytest) → Log to MLflow → Build Container → Deployment Approval
```

---

## Lecture 6 — Conditional Execution & Midterm Tricks

### Midterm Trick 1: YAML Structure Anatomy
Common bugs:
- Missing `actions/checkout@v4` step
- Indentation errors in `uses:`, `with:`, `run:`
- Empty steps (no `run:` or `uses:`)
- Multi-line string indentation under `run: |`
- Steps must have `uses:` syntax, not `uses docker build ...`

### Midterm Trick 2: Job Dependencies & Data Sharing

> [!CAUTION]
> **Each Job is a SEPARATE VM.** They start with an empty disk. No shared memory. No shared files.

- Communication between **Steps** → `env` or local files
- Communication between **Jobs** → Artifacts (upload/download)

```yaml
# Job A: Produce data
- uses: actions/upload-artifact@v4
  with:
    name: model-id-storage
    path: model_id.txt

# Job B: Consume data
- uses: actions/download-artifact@v4
  with:
    name: model-id-storage
- run: cat model_id.txt
```

### Midterm Trick 3: Docker — Build vs. Run

| Instruction | When it Executes | Purpose |
|-------------|-----------------|---------|
| `RUN` | **Image Build** (`docker build`) | Creates a permanent layer |
| `CMD` | **Runtime** (`docker run`) | Runs when container starts |

```dockerfile
RUN date > /app/build_time.txt    # Runs ONCE during build
CMD ["cat", "/app/build_time.txt"] # Reads the frozen file at runtime
```

### Key Lessons Learned
1. Each **Job** = separate VM (empty disk, no shared memory/files)
2. Each **Step** = separate shell (local variables die when step ends)
3. Global `env` blocks are **Read-Only** at runtime

### Conditional Execution: Branch Protection
```yaml
deploy:
  needs: test
  if: github.ref == 'refs/heads/main'   # Only deploy from main
```

### Conditional Execution: Status Functions

| Function | Behavior |
|----------|----------|
| `success()` | **(Default)** Run only if no previous step/job failed |
| `failure()` | Run only if a previous step failed |
| `cancelled()` | Run only if a human clicked "Cancel" |
| `always()` | Run no matter what (e.g., shutdown GPU instances) |

> [!WARNING]
> **Critical Rule:** Every step has a **hidden default** `if: success()`. As soon as you write a custom `if:`, the default "Stop on Failure" safety is **DISABLED**. You must re-enable it manually!

```yaml
# ❌ WRONG — publish runs even if compile/test failed!
- name: publish
  if: github.ref == 'refs/heads/main'
  run: ./publish.sh

# ✅ CORRECT — re-add success() check
- name: publish
  if: success() && github.ref == 'refs/heads/main'
  run: ./publish.sh
```

### Conditional Execution: Failure Handling
```yaml
- name: Heavy Training
  run: python train.py    # Fails ❌

- name: Upload Logs on Failure
  if: failure()           # Only runs if training failed
  uses: actions/upload-artifact@v4
  with:
    name: crash-report
    path: logs/debug_info.log
```

### Selective Training (Commit Keywords)
Only run expensive GPU training when:
- Linter passes (dependency)
- Code is on `main` branch (branch protection)
- Commit message contains `[run-train]` (manual intent)

```yaml
if: >
  needs.code-check.result == 'success' &&
  github.ref_name == 'main' &&
  contains(github.event.head_commit.message, '[run-train]')
```

### GHA Secrets
- Store sensitive values like `MLFLOW_TRACKING_URI`, `DOCKER_USERNAME`, `DOCKER_PASSWORD`
- Access via `${{ secrets.SECRET_NAME }}`
- **WRONG:** `secrets.MLFLOW_URI` (no `${{ }}`)
- **CORRECT:** `${{ secrets.MLFLOW_URI }}`

---

## Lecture 7 — Kubernetes Fundamentals

### Motivation: PersonaCanvas
A multi-component AI system (Web App, AI Model, Printing, Payment, Shipping)

**Why separate components?**
- **Efficient Resources:** GPU only for AI, CPU for web app
- **Independent Scaling:** Scale web app during high demand
- **Fault Isolation:** One crash doesn't take down everything
- **Communication:** Standardized REST APIs

### What is Kubernetes (K8s)?
- Open-source platform for **container orchestration**
- Coordinates a highly available cluster of computers as a single unit
- Removes manual labor from managing 100s of containers
- K8s is the **"OS" for the modern cloud-native data center**

> "K8s" — the "8" represents the 8 letters between 'K' and 's' in "Kubernetes"

### K8s in the AI Lifecycle

| Function | Detail |
|----------|--------|
| **Deploying** | Automatic rollouts without downtime |
| **Scaling** | Distribute across GPUs/nodes, scale up/down for cost |
| **Portability** | No vendor lock-in — AWS, GCP, on-premise |

### K8s Architecture: Key Concepts

| Concept | Definition |
|---------|-----------|
| **Pod** | Smallest unit. "Logical host" for 1+ containers. Share network (IP) & storage. Each pod has a **unique IP** |
| **Node** | Worker machine (VM or Physical). Where pods live |
| **Kubelet** | Agent on each node — manages the node, communicates with control plane |
| **Service** | Stable entry point. Fixed address + load balancer (since pods die & restart with new IPs) |
| **Volume** | Persistent storage. Local or remote (S3, Google Drive) |
| **Cluster** | Set of nodes managed by a central **Control Plane** |

> **Crucial:** In 95% of cases, **1 Pod = 1 Container**. Multiple containers in one Pod only if tightly coupled.

### Control Plane (Main Node)
- **API Server:** Central entry point for all commands. Validates & processes requests
- **etcd:** The cluster's database. Maintains current info for every config, pod status, resource
- **Scheduler:** Matches Pods to best available Node (e.g., GPU availability)
- **Controller Manager:** Ensures **Current State** matches **Desired State**

### Pods, Nodes, and Network Stability
- Containers in same pod share **storage** and **localhost**
- Pods are **ephemeral** — if a pod dies, replacement gets a **different IP**
- **Services** provide a **Permanent Virtual IP** — stable "front door"

**Service Types:**
- **Internal Service:** Communication inside the cluster
- **External Service:** Exposing to the world (`http://<node-ip>:<port>`)

> **Key Takeaway:** Never talk to a Pod IP. Always talk to a **Service**!

### Cluster Architecture
- **Master Nodes** manage; **Worker Nodes** work
- **High Availability (HA):** Production uses 2-3 Master Nodes
- Master → Worker communication via **API Server**
- If etcd goes down → cluster "freezes"

### Interacting with K8s

| Approach | Method | Best For |
|----------|--------|----------|
| **Imperative** | `kubectl` commands | Testing, debugging, one-off experiments |
| **Declarative** | YAML files | Production, teamwork, version control |

> **Rule:** Use `kubectl` to **inspect**, use `YAML` to **configure**

### Local Cluster Setup
- **Minikube:** Single-node K8s cluster (Master + Worker combined)
- **kubectl:** CLI tool for K8s

```bash
minikube start          # Start the cluster
kubectl cluster-info    # Check status
kubectl get nodes       # See nodes
```

### Lecture 7 Deployment YAML (Simple Version)
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: personacanvas-frontend
spec:
  replicas: 3              # Desired State: Always keep 3 pods running
  selector:
    matchLabels:
      app: web-ui
  template:
    metadata:
      labels:
        app: web-ui        # This label links the Pod to the Service
    spec:
      containers:
      - name: streamlit-app
        image: almond/streamlit-k8s-demo:latest
        ports:
        - containerPort: 8501
```

### Lecture 7 Service YAML (Simple Version)
```yaml
apiVersion: v1
kind: Service
metadata:
  name: frontend-service
spec:
  type: NodePort           # Makes the service accessible outside the cluster
  selector:
    app: web-ui            # This MUST match the label in the Deployment
  ports:
    - protocol: TCP
      port: 80             # Port the service listens on
      targetPort: 8501     # Port the Streamlit container is running on
```

---

## Lecture 8 — K8s Deployments, Services & Hands-On

### Deployment YAML — Step-by-Step Breakdown

**Part 1: Metadata ("Who am I?")**
```yaml
# Tells K8s we are creating a Deployment using the standard apps API
apiVersion: apps/v1
kind: Deployment           # either Deployment or Service
metadata:
  name: personacanvas-frontend   # Mandatory: the unique name in your cluster
  labels:                         # Optional: keywords for organization
    owner: company-x
    app: streamlit-web
    tier: frontend
    version: 1.1
```
- `kubectl delete deployment personacanvas-frontend` — delete by name
- `kubectl get deployments -l tier=frontend` — filter by label

**Part 2: Spec — Replicas, Selector, Template**
```yaml
spec:
  replicas: 3              # ensure 3 copies are always running (desired)
  selector:                # how the Deployment finds Pods it manages
    matchLabels:
      app: streamlit-web
  template:                # The "blueprint" for the Pods
    metadata:
      labels:              # Key-value pairs to "hook" Pods to Services
        app: streamlit-web
    spec:
      containers:          # why multiple containers? → Sidecar pattern
      - name: ...          # optional name
        image: ...         # the Docker image to run
        ports: ...         # ports for your app
        resources: ...     # resources for the pod
```

**Part 3: Container Resources (the full detailed version)**
```yaml
    spec:
      containers:
      - name: streamlit-container     # optional name
        image: your-docker-username/streamlit-image:latest  # the Docker image to run
        ports:
        - containerPort: 8501         # the port your application is listening on
        resources:                    # required resources for the pod
          requests:                   # the minimum amount guaranteed to the Pod
            cpu: "250m"               # 0.25 core
            memory: "256Mi"
          limits:                     # the maximum amount the Pod is allowed to consume
            cpu: "500m"               # 0.5 core. CPU limit → Kubernetes SLOWS DOWN the CPU (not killed)
            memory: "512Mi"           # Memory limit → Kubernetes IMMEDIATELY KILLS the process (OOM)
```

### Full Deployment YAML (Combined)
```yaml
apiVersion: apps/v1
kind: Deployment           # Deployment or Service
metadata:
  name: personacanvas-frontend    # Unique name (mandatory)
  labels:                          # Optional organization keywords
    app: streamlit-web
    tier: frontend
spec:
  replicas: 3              # Desired running instances
  selector:                # How Deployment finds its Pods
    matchLabels:
      app: streamlit-web
  template:                # Pod blueprint
    metadata:
      labels:
        app: streamlit-web   # Links Pod to Service
    spec:
      containers:
      - name: streamlit-container
        image: your-username/streamlit:latest
        ports:
        - containerPort: 8501
        resources:
          requests:          # Minimum guaranteed
            cpu: "250m"      # 0.25 core
            memory: "256Mi"
          limits:            # Maximum allowed
            cpu: "500m"      # Throttled if exceeded (not killed)
            memory: "512Mi"  # KILLED if exceeded (OOM)
```

> [!IMPORTANT]
> - CPU limit exceeded → K8s **slows down** the CPU (not killed)
> - Memory limit exceeded → K8s **immediately kills** the process (OOM)

### GPU Resources
```yaml
resources:
  requests:
    memory: "4Gi"
    cpu: "2000m"
    nvidia.com/gpu: 1    # Request 1 GPU
  limits:
    memory: "8Gi"
    cpu: "4000m"
    nvidia.com/gpu: 1
```

### Service YAML Structure
```yaml
apiVersion: v1
kind: Service
metadata:
  name: streamlit-service
spec:
  type: NodePort           # Accessible outside cluster
  selector:
    app: streamlit-web     # MUST match Deployment label!
  ports:
    - name: web
      protocol: TCP
      port: 80             # INTERNAL cluster port
      targetPort: 8501     # POD/container port
      nodePort: 30085      # EXTERNAL port (range: 30000-32767)
```

**Traffic Flow:**
1. User enters `http://<Server-IP>:30085`
2. NodePort catches the request
3. Service finds Pods labeled `app: streamlit-web`
4. Forwards traffic to port 8501 inside the Pod
5. Streamlit App responds with UI

### Applying YAML Files
```bash
kubectl apply -f image-gen-deployment.yaml
kubectl apply -f streamlit-deployment.yaml
kubectl apply -f service.yaml
```

### Lifecycle of a Deployment
1. **API Server** receives your YAML, validates syntax
2. **etcd** stores the desired state (e.g., "3 replicas")
3. **Controller Manager** notices gap (0 running vs. 3 desired), creates Pod definitions
4. **Scheduler** assigns Pods to Worker Nodes based on CPU/RAM/health

### Inspecting the Cluster
```bash
kubectl get pods                          # Pod status
kubectl get deployments                   # Deployment status
kubectl get service streamlit-service     # Service info
kubectl get nodes -o wide                 # Node IPs
kubectl get deployments -l tier=frontend  # Filter by label
kubectl delete deployment NAME            # Delete deployment
```

### Scaling & Self-Healing
```bash
# Scale up
kubectl scale deployment personacanvas-backend --replicas=10

# Simulate crash (K8s auto-heals)
kubectl delete pod <pod-name>
# K8s notices 2 pods ≠ 3 desired → starts new pod in seconds

# Update image (zero-downtime)
kubectl set image deployment/personacanvas-backend generator-core=new-image:v2
```

---

## Lecture 9 — Kubeflow Pipelines & Production Monitoring

### Why GitHub Actions is NOT Enough for Heavy AI

| Problem | GHA | Kubeflow |
|---------|-----|----------|
| **Data Moving** | Moving 1TB to external runner = impossible/expensive | Runs where data lives (in-cluster) |
| **Hardware** | Standard CPUs, managing self-hosted GPUs is nightmare | Native K8s GPU scheduling |
| **Caching** | Full restart on failure | Step-level caching |
| **Hyperparameter Tuning** | Linear queue (50 jobs) | Natural parallel explosion |

> **Use GHA for CI (code integrity). Use Kubeflow for MLOps (science reproducibility).**

### GHA vs. Kubeflow Comparison

| Feature | GHA (CI/CD) | Kubeflow (ML Orchestrator) |
|---------|-------------|---------------------------|
| **Primary Goal** | Building & Testing | Managing the ML Factory |
| **Infrastructure** | General Cloud VMs | Inside the K8s Cluster |
| **Resource Logic** | Assigns a whole VM | Fine-grained Bin-Packing |
| **Data Handling** | Upload/Download artifacts | Mounts Persistent Volumes |
| **State & Failure** | Restarts from Step 1 | Step-Level Caching |
| **Trigger** | Code Push (Git events) | Data Event (file saved to cluster) |

### Three Critical Operational Gaps of Standard K8s
1. **Orchestration Gap:** K8s is "always-on"; ML needs "run-and-exit" with data dependencies
2. **Visibility Gap:** No native DAG to visualize data flow (scraper → trainer → deployer)
3. **Trigger Gap:** K8s relies on config updates; can't listen to storage events natively

### Kubeflow Platform Components
- **Notebooks:** Jupyter/VS Code as scalable Pods
- **Pipelines:** Multi-step workflows (Data → Train → Deploy), repeatable
- **Katib:** Automated hyperparameter tuning (AutoML)
- **KServe:** Advanced model serving with Scale-to-Zero

### Three Scenarios Where Kubeflow Wins

#### Scenario 1: Data Sharing
- **GHA:** Upload/download artifacts (network-bound)
- **Kubeflow:** Mount same Persistent Volume (disk-speed)

#### Scenario 2: OOM Issue (Resource Sharing)
- **GHA:** Both jobs start → OOM kills one (60GB + 8GB = 68GB > 64GB)
- **Kubeflow:** Queues Job B in PENDING until Job A releases resources

### Kubeflow Pipeline — Python SDK

**Step 1: Define Components (each becomes a separate container/Pod)**
```python
from kfp import dsl, compiler

# --- SCENARIO 1: DATA SHARING ---
# Kubeflow uses InputPath and OutputPath to automatically handle the Persistent Volume
# so Task B sees Task A's files (no upload/download artifacts like GHA!)

@dsl.component(base_image='python:3.9')
def preprocess_data(data_path: str, cleaned_data: dsl.OutputPath(str)):
    ...
    with open(cleaned_data, 'w') as f:
        f.write("/mnt/data/cleaned_sequences.bin")  # write path to shared volume

# --- SCENARIO 2: THE OOM & Resource Sharing ---
# K8s will queue 'train_model' if the 60GB RAM 'preprocess' job is already
# occupying the worker node.

@dsl.component(base_image='pytorch/pytorch:latest', packages_to_install=['mlflow'])
def train_model(cleaned_data_path: dsl.InputPath(str), epochs: int, lr: float):
    # Loading data from {cleaned_data_path}
    ...
    mlflow.log_param("learning_rate", lr)

# --- SCENARIO 3: Caching ---
# If you run this pipeline twice with the same 'data_path',
# Kubeflow will show "Taken from Cache" and skip the step.
```

**Step 2: Define the Pipeline (the DAG)**
```python
@dsl.pipeline(name="personacanvas-research-lifecycle")
def research_pipeline(data_path: str = "s3://.../raw-v1", lr: float = 0.01):
    # Task 1: Preprocess (The High-RAM job)
    prep_task = preprocess_data(data_path=data_path)
    prep_task.set_memory_limit('60Gi')
    prep_task.set_cpu_limit('4')

    # Task 2: Train (The GPU job), will wait if Task 1 takes all the RAM
    train_task = train_model(
        cleaned_data_path=prep_task.outputs['cleaned_data'],
        epochs=10, lr=lr)
    train_task.set_gpu_limit(1)       # nvidia.com/gpu
    train_task.set_memory_limit('8Gi')

    # SCENARIO 3: Caching is enabled by default.
    # If train_task fails, re-running the pipeline will SKIP prep_task.

# --- COMPILATION: Converts Python → YAML for Kubeflow to execute ---
if __name__ == "__main__":
    compiler.Compiler().compile(research_pipeline, 'research_pipeline.yaml')
```

### Production Monitoring

> *"If we can measure, then we can compare. And if we can compare, only then can we improve."*

### Three Dimensions of Monitoring

| Dimension | Focus | Metrics |
|-----------|-------|---------|
| **1. Service** | Infrastructure | Prediction latency, performance cliffs, cost |
| **2. Data** | Input/Output | Quality checks, data drift, concept drift |
| **3. Model** | Logic | Real-time actuals, delayed actuals, proxy measures |

### Types of Drift

| Drift Type | Definition | Example |
|------------|-----------|---------|
| **Data Drift (Prompt Drift)** | Input distribution shifts from training data | Simple prompts → complex 50+ keyword prompts |
| **Concept Drift** | Relationship between inputs and outputs changes | Model trained for "art" but users expect "photos" |

### The "Silent Failure" Scenario
- Infrastructure looks perfect (200 OK, stable GPU, low queue)
- But users complain about degraded output quality
- Root causes: Prompt Drift (input) + Concept Drift (output)

### Closed-Loop System to Fix Silent Failures
1. **Automated Evaluation:** Sidecar container computes CLIP scores. Alert if similarity < 0.25
2. **Human-in-the-Loop (HITL):** Low-confidence outputs → labeling UI → 👍/👎 → new Gold Standard dataset
3. **Triggered Retraining:** 1000 new examples → Kubeflow auto-triggers fine-tuning pipeline

---

## Assignment Deep Dive — Exam-Critical Knowledge

---

### Assignment 1: The Reproducibility Problem

**Objective:** Experience firsthand why MLOps exists — try to run someone else's ML code.

**Key Exam Questions:**
- *How many commands did I have to run before it worked?* → Often many `pip install` commands needed
- *What libraries were missing? Did version mismatches cause errors?* → Yes, PyTorch version mismatch required upgrade
- *Did the model produce the same result?* → **No!** Random seeds were not fixed → different accuracy each run
- *If this had to run on a server at 3:00 AM, would it survive?* → **No!** Network timeouts, missing dependencies

**Exam-Testable Lessons:**
1. **Dependency Hell** — Different library versions (scikit-learn 1.2 vs 0.24) break everything
2. **Random Seeds** — Without fixing seeds (`torch.manual_seed()`, `random_state=42`), results are non-reproducible
3. **Hardcoded Paths** — `/home/mohamed/data` won't exist on another machine
4. **No `requirements.txt`** — Makes it impossible to recreate the environment
5. **This is WHY we need MLOps** — Docker, Conda, DVC solve all of these

---

### Assignment 2: Conda Environment + Dockerfile

**Objective:** Make the Assignment 1 script fully reproducible.

**Key Commands (know these for the exam!):**
```bash
# Part 1: Conda Environment
conda create --name env_rl_project python=3.10
conda activate env_rl_project
pip install -r requirements.txt
pip freeze > requirements.txt           # Export pip dependencies
conda env export > environment.yml       # Export full conda environment

# Part 2: Docker
docker build -t myimage .
```

**The Correct Dockerfile (with layer caching):**
```dockerfile
FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "train.py"]
```

**Exam-Testable Lessons:**
1. **Layer Caching Order:** `COPY requirements.txt` → `RUN pip install` → `COPY . .` (code changes don't re-download libraries)
2. **`FROM python:3.10-slim`** — Use slim images (smaller, faster)
3. **`WORKDIR /app`** — Sets the working directory inside the container
4. **`RUN` = Build time, `CMD` = Runtime** — `pip install` runs once during build, `python train.py` runs each time container starts
5. **`--no-cache-dir`** — Prevents pip from caching downloads (smaller image)

---

### Assignment 3: MLflow Experiment Tracking

**Objective:** Instrument a training script with MLflow to track, compare, and version experiments.

**Complete MLflow Training Script (exam-critical code):**
```python
import mlflow
import mlflow.pytorch

# Setup tracking
mlflow.set_tracking_uri("sqlite:///mlflow.db")     # or "http://localhost:5000"
mlflow.set_experiment("Assignment3_YourName")

def train_classifier(run_name, epochs, batch_size, lr):
    with mlflow.start_run(run_name=run_name):
        
        # 1. Log Parameters (the "Input" config)
        mlflow.log_param("epochs", epochs)
        mlflow.log_param("batch_size", batch_size)
        mlflow.log_param("learning_rate", lr)
        
        # 2. Set Tags (for searching/filtering)
        mlflow.set_tag("student_id", "YOUR_ID")
        mlflow.set_tag("model_type", "CNN_Classifier")
        
        # 3. Training Loop with Live Logging
        for epoch in range(epochs):
            # ... training code ...
            
            # Log metrics at end of every epoch (generates learning curves)
            mlflow.log_metric("loss", epoch_loss, step=epoch)
            mlflow.log_metric("accuracy", epoch_acc, step=epoch)
        
        # 4. Save Model Artifact
        mlflow.pytorch.log_model(model, "cnn_model")

# Run 5 experiments with different hyperparameters
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

**Launch MLflow UI:** `mlflow ui --port 5000` → Open `http://localhost:5000`

**Exam-Testable Lessons:**
1. **`mlflow.set_experiment()`** — Groups runs under a named experiment
2. **`with mlflow.start_run():`** — All logging MUST be inside this context manager
3. **`log_param`** → hyperparameters (input), **`log_metric`** → results (output), **`set_tag`** → labels (searchable)
4. **`step=epoch`** in `log_metric` → generates learning curve graphs
5. **`mlflow.pytorch.log_model()`** → saves model weights + environment details as artifacts
6. **Analysis skills:** Which run converges fastest? Does high LR cause instability? Evidence of overfitting?

---

### Assignment 4: GitHub Actions YAML Debugging

**Objective:** Fix a broken GitHub Actions YAML and add features.

**The Buggy YAML (from the professor):**
```yaml
# .github/workflows/ml-pipeline.yml
name: ML Model CI
on:
    push:
        branches: main
    pull_request:
jobs:
    validate-and-test:
        runs-on: ubuntu-latest
        steps:                
            - name: Set up Python
                uses: actions/setup-python@v5    # Bug: indentation
                with:
                    python-version: '3.10'
            - name: Install Dependencies
                run: pip install -r requirements.txt
            - name: Linter Check
                                                  # Bug: empty step!
            - name: Model Dry Test
                run: |
                python -c "import torch; print('...')"   # Bug: indentation
```

**All Bugs Found:**
1. **Missing `actions/checkout@v4`** — Runner has no code!
2. **Indentation errors** — `uses:`, `with:`, `run:` indented too deep
3. **Empty Linter Step** — No `run:` or `uses:` command
4. **Multi-line indentation** — `python -c` must be indented under `run: |`

**The Fixed + Enhanced YAML:**
```yaml
name: ML Model CI
on:
  push:
    branches-ignore:        # Task: Run on all branches EXCEPT main
      - main
  pull_request:

jobs:
  validate-and-test:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout Code               # Fix 1: Added checkout
        uses: actions/checkout@v4

      - name: Set up Python               # Fix 2: Fixed indentation
        uses: actions/setup-python@v5
        with:
          python-version: '3.10'

      - name: Install Dependencies
        run: |
          if [ -f requirements.txt ]; then
            pip install -r requirements.txt
          else
            echo "requirements.txt not found, skipping install."
          fi

      - name: Linter Check                # Fix 3: Added linter command
        run: |
          pip install flake8
          flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics

      - name: Model Dry Test              # Fix 4: Fixed indentation
        run: |
          python -c "import torch; print('Model environment ready!')"

      - name: Upload README Artifact       # Task: Upload artifact
        uses: actions/upload-artifact@v4
        with:
          name: project-doc
          path: README.md
```

**Exam-Testable Lessons:**
1. **`branches-ignore: - main`** → Run on all branches EXCEPT main
2. **`actions/checkout@v4`** must ALWAYS be first step
3. **Empty steps** will crash the workflow — every `- name:` needs `run:` or `uses:`
4. **Multi-line `run: |`** — content must be indented further than the `run:` key
5. **Grading Rubric:** Syntax Fixes (30), Workflow Logic (30), Artifact (20), Evidence (20)

---

### Assignment 5: Multi-Job Validation & Deployment Pipeline

**Objective:** Build a 2-job pipeline: Validate (train + log) → Deploy (threshold check + Docker).

**The `train.py` Script (writes `model_info.txt`):**
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

    # KEY: Write run ID AND accuracy to file for the deploy job
    with open("model_info.txt", "w") as f:
        f.write(f"{run.info.run_id}\n")
        f.write(f"{accuracy:.4f}\n")
```

**The `check_threshold.py` Script:**
```python
import sys

THRESHOLD = 0.85

with open("model_info.txt") as f:
    lines = f.read().strip().splitlines()

run_id   = lines[0].strip()
accuracy = float(lines[1].strip())

if accuracy < THRESHOLD:
    print(f"❌ FAILED — accuracy {accuracy:.4f} is below {THRESHOLD}.")
    sys.exit(1)    # EXIT CODE 1 = FAILS THE PIPELINE

print(f"✅ PASSED — accuracy {accuracy:.4f} meets the threshold.")
```

**The Dockerfile with ARG:**
```dockerfile
FROM python:3.10-slim
ARG RUN_ID                       # Build-time argument from GHA
ENV RUN_ID=${RUN_ID}             # Convert to runtime env var

RUN pip install --no-cache-dir mlflow scikit-learn
WORKDIR /app

RUN echo "Downloading model for Run ID: ${RUN_ID}" && \
    mkdir -p /app/model && \
    echo "${RUN_ID}" > /app/model/run_id.txt

CMD ["python", "-c", \
     "import os; print(f'Model container running. Run ID: {os.environ[\"RUN_ID\"]}')"]
```

**The Complete Pipeline YAML:**
```yaml
name: ML Validation and Deployment Pipeline
on:
  push:
    branches: [main]

jobs:
  validate:
    name: Train & Validate Model
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
      - name: Upload model_info artifact
        uses: actions/upload-artifact@v4
        with:
          name: model-artifacts
          path: model_info.txt

  deploy:
    name: Check Threshold & Deploy
    runs-on: ubuntu-latest
    needs: validate                    # Wait for validation!
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.10"
      - run: pip install -r requirements.txt
      - name: Download model_info artifact
        uses: actions/download-artifact@v4
        with:
          name: model-artifacts
          path: .
      - name: Check accuracy threshold
        run: python check_threshold.py     # Fails pipeline if < 0.85
      - name: Mock Docker build
        run: |
          RUN_ID=$(head -1 model_info.txt)
          echo "Building Docker image for Run ID: ${RUN_ID}"
          docker build --build-arg RUN_ID="${RUN_ID}" -t ml-model:${RUN_ID} .
```

**Exam-Testable Lessons:**
1. **`needs: validate`** — Deploy job MUST wait for validation
2. **Artifact handover** — `upload-artifact` in Job 1, `download-artifact` in Job 2 (different VMs!)
3. **`sys.exit(1)`** — Non-zero exit code FAILS the pipeline step
4. **`ARG` vs `ENV`** in Dockerfile: `ARG` = build-time only, `ENV` = available at runtime too
5. **`--build-arg RUN_ID=...`** — Pass values from GHA to Docker during build
6. **Grading:** Pipeline Architecture (30), Data Handover (30), Threshold Logic (20), Security/Docker (20)

---

### Assignment 6: Conditional Execution & Gatekeeper Logic

**Objective:** Add "Gatekeeper" logic so expensive training only runs under strict conditions.

**The Three Conditions (ALL must be true):**
1. `needs.code-check.result == 'success'` — Linter job passed
2. `github.ref_name == 'main'` — On main branch only
3. `contains(github.event.head_commit.message, '[run-train]')` — Manual intent keyword

**The Complete Gatekeeper Pipeline:**
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
      - name: Run linter
        run: |
          echo "Running lint checks..."
          echo "No issues found"

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
      - name: Create error logs (on failure)
        if: failure()                      # Only if training failed
        run: echo "Training failed logs" > error_logs.txt
      - name: Upload logs
        if: failure()                      # Only if training failed
        uses: actions/upload-artifact@v4
        with:
          name: error_logs
          path: error_logs.txt
      - name: Cleanup resources
        if: always()                       # ALWAYS runs (success or failure)
        run: echo "Cleaning up .."

  training-status:
    name: Training Status Report
    runs-on: ubuntu-latest
    needs: model-training
    if: always()                           # Run even if training was skipped
    steps:
      - name: Show final status
        run: |
          if [ "${{ needs.model-training.result }}" = "success" ]; then
            echo "STATUS: SUCCESS"
          elif [ "${{ needs.model-training.result }}" = "failure" ]; then
            echo "STATUS: FAILURE"
          else
            echo "STATUS: SKIPPED"
          fi
```

**Exam-Testable Lessons:**
1. **`if: failure()`** — Step only runs when a previous step failed (upload crash logs)
2. **`if: always()`** — Step runs no matter what (cleanup GPU, print status)
3. **`contains(github.event.head_commit.message, '[run-train]')`** — Commit keyword gating
4. **Training-status job with `if: always()`** — Reports whether training was SUCCESS/FAILURE/SKIPPED
5. **`${{ needs.model-training.result }}`** — Access the result of a dependent job

---

### Assignment 7: 3-Job DAG Pipeline (Audit → Build → Promote)
![[Pasted image 20260603020637.png]]

**Objective:** Build a "High-Integrity Promotion Pipeline" for a medical AI company with three stages.

**The DAG Architecture:**
```text
[Integrity Audit] ──(success)──> [Forensic Build] ──(success)──> [Production Promotion]
 (Data + Code Audit)            (Docker Build & Log)            (Tag v* Only - Deploy)
```

**Solved Code Implementation:**

#### 1. `check_data.py` (Integrity Audit Logic)
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

#### 2. `Dockerfile` (Multi-stage Forensic Build)
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

#### 3. `.github/workflows/pipeline.yaml` (The 3-Job DAG)
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

**Exam-Testable Lessons:**
1. **Git Tag Trigger:** `on: push: tags: ['v*']` or check `startsWith(github.ref, 'refs/tags/')`
2. **DVC in CI:** Must `checkout` code first (to get `.dvc` files), then `dvc pull`
3. **Multi-stage gating:** Each job adds stricter conditions
4. **Failure artifacts:** Upload build logs as artifacts when `if: failure()` for debugging without re-running GPU

---

### Assignment 8: Kubernetes Frontend Deployment

**Objective:** Deploy PersonaCanvas frontend on local K8s using Minikube.

**Solved Code Implementation:**

#### 1. `deployment.yaml` (Frontend Deployment)
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

#### 2. `service.yaml` (NodePort Service)
```yaml
apiVersion: v1
kind: Service
metadata:
  name: frontend-service
spec:
  type: NodePort
  selector:
    app: streamlit-web # Must match deployment spec matchLabels
  ports:
    - name: web
      protocol: TCP
      port: 80         # Internal cluster port
      targetPort: 8501 # Container Port Streamlit is running on
      nodePort: 30085  # External access port (30000-32767)
```

**Step-by-Step Deployment Verification Commands:**
```bash
# 1. Start cluster
minikube start                                      

# 2. Deploy the 3 replicas of the frontend pod
kubectl apply -f deployment.yaml                    

# 3. Create the NodePort service to expose the deployment externally
kubectl apply -f service.yaml                       

# 4. Verify all 3 instances are in the "Running" state
kubectl get pods                                    

# 5. Open the exposed frontend app directly in your browser
minikube service frontend-service                   

# 6. Test Self-Healing: Delete a pod manually and watch replica set recreate it
kubectl delete pod <pod-name-from-step-4>
kubectl get pods -w # Observe container termination and auto-recreation
```

**Exam-Testable Lessons:**
1. **`replicas: 3`** — K8s maintains exactly 3 instances
2. **Self-healing:** Delete a pod → Controller Manager detects mismatch → creates new pod automatically
3. **`minikube service`** — Opens the NodePort service in your browser
4. **Keep terminal open** while minikube service is running

---

### Assignment 9: Kubernetes Frontend + Backend (Multi-Service)

**Objective:** Deploy BOTH frontend AND backend with inter-service communication.

**Architecture:**
```
[User] → NodePort:30085 → [Frontend Service] → [Frontend Pods (×3)]
                                                      ↓ (HTTP call)
                              [Backend Service] → [Backend Pods (×2)]
                                 (ClusterIP)
```

**Key Differences from Assignment 8:**
- **Two Deployment YAMLs:** Web app (3 replicas) + AI app (2 replicas) with different resources
- **Two Service YAMLs:**
  - `service_web.yaml` → `type: NodePort` (external access)
  - `service_ai.yaml` → `type: ClusterIP` (internal only, default)
- **Inter-service communication:** Frontend calls backend via `http://ai-service:<port>`

**Exam-Testable Lessons:**
1. **`NodePort`** = external access (browser), **`ClusterIP`** = internal only (pod-to-pod)
2. **Service DNS:** Pods call other services by name: `http://backend-service:5000`
3. **Different resources per deployment:** Frontend = low CPU/RAM, Backend = high RAM + GPU
4. **Labels must match:** `selector.matchLabels` in Deployment must match `selector` in Service

---

### Assignment Quick-Reference Summary

| # | Topic | Key Concepts to Know for Exam |
|---|-------|-------------------------------|
| **1** | Reproducibility | Dependency hell, random seeds, hardcoded paths, no requirements.txt |
| **2** | Conda + Docker | `pip freeze`, `conda env export`, Dockerfile layer caching order |
| **3** | MLflow | `set_experiment`, `start_run`, `log_param/metric`, `log_model`, 5 runs comparison |
| **4** | GHA Debugging | Missing checkout, indentation, empty steps, `branches-ignore`, upload artifact |
| **5** | Multi-Job Pipeline | `needs:`, artifact upload/download, `check_threshold.py`, `sys.exit(1)`, Docker `ARG` |
| **6** | Gatekeeper Logic | 3 conditions (linter + branch + keyword), `failure()`, `always()`, status report |
| **7** | DAG Pipeline | 3-job DAG, Git tag triggers, DVC in CI, `check_data.py`, failure artifact upload |
| **8** | K8s Frontend | `minikube start`, deployment (3 replicas), service (NodePort), self-healing |
| **9** | K8s Multi-Service | Two deployments, NodePort vs ClusterIP, inter-service DNS, different resources |

---

### Bonus: Assignment 9 — Buggy YAML Exercise (Find All Errors!)

The professor may give you a YAML file full of bugs to fix. Here's an example from Assignment 9:

**❌ Buggy YAML:**
```yaml
name: test
on:
  push:
jobs:
  lint:
    runs-on: ubuntu-latest
  steps:                               # Bug 1: 'steps' should be indented under 'lint'
    - name: checkout code
      uses: actions/checkout@v4
    - name: setup python 
      uses: actions/setup-python@v3
      with:
        python: version:"3.10"         # Bug 2: should be 'python-version: "3.10"'
    - name: Install dependencies
      run: pip install -r requirements.txt
    - name: lint
      run: flake src/                  # Bug 3: should be 'flake8 src/'
  train:
    needs: lint
    runs-on: ubuntu-latest
    steps:
      - name: checkout code
        uses: actions/checkout@v4
        
        uses: actions/setup-python@v3  # Bug 4: missing '- name:' for new step
        with:
          python: version:"3.10"       # Bug 5: same python-version bug
      - name: install dependencies
        runs: pip install -r requirement.txt  # Bug 6: 'runs' should be 'run', 'requirement' → 'requirements'
      - name: train model
        run: python train.py
      - name: save model to artifact
        uses: actions/upload-artifact@v3
        with:
          name: model
          path: model.pkl
  deploy:
    needs: train
    runs-on: ubuntu-latest
    if: success() && github.ref == 'refs/heads/main'
    steps:
      - name: checkout code
        uses: actions/checkout@v3
      - name: download artifact
        uses: actions/download-artifact@v3
        with: model                    # Bug 7: should be 'with:\n  name: model'
      - name: build docker image
        run: docker build -t docker myapp:latest .  # Bug 8: 'docker' is extra → 'docker build -t myapp:latest .'
      - name: login docker hub
        run: echo "${{ secrets.DOCKER_PASSWORD }}" | docker login -u "${{ secrets.DOCKER_USERNAME }}" --password-stdin
      - run: docker tag myapp:latest myrepo/app:latest
      - run: docker push myrepo/myapp:latest  # Bug 9: tag says 'app' but push says 'myapp' → mismatch
```

**All 9 Bugs:**
1. `steps:` indented at wrong level (should be under `lint:` job)
2. `python: version:"3.10"` → should be `python-version: "3.10"`
3. `flake src/` → should be `flake8 src/`
4. Missing `- name:` before second `uses:` in train job (two `uses:` under one step)
5. Same `python: version:` syntax error repeated
6. `runs:` → should be `run:` (singular), `requirement.txt` → `requirements.txt`
7. `with: model` → should be `with:\n  name: model`
8. `docker build -t docker myapp:latest .` → extra word `docker` in the tag
9. Tag mismatch: `myrepo/app:latest` vs `myrepo/myapp:latest`

---

## The Complete MLOps Lifecycle

```
┌─────────────────────────────────────────────────────┐
│ 1. FOUNDATIONS                                       │
│    DevOps · Git · Conda                              │
├─────────────────────────────────────────────────────┤
│ 2. REPRODUCIBILITY                                   │
│    Docker · DVC · MLflow                             │
├─────────────────────────────────────────────────────┤
│ 3. AUTOMATION                                        │
│    CI/CD · GitHub Actions                            │
├─────────────────────────────────────────────────────┤
│ 4. ORCHESTRATION                                     │
│    Kubernetes · Nodes · Pods · Cluster               │
├─────────────────────────────────────────────────────┤
│ 5. NETWORKING                                        │
│    Services · Deployments                            │
├─────────────────────────────────────────────────────┤
│ 6. OPERATIONS & FEEDBACK LOOPS                       │
│    Kubeflow Pipelines · Monitoring · Logging         │
└─────────────────────────────────────────────────────┘
```

> *"You are no longer just building models. You are engineering the systems that bring science to life."*

### The Two Perspectives
- **Software Architect (CI/CD via GHA):** "Is the code tested? Does the Docker Image build correctly?"
- **Research Scientist (MLOps via Kubeflow):** "Is the model accurate? Can we train on local GPUs? Is it reproducible?"

**The Bottom Line:** GHA builds the **Engine** (CI), and Kubeflow **Drives** the experiment (MLOps).
