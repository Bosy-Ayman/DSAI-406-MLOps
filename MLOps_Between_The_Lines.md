# 🧠 DSAI-406 MLOps — Between the Lines

> **Purpose:** Things your professor will ask that are NOT in the slides, but are logically connected to the course content. The "tricky quiz" material.

---

## Table of Contents

1. [The Gaps Between Lectures](#the-gaps-between-lectures)
2. [Git & Security — What the Lectures Don't Say](#git--security)
3. [Docker — Hidden Knowledge](#docker--hidden-knowledge)
4. [CI/CD — The Edge Cases](#cicd--the-edge-cases)
5. [MLflow — Beyond the Basics](#mlflow--beyond-the-basics)
6. [DVC — The Full Picture](#dvc--the-full-picture)
7. [Kubernetes — What They Don't Tell You](#kubernetes--what-they-dont-tell-you)
8. [Kubeflow & Monitoring — Deeper Concepts](#kubeflow--monitoring--deeper-concepts)
9. [Tricky Quiz Questions (50+ Questions)](#tricky-quiz-questions)

---

## The Gaps Between Lectures

The course follows a clear narrative, but gaps exist between each transition:

```
Lec 1 (Why MLOps?) ──── GAP: What exactly breaks? ────→ Lec 2 (Reproducibility)
Lec 2 (Docker/Conda) ── GAP: Env is fixed, but which model won? ─→ Lec 3 (MLflow)
Lec 3 (MLflow) ──────── GAP: I track locally, but how to automate? ─→ Lec 4 (CI/CD)
Lec 4 (Basic CI/CD) ─── GAP: Pipeline works but is wasteful ────→ Lec 5 (Advanced + DVC)
Lec 5 (Full Pipeline) ─ GAP: How to stop wasting GPU money? ────→ Lec 6 (Conditionals)
Lec 6 (Conditionals) ── GAP: Code deploys, but how to scale? ───→ Lec 7 (K8s Theory)
Lec 7 (K8s Theory) ──── GAP: I know theory, how to use it? ─────→ Lec 8 (K8s Hands-On)
Lec 8 (K8s Hands-On) ── GAP: K8s runs services, not ML pipelines ─→ Lec 9 (Kubeflow)
```

---

## Git & Security

### 🔑 The Password Question (Professor's Favorite!)

> **Q: "If you have a password hardcoded in your code, will GitHub stop you from pushing it?"**

**Answer: NO!** Git and GitHub will **happily push your password** to the repository. Git does not check file contents — it just tracks changes.

**However**, GitHub has optional features:
- **GitHub Secret Scanning** — scans for known patterns (AWS keys, API tokens) and sends a warning **AFTER** the push. It does NOT block the push.
- **Push Protection** (newer feature) — can block pushes containing detected secrets, but it's opt-in and only works for certain patterns.

**The MLOps lesson:** This is why we use:
- `${{ secrets.NAME }}` in GitHub Actions (encrypted, never exposed in logs)
- `.env` files (local only, added to `.gitignore`)
- Never hardcode credentials in source code

### What Happens If You Accidentally Commit a Secret?

1. The secret is now in **Git history forever** — even if you delete the file in the next commit
2. Anyone who cloned the repo already has it
3. **To truly remove it:** Use `git filter-branch` or the BFG Repo Cleaner tool to rewrite history
4. **Best practice:** Rotate the credential immediately (change the password/key)

### `.gitignore` — What It Does and Doesn't Do

| What `.gitignore` Does | What It Doesn't Do |
|---|---|
| Prevents **untracked** files from being added | Does NOT remove already-tracked files |
| Works on patterns (e.g., `*.pkl`, `data/`) | Does NOT encrypt or protect files |
| Local to the repo | Does NOT affect files already committed |

> **Tricky Q:** *"I added `secrets.txt` to `.gitignore` AFTER I already committed it. Is it safe?"*
> **A:** No! The file is still in Git history. You must run `git rm --cached secrets.txt` AND rewrite history.

### `.env` Files — The Security Pattern

```bash
# .env (NEVER committed to Git!)
MLFLOW_TRACKING_URI=http://mlflow-server:5000
DOCKER_USERNAME=myuser
DOCKER_PASSWORD=SuperSecret123
AWS_ACCESS_KEY=AKIAIOSFODNN7EXAMPLE
```

```bash
# .gitignore
.env           # Always ignore .env files!
```

In code: `os.getenv("MLFLOW_TRACKING_URI")` reads from environment, not hardcoded.

---

## Docker — Hidden Knowledge

### `ENTRYPOINT` vs `CMD` — The Full Picture

The lectures only mention `CMD`, but the professor might ask about `ENTRYPOINT`:

| Instruction | Purpose | Overridable? |
|---|---|---|
| `CMD` | Default command when container starts | Yes — `docker run image <new_command>` replaces it |
| `ENTRYPOINT` | The "main program" of the container | No — arguments are appended, not replaced |

```dockerfile
# CMD example — can be overridden
CMD ["python", "train.py"]
# docker run myimage             → runs "python train.py"
# docker run myimage bash        → runs "bash" (CMD replaced!)

# ENTRYPOINT example — cannot be overridden
ENTRYPOINT ["python"]
CMD ["train.py"]
# docker run myimage             → runs "python train.py"
# docker run myimage serve.py    → runs "python serve.py" (only CMD replaced)
```

### `EXPOSE` — A Common Misconception

```dockerfile
EXPOSE 8501
```

> **Tricky Q:** *"Does `EXPOSE` in a Dockerfile actually publish the port?"*
> **A:** **No!** `EXPOSE` is just **documentation** — it tells other developers which port the app uses. To actually publish: `docker run -p 8501:8501 myimage`

### What Happens to Data When a Container Stops?

> **A:** Everything inside the container is **LOST** unless you use:
> - **Volumes** (`docker run -v myvolume:/data`) — Docker-managed persistent storage
> - **Bind Mounts** (`docker run -v /host/path:/container/path`) — Host directory mapped in
> - **`COPY` during build** — Baked into the image layer permanently

This is why MLflow artifacts, model weights, and training data need persistent storage.

### Docker Image vs Container

| Concept | Analogy | Details |
|---|---|---|
| **Image** | A recipe / blueprint | Read-only template built from Dockerfile |
| **Container** | A running dish / instance | A live, writable instance of an image |

You can run **many containers** from **one image**. Each container is isolated.

### Docker Registry vs Docker Hub

- **Docker Registry** = Any server that stores Docker images (generic term)
- **Docker Hub** = Docker's public registry (like GitHub for images)
- **Other registries:** AWS ECR, Google GCR, GitHub Container Registry
- `docker push` sends to a registry; `docker pull` downloads from one

### The `docker build` Context

> **Tricky Q:** *"Why does `docker build -t myimage .` have a dot at the end?"*
> **A:** The `.` is the **build context** — Docker sends all files in the current directory to the Docker daemon. This is why `.dockerignore` matters (like `.gitignore` but for Docker).

### Multi-Stage Builds (Mentioned in Assignment 7)

```dockerfile
# Stage 1: Build
FROM python:3.10 AS builder
COPY requirements.txt .
RUN pip install -r requirements.txt

# Stage 2: Production (smaller image!)
FROM python:3.10-slim
COPY --from=builder /usr/local/lib/python3.10/site-packages /usr/local/lib/python3.10/site-packages
COPY . /app
CMD ["python", "app.py"]
```

Result: Final image is much smaller because build tools aren't included.

---

## CI/CD — The Edge Cases

### What is `workflow_dispatch`?

```yaml
on:
  workflow_dispatch:    # Manual trigger button in GitHub Actions UI
```

This adds a "Run workflow" button in the Actions tab. Used for:
- Manual deployments
- On-demand training runs
- Emergency rollbacks

### Self-Hosted Runners vs GitHub Runners

| Feature | GitHub-Hosted | Self-Hosted |
|---|---|---|
| **Hardware** | Standard CPU VMs | Your own machines (GPU!) |
| **Cost** | Free (public repos) | Your electricity/hardware |
| **Setup** | Zero | Must install runner agent |
| **Security** | Isolated (fresh VM each time) | Persistent (shared state risk) |
| **Use Case** | CI/CD, testing | GPU training, large data |

```yaml
runs-on: ubuntu-latest              # GitHub-hosted
runs-on: [self-hosted, gpu-node]    # Self-hosted with GPU label
```

### Matrix Strategy — Running Tests in Parallel

```yaml
strategy:
  matrix:
    python-version: ['3.9', '3.10', '3.11']
    os: [ubuntu-latest, macos-latest]
```

This creates **6 parallel jobs** (3 Python versions × 2 OS). Used for testing compatibility.

### What Happens If Two Pushes Trigger Simultaneously?

By default, both workflows run in parallel. To prevent this:
```yaml
concurrency:
  group: ${{ github.ref }}
  cancel-in-progress: true    # Cancel the older run
```

### Environment Variables Scope

| Scope | Visibility | Example |
|---|---|---|
| **Workflow-level `env:`** | All jobs and steps | `env: PYTHON: 3.10` |
| **Job-level `env:`** | All steps in that job | Under `jobs: build: env:` |
| **Step-level `env:`** | Only that step | Under a step's `env:` |

> **Tricky Q:** *"Can a step modify a workflow-level env variable?"*
> **A:** **No!** Workflow and job `env` blocks are **read-only at runtime**. To pass data between steps, write to `$GITHUB_ENV` or use files.

### Passing Data Between Steps (Same Job)

```yaml
# Method 1: GITHUB_ENV (persists across steps)
- run: echo "MODEL_ID=run_123" >> $GITHUB_ENV
- run: echo $MODEL_ID    # Works!

# Method 2: GITHUB_OUTPUT (for job outputs)
- id: get-id
  run: echo "model_id=run_123" >> $GITHUB_OUTPUT
- run: echo ${{ steps.get-id.outputs.model_id }}
```

### GitHub Actions Billing & Limits

- **Public repos:** Free unlimited minutes
- **Private repos:** Limited free minutes per month
- **Job timeout:** 6 hours max (default)
- **Workflow timeout:** 35 days
- **Artifact storage:** 500 MB free, deleted after 90 days

---

## MLflow — Beyond the Basics

### `mlflow.autolog()` — Automatic Logging

```python
import mlflow
mlflow.autolog()    # Automatically logs params, metrics, and model!

model.fit(X_train, y_train)  # MLflow captures everything
```

Works with: PyTorch, TensorFlow, Scikit-learn, XGBoost, LightGBM.
No need to manually call `log_param`, `log_metric`, `log_model`.

### Model Registry Lifecycle

```
None → Staging → Production → Archived
```

| Stage | Meaning |
|---|---|
| **None** | Just logged, not registered |
| **Staging** | Being tested/validated |
| **Production** | Actively serving predictions |
| **Archived** | Retired, kept for audit |

```python
# Register a model
mlflow.register_model("runs:/abc123/model", "MyModel")

# Transition stages
client.transition_model_version_stage("MyModel", version=1, stage="Production")
```

### MLflow Storage — Where Does Data Go?

| Component | Default Storage | Production Storage |
|---|---|---|
| **Tracking data** (params, metrics) | `./mlruns/` directory | SQLite/PostgreSQL database |
| **Artifacts** (models, plots) | `./mlruns/` directory | S3, GCS, Azure Blob |
| **Tracking URI** | `file:./mlruns` | `http://mlflow-server:5000` |

```python
mlflow.set_tracking_uri("sqlite:///mlflow.db")      # Local database
mlflow.set_tracking_uri("http://mlflow-server:5000") # Remote server
```

### The `MLmodel` File — Model Packaging

When you `log_model`, MLflow creates:
```
model/
├── MLmodel            # Metadata: flavor, signature, env
├── conda.yaml         # Conda environment to reproduce
├── requirements.txt   # Pip dependencies
├── model.pkl          # The actual weights (or model.pt for PyTorch)
```

The `MLmodel` file describes **how to load** the model regardless of framework.

### Model Flavors

| Flavor | Module | Use Case |
|---|---|---|
| `mlflow.sklearn` | Scikit-learn | Traditional ML |
| `mlflow.pytorch` | PyTorch | Deep learning |
| `mlflow.tensorflow` | TensorFlow/Keras | Deep learning |
| `mlflow.pyfunc` | Generic Python | Custom models |

---

## DVC — The Full Picture

### DVC Remote Storage

DVC doesn't store data in Git — but where does it go?

```bash
# Configure remote storage
dvc remote add -d myremote s3://my-bucket/dvc-storage     # AWS S3
dvc remote add -d myremote gdrive://folder-id              # Google Drive
dvc remote add -d myremote /mnt/shared/dvc-cache           # Local/NFS
```

### The Full DVC Workflow

```bash
# Track data
dvc add data/training.csv          # Creates data/training.csv.dvc
git add data/training.csv.dvc data/.gitignore
git commit -m "Track training data"

# Push data to remote
dvc push                           # Uploads actual file to S3/GDrive

# Teammate pulls data
git pull                           # Gets the .dvc pointer file
dvc pull                           # Downloads actual data matching the hash
```

### DVC in CI/CD Pipeline

```yaml
steps:
  - uses: actions/checkout@v4      # Step 1: Get code + .dvc pointers
  - run: pip install dvc[s3]       # Step 2: Install DVC with S3 support
  - run: dvc pull                  # Step 3: Download actual data
  - run: python train.py           # Step 4: Train with real data
```

> **Tricky Q:** *"Why must `checkout` come before `dvc pull`?"*
> **A:** Because `dvc pull` needs the `.dvc` pointer files that are tracked in Git. Without checkout, there are no `.dvc` files to reference.

### DVC vs Git LFS

| Feature | DVC | Git LFS |
|---|---|---|
| **Designed for** | ML data & models | Large files in general |
| **Storage** | Any remote (S3, GDrive, etc.) | Git server extension |
| **Versioning** | Linked to Git commits | Part of Git history |
| **Pipeline support** | Yes (`dvc.yaml`) | No |
| **ML-specific** | Yes | No |

---

## Kubernetes — What They Don't Tell You

### Liveness vs Readiness Probes

| Probe | Question It Answers | Action on Failure |
|---|---|---|
| **Liveness** | "Is the container still alive?" | K8s **kills and restarts** it |
| **Readiness** | "Is the container ready to receive traffic?" | K8s **removes it from Service** (no traffic) |

```yaml
livenessProbe:
  httpGet:
    path: /health
    port: 5000
  initialDelaySeconds: 30     # Wait 30s before first check
  periodSeconds: 10           # Check every 10s

readinessProbe:
  httpGet:
    path: /ready
    port: 5000
```

> **Why this matters for ML:** A model that takes 2 minutes to load into GPU memory needs a readiness probe — otherwise K8s sends traffic before the model is ready.

### Kubernetes Secrets (Different from GHA Secrets!)

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: mlflow-credentials
type: Opaque
data:
  username: YWRtaW4=          # base64 encoded "admin"
  password: cGFzc3dvcmQ=      # base64 encoded "password"
```

```yaml
# Use in a Pod
env:
  - name: MLFLOW_USER
    valueFrom:
      secretKeyRef:
        name: mlflow-credentials
        key: username
```

> **Tricky Q:** *"Are K8s Secrets encrypted?"*
> **A:** By default, Secrets are only **base64 encoded** (NOT encrypted!). They're stored in etcd. For real security, enable encryption at rest.

### ConfigMaps — Non-Secret Configuration

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: model-config
data:
  MODEL_VERSION: "v2.1"
  BATCH_SIZE: "32"
  THRESHOLD: "0.85"
```

Used for: model hyperparameters, feature flags, endpoint URLs. 
**Secrets** = passwords, API keys. **ConfigMaps** = everything else.

### Namespaces — Logical Isolation

```bash
kubectl create namespace production
kubectl create namespace staging
kubectl get pods -n production    # Only see production pods
```

> **Why this matters:** A team can run staging and production models on the same cluster without interference.

### Rolling Update vs Recreate

| Strategy | Behavior | Downtime? |
|---|---|---|
| **RollingUpdate** (default) | Gradually replaces old pods with new ones | No |
| **Recreate** | Kills all old pods, then creates new ones | Yes |

```yaml
spec:
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1          # Create 1 extra pod during update
      maxUnavailable: 0    # Never have fewer than desired
```

### `kubectl apply` vs `kubectl create`

| Command | Behavior |
|---|---|
| `kubectl create` | Creates resource; **fails** if it already exists |
| `kubectl apply` | Creates if new; **updates** if it already exists |

> **Rule:** Always use `kubectl apply -f` for production (idempotent).

### `imagePullPolicy` — When Does K8s Download the Image?

| Policy | Behavior |
|---|---|
| `Always` | Pull image every time a Pod starts (ensures latest) |
| `IfNotPresent` | Only pull if not cached on the Node |
| `Never` | Never pull; only use local cache |

```yaml
containers:
  - name: my-app
    image: myrepo/model:latest
    imagePullPolicy: Always    # Always get the freshest image
```

> **Tricky Q:** *"If you use `image: myapp:latest` and push a new image with the same tag, will K8s automatically update?"*
> **A:** **No!** K8s won't notice. You must either:
> 1. Use `imagePullPolicy: Always`
> 2. Change the tag (e.g., `myapp:v2`)
> 3. Run `kubectl rollout restart deployment my-deployment`

### What Happens When You Delete a Pod's Data?

| Storage Type | Data After Pod Delete |
|---|---|
| **Container filesystem** | **GONE** — ephemeral |
| **emptyDir Volume** | **GONE** — tied to Pod lifecycle |
| **PersistentVolume (PV)** | **SURVIVES** — independent of Pod |
| **hostPath Volume** | **SURVIVES** — on the Node's disk |

---

## Kubeflow & Monitoring — Deeper Concepts

### A/B Testing — The Deployment Strategy for ML

The lectures mention monitoring but not how to **compare models in production:**

1. Deploy Model A (current) and Model B (new) simultaneously
2. Route 90% of traffic to A, 10% to B
3. Compare metrics (accuracy, latency, user satisfaction)
4. If B wins → gradually shift 100% to B

### Canary Deployment

Deploy the new version to a **small subset** of users first:
- If metrics look good → roll out to everyone
- If metrics degrade → roll back immediately

This is how you avoid deploying a broken model to all users at once.

### Feature Store — The Missing Piece

Not in lectures, but connects Data + Model:
- A **Feature Store** is a centralized repository for feature engineering
- Ensures training features match serving features (training-serving skew)
- Tools: Feast, Tecton, Hopsworks

### CI/CD vs CT (Continuous Training)

| Concept | What It Automates |
|---|---|
| **CI** | Code testing (lint, unit tests) |
| **CD** | Code deployment (Docker push, K8s update) |
| **CT** | Model retraining (trigger on data drift, schedule) |

CT is what Kubeflow enables — triggering retraining automatically when data changes.

### MLOps Maturity Levels

| Level | Description | Course Coverage |
|---|---|---|
| **0** | No MLOps — manual everything | Assignment 1 (the problem) |
| **1** | DevOps for ML — CI/CD pipeline | Lectures 4-6 |
| **2** | Automated training — Experiment tracking | Lectures 3, 5 (MLflow + DVC) |
| **3** | Full automation — Kubeflow + Monitoring | Lecture 9 |

---

## Tricky Quiz Questions

These are the "between the lines" questions a professor loves to ask:

### Git & Security

**Q1.** If you commit a file containing `password=12345` and push to GitHub, will GitHub block the push?
**A:** No. Git pushes everything. GitHub may alert you after the push (secret scanning), but it does NOT block it by default.

**Q2.** You added `data.csv` to `.gitignore`. You then run `git add data.csv`. What happens?
**A:** Git WILL add it! `.gitignore` only prevents auto-tracking. You can force-add ignored files. Use `git add` carefully.

**Q3.** You committed a secret file, then added it to `.gitignore` and deleted it in the next commit. Is the secret safe?
**A:** No! The secret is still in the Git history. Anyone with repo access can see it in old commits.

**Q4.** What is the correct way to store sensitive values (like API keys) in a CI/CD pipeline?
**A:** Use GitHub Secrets (Settings → Secrets) and access via `${{ secrets.KEY_NAME }}`. Never hardcode in YAML or code.

**Q5.** What's the difference between a `.gitignore` and a `.dockerignore`?
**A:** `.gitignore` tells Git which files to ignore. `.dockerignore` tells Docker which files NOT to send to the build context (saves time and image size).

### Docker

**Q6.** You build a Docker image at 10:00 AM. `RUN date > /app/time.txt` is in the Dockerfile. You run the container at 3:00 PM. What time does the file show?
**A:** 10:00 AM. `RUN` executes at build time and the result is baked into the image layer.

**Q7.** Does `EXPOSE 8501` in a Dockerfile actually make port 8501 accessible from outside?
**A:** No. `EXPOSE` is documentation only. You need `docker run -p 8501:8501` to actually publish the port.

**Q8.** What happens to files created inside a running container when the container stops?
**A:** They are LOST (unless you used volumes or bind mounts).

**Q9.** What is the difference between `docker run` and `docker build`?
**A:** `docker build` creates an image from a Dockerfile. `docker run` creates and starts a container from an image.

**Q10.** Can you run `CMD` and `RUN` in the same Dockerfile?
**A:** Yes! `RUN` runs during build (can have multiple). `CMD` runs at startup (only the last one counts).

**Q11.** Why do we use `python:3.10-slim` instead of `python:3.10`?
**A:** `slim` removes unnecessary system packages, making the image much smaller (100MB vs 900MB+). Faster to build, push, and pull.

**Q12.** What does `--no-cache-dir` do in `pip install --no-cache-dir`?
**A:** Prevents pip from storing downloaded packages in cache. Makes the Docker image smaller.

### CI/CD

**Q13.** In GitHub Actions, do jobs run sequentially or in parallel by default?
**A:** In parallel! Use `needs:` to make them sequential.

**Q14.** What happens if a step fails and the next step has no `if:` condition?
**A:** The next step is SKIPPED because of the hidden `if: success()` default.

**Q15.** Can you access a file created in Job A from Job B without using artifacts?
**A:** No! Each job runs on a separate VM with an empty disk. You must use upload/download artifacts.

**Q16.** What is `workflow_dispatch` used for?
**A:** It adds a manual "Run workflow" button in the GitHub Actions UI. Used for on-demand deployments.

**Q17.** What's the difference between `branches: [main]` and `branches-ignore: [main]` in the `on: push` trigger?
**A:** `branches: [main]` runs ONLY on pushes to main. `branches-ignore: [main]` runs on pushes to ALL branches EXCEPT main.

**Q18.** If you write `if: github.ref == 'refs/heads/main'` on a step, will it still check for previous step failures?
**A:** NO! The custom `if:` overrides the hidden `success()` check. The step becomes "status-blind." Fix: `if: success() && github.ref == 'refs/heads/main'`

**Q19.** Can you set a variable in one step and read it in the next step?
**A:** Not with shell variables (each step is a new shell). Use `echo "KEY=value" >> $GITHUB_ENV` or the `env:` block.

**Q20.** What does `exit 1` do in a CI/CD step?
**A:** It causes the step to FAIL with a non-zero exit code, which stops the pipeline (or triggers `failure()` conditions).

### MLflow

**Q21.** What happens if you call `mlflow.log_metric()` outside of `with mlflow.start_run():`?
**A:** It will fail or create an implicit run. All logging MUST be inside the run context.

**Q22.** Can you log the same metric multiple times with different values?
**A:** Yes! Use `step=epoch` parameter to log metric values over time (creates learning curves).

**Q23.** What's the difference between `mlflow.log_param()` and `mlflow.log_metric()`?
**A:** Parameters are inputs (set once per run: LR, epochs). Metrics are outputs (can change: loss per epoch).

**Q24.** Where does MLflow store artifacts by default?
**A:** In a local `./mlruns/` directory. For production, use a remote tracking server (PostgreSQL + S3).

**Q25.** What is the purpose of `mlflow.set_tag()`?
**A:** Tags are labels for searching and filtering runs (e.g., `model_type: CNN`, `student_id: 123`). They don't affect training.

### DVC

**Q26.** Does `git pull` download the actual data tracked by DVC?
**A:** No! `git pull` only downloads the `.dvc` pointer files. You need `dvc pull` to get the actual data.

**Q27.** What information does a `.dvc` file contain?
**A:** An MD5 hash of the data, the file size, and the file path. It's a pointer, not the data itself.

**Q28.** Why can't Git handle large ML datasets?
**A:** Git stores full copies of binary files on every change (no line-diffs for binaries). A 5GB dataset with 10 versions = 50GB in `.git/`.

**Q29.** What happens if you run `dvc pull` before `git checkout`?
**A:** It might pull wrong or outdated data because the `.dvc` pointer files haven't been updated to the correct version yet.

### Kubernetes

**Q30.** What happens when a Pod exceeds its memory limit?
**A:** K8s IMMEDIATELY KILLS it (OOM — Out of Memory). Unlike CPU, which is just throttled.

**Q31.** What happens when a Pod exceeds its CPU limit?
**A:** K8s THROTTLES the CPU (slows it down). The Pod is NOT killed.

**Q32.** Can two Pods in the same cluster communicate directly by Pod IP?
**A:** Technically yes, but you should NEVER do this. Pod IPs change when pods restart. Always use Services.

**Q33.** What is the difference between `NodePort` and `ClusterIP` service types?
**A:** `ClusterIP` = internal only (pod-to-pod). `NodePort` = accessible from outside the cluster (browser).

**Q34.** What port range is valid for `nodePort`?
**A:** 30000 - 32767 only.

**Q35.** What happens if you delete a Pod that is managed by a Deployment?
**A:** K8s automatically creates a new Pod to maintain the desired replica count (self-healing).

**Q36.** What is `etcd` and what happens if it goes down?
**A:** etcd is the cluster's database storing all state. If it goes down, the cluster "freezes" — no new changes can be made.

**Q37.** What does `kubectl apply -f file.yaml` do differently from `kubectl create -f file.yaml`?
**A:** `apply` creates if new, updates if exists (idempotent). `create` fails if the resource already exists.

**Q38.** If you push a new Docker image with the same tag (e.g., `myapp:latest`), will K8s automatically update the running pods?
**A:** NO! K8s doesn't know the image changed. You must use `kubectl rollout restart` or change the tag.

**Q39.** What is the difference between `requests` and `limits` for resources?
**A:** `requests` = guaranteed minimum (used for scheduling). `limits` = maximum allowed (enforced at runtime: CPU throttled, Memory killed).

**Q40.** How does the K8s Scheduler decide which Node to place a Pod on?
**A:** It checks which Nodes have enough resources (CPU, RAM, GPU) to satisfy the Pod's `requests`, then picks the best fit.

### Kubeflow & Monitoring

**Q41.** What is the difference between Data Drift and Concept Drift?
**A:** Data Drift = input distribution changes (users changed behavior). Concept Drift = the relationship between inputs and outputs changes (what "good" means changed).

**Q42.** Can a model fail silently even if all infrastructure metrics are green?
**A:** YES! This is a "Silent Failure." The system is healthy (200 OK, low latency) but the model serves degraded predictions.

**Q43.** What is a CLIP Score used for?
**A:** Measuring how well a generated image matches its text prompt. Used to detect drift in text-to-image models.

**Q44.** Why can't standard K8s replace Kubeflow for ML pipelines?
**A:** K8s manages "always-on" services but lacks: run-and-exit DAG orchestration, step-level caching, data lineage visualization, and data-event triggers.

**Q45.** What is Human-in-the-Loop (HITL) in monitoring?
**A:** Routing low-confidence predictions to human reviewers who label them, creating a "Gold Standard" dataset for retraining.

### Cross-Topic Connections

**Q46.** Why do we need BOTH MLflow AND DVC? Don't they overlap?
**A:** MLflow tracks experiments (params, metrics, models). DVC tracks data versions. Together: Code (Git) + Data (DVC) + Experiments (MLflow) = full reproducibility.

**Q47.** Why do we need BOTH GitHub Actions AND Kubeflow? Don't they overlap?
**A:** GHA handles CI/CD (code quality, Docker builds). Kubeflow handles ML operations (training orchestration, GPU scheduling, data pipelines). They complement each other.

**Q48.** In the full MLOps pipeline, which tool is responsible for each step?
**A:** Git Push → DVC Pull (data) → Pytest (testing) → MLflow (tracking) → Docker (packaging) → K8s/Kubeflow (deployment/orchestration) → Monitoring (feedback)

**Q49.** What is the connection between Docker layer caching and CI/CD speed?
**A:** In CI/CD, if you structure your Dockerfile correctly (copy requirements first), Docker reuses cached layers. This means `docker build` takes seconds instead of minutes, saving CI/CD runner time and cost.

**Q50.** Why does Assignment 1 exist if the rest of the course teaches you how to fix those problems?
**A:** It's the **motivation for the entire course**. Every tool (Conda, Docker, MLflow, DVC, CI/CD, K8s) solves a specific problem experienced in Assignment 1: dependency hell → Conda/Docker, no tracking → MLflow, no data versioning → DVC, manual deployment → CI/CD + K8s.

### Bonus Tricky Questions

**Q51.** What is idempotency and why does it matter in MLOps?
**A:** An operation is idempotent if running it multiple times produces the same result. `kubectl apply` is idempotent (safe to re-run). `kubectl create` is NOT (fails on second run).

**Q52.** What is "training-serving skew"?
**A:** When the features used during training differ from those used during inference. Causes silent failures in production.

**Q53.** Why should you use `random_state=42` (or any fixed seed) in ML experiments?
**A:** For reproducibility! Without a fixed seed, random operations (data shuffling, weight initialization) produce different results each run, making comparisons meaningless.

**Q54.** If a Docker container is running a model server and the model file is stored in the container filesystem (not a volume), what happens when K8s restarts the Pod?
**A:** The model file is LOST. The new Pod starts with a fresh container. The model must be re-downloaded or baked into the image.

**Q55.** What's the difference between horizontal and vertical scaling in K8s?
**A:** Horizontal = add more Pods (replicas: 3 → 10). Vertical = give each Pod more resources (memory: 2Gi → 8Gi). K8s supports both.
