# GitHub Actions & Workflows — MLOps Edition

This document covers execution models, scopes, parameters, conditional logic, and architectural comparisons for Continuous Integration (CI), Continuous Delivery (CD), and ML Orchestrators.

---

## 1. Jobs, Machines, and Steps: Workflow Execution in ML Pipelines

### Jobs Run on Separate Machines (Runners)
In a GitHub Actions workflow, each **job** runs on its own fresh virtual machine (a runner). These machines are completely isolated from one another — they do not share a filesystem, environment variables, memory, or any state.

In an MLOps context, this is critical because different stages of an ML pipeline have very different resource needs. Your training job might need an expensive GPU runner, whereas your evaluation or deployment job can run on a cheap CPU machine. However, this also means the trained model file produced on the GPU machine is invisible to the next job unless you explicitly pass it over.

```yaml
# ❌ THIS WILL FAIL
jobs:
  train:
    runs-on: gpu-runner          # expensive GPU machine
    steps:
      - name: Train model
        run: python train.py     # produces model.pkl

  evaluate:
    runs-on: ubuntu-latest       # ← brand new CPU machine, model.pkl does NOT exist here!
    steps:
      - name: Evaluate model
        run: python evaluate.py  # ❌ Fails — model.pkl was on the GPU machine
```

#### The Solution: GHA Artifacts
GitHub Actions provides `upload-artifact` and `download-artifact` actions to explicitly shuttle files between jobs through GitHub's storage layer:

```yaml
# ✅ CORRECT IMPLEMENTATION
jobs:
  train:
    runs-on: gpu-runner
    steps:
      - name: Train model
        run: python train.py     # produces model.pkl and metrics.json
      - name: Upload trained model
        uses: actions/upload-artifact@v4
        with:
          name: trained-model
          path: |
            model.pkl
            metrics.json

  evaluate:
    runs-on: ubuntu-latest
    needs: train                 # wait for training to finish first
    steps:
      - name: Download trained model
        uses: actions/download-artifact@v4
        with:
          name: trained-model
      - name: Evaluate model
        run: python evaluate.py  # ✅ Works — model.pkl and metrics.json are now available

  deploy:
    runs-on: ubuntu-latest
    needs: evaluate              # only deploy after evaluation passes
    steps:
      - name: Download trained model
        uses: actions/download-artifact@v4
        with:
          name: trained-model
      - name: Deploy model to serving endpoint
        run: python deploy.py
```

* **What happens under the hood:**
  1. The `train` job uploads `model.pkl` and `metrics.json` to GitHub's artifact storage.
  2. The `evaluate` job (on a different, cheaper machine) downloads them before running evaluation.
  3. The `deploy` job downloads the same artifact and pushes the model to a serving endpoint.

* **MLOps Tip:** For large model files (multi-GB checkpoints), GitHub artifact storage has size limits. In practice, teams push model artifacts to an external Model Registry (MLflow, W&B, S3) during training and pull them by version in later jobs — using GHA artifact storage only for lightweight metadata like metrics and configs.

---

### Steps Run on the Same Machine — But in Separate Terminals
Within a single job, all **steps** run on the same machine sequentially. However, each step is executed in its own shell process — meaning the environment is not fully shared between steps.

* **The Key Implication:** Environment variables set with `export` in one step do NOT carry over to the next step.

```yaml
# ❌ THIS WILL FAIL
jobs:
  train:
    runs-on: ubuntu-latest
    steps:
      - name: Preprocess data and compute dataset hash
        run: |
          python preprocess.py
          export DATASET_VERSION=$(python get_hash.py)
      - name: Train model using dataset version
        run: |
          # ❌ DATASET_VERSION is gone — this is a new shell process
          python train.py --dataset-version $DATASET_VERSION
```

#### The Solution: `$GITHUB_ENV` and `$GITHUB_OUTPUT`
To pass environment variables across steps, echo them to the special `$GITHUB_ENV` file:

```yaml
# ✅ CORRECT ENV HANDOVER
jobs:
  train:
    runs-on: ubuntu-latest
    steps:
      - name: Preprocess data and compute dataset hash
        run: |
          python preprocess.py
          echo "DATASET_VERSION=$(python get_hash.py)" >> $GITHUB_ENV
      - name: Train model using dataset version
        run: |
          # ✅ DATASET_VERSION is available
          python train.py --dataset-version $DATASET_VERSION
```

Similarly, to pass structured outputs like model performance metrics between steps, use `$GITHUB_OUTPUT`:

```yaml
# ✅ CORRECT OUTPUT HANDOVER
jobs:
  evaluate:
    runs-on: ubuntu-latest
    steps:
      - name: Evaluate model and extract accuracy
        id: eval
        run: |
          python evaluate.py
          ACC=$(python -c "import json; print(json.load(open('metrics.json'))['accuracy'])")
          echo "accuracy=$ACC" >> $GITHUB_OUTPUT
      - name: Gate on accuracy threshold
        run: |
          ACC=${{ steps.eval.outputs.accuracy }}
          # Use the accuracy score to decide whether to proceed
          python -c "
          acc = float('$ACC')
          if acc < 0.85:
              raise SystemExit('Model accuracy $ACC below threshold 0.85 — blocking deploy')
          print(f'Accuracy {acc} passed threshold')
          "
```

---

### Summary: What Persists and What Doesn't

| Resource / Concept | Within a Job (Same Machine) | Across Jobs (Different Machines) |
|---|---|---|
| **Filesystem / Files** (e.g. `model.pkl`, datasets) | Shared | Needs `upload`/`download-artifact` or a model registry |
| **`export VAR=...` variables** | Dies with each step's shell | Does not cross jobs |
| **`$GITHUB_ENV` variables** (e.g. run ID, data hash) | Persists across steps | Dies with the machine; does not cross jobs |
| **`$GITHUB_OUTPUT` values** (e.g. accuracy) | Accessible via `steps.<id>.outputs` | Does not cross jobs |
| **Installed packages / ML libraries** | Shared within the job | Must reinstall on each machine runner |
| **GPU / Hardware resources** | Same runner throughout job | Each job requests its own runner |

---

## 2. Environment Variable Scoping: Global, Job, and Step Level

GitHub Actions lets you define `env` variables at three levels. Override priority (narrower scope wins):
$$\text{Step env} > \text{Job env} > \text{Global env}$$

### Global Level — Visible to all jobs and all steps
```yaml
env:
  EXPERIMENT_NAME: churn-v2   # every job and step can read this

jobs:
  train:
    runs-on: ubuntu-latest
    steps:
      - run: echo $EXPERIMENT_NAME   # ✅ Prints "churn-v2"
  deploy:
    runs-on: ubuntu-latest
    steps:
      - run: echo $EXPERIMENT_NAME   # ✅ Prints "churn-v2"
```
* **Best for:** Global variables like Registry URLs, Experiment names, and target Python versions.

### Job Level — Visible only to steps inside that job
```yaml
env:
  EXPERIMENT_NAME: churn-v2   # global

jobs:
  train:
    runs-on: ubuntu-latest
    env:
      BATCH_SIZE: "64"        # only the train job sees this
    steps:
      - run: echo $BATCH_SIZE        # ✅ Prints "64"
      - run: echo $EXPERIMENT_NAME   # ✅ Prints "churn-v2"
  deploy:
    runs-on: ubuntu-latest
    steps:
      - run: echo $BATCH_SIZE        # ❌ Empty — BATCH_SIZE belongs to train job
      - run: echo $EXPERIMENT_NAME   # ✅ Prints "churn-v2"
```
* **Best for:** Hardware config (`CUDA_VISIBLE_DEVICES`), local data paths, or job-specific hyperparameter defaults.

### Step Level — Visible only to that one step
```yaml
jobs:
  train:
    runs-on: ubuntu-latest
    steps:
      - name: Normal training
        run: echo $LOG_LEVEL         # ❌ Empty, not set
      - name: Debug run
        env:
          LOG_LEVEL: DEBUG           # only this step sees it
        run: echo $LOG_LEVEL         # ✅ Prints "DEBUG"
      - name: Back to normal
        run: echo $LOG_LEVEL         # ❌ Empty again
```
* **Best for:** One-off overrides like debug flags or custom temporary variables without affecting the rest of the pipeline.

### Override Example — Step wins over Global
```yaml
env:
  LOG_LEVEL: INFO             # global default

jobs:
  train:
    runs-on: ubuntu-latest
    steps:
      - run: echo $LOG_LEVEL         # Prints "INFO" (global default)
      - env:
          LOG_LEVEL: DEBUG           # step overrides global
        run: echo $LOG_LEVEL         # Prints "DEBUG" (step wins)
      - run: echo $LOG_LEVEL         # Prints "INFO" (global restored)
```

---

## 3. `if` Conditions: Controlling What Runs and When

`if` conditions can be placed at the **job level** or the **step level**. The three most important conditional checks are:
- `success()`: (Default) Runs only if all previous steps/jobs succeeded.
- `failure()`: Runs only if a previous step/job failed.
- `always()`: Runs no matter what (even if previous steps/jobs failed or were cancelled).

### Step Level `if`
Controls whether an individual step runs. The other steps in the job are not affected.

```yaml
jobs:
  train:
    runs-on: ubuntu-latest
    steps:
      - name: Train model
        run: python train.py
      - name: Upload to registry
        if: success()           # runs only if train succeeded
        run: python upload.py
      - name: Notify on failure
        if: failure()           # runs only if train failed
        run: echo "Training failed!"
      - name: Clean up temp files
        if: always()            # runs even if a previous step failed
        run: rm -rf /tmp/model_cache
```

### Job Level `if` — Without `needs`
Without `needs`, all jobs start at the same time when the workflow triggers. A job-level `if` is evaluated immediately at startup:
- `success()` is always true (since no upstream jobs could have failed yet).
- `failure()` is always false.
- This means job-level conditionals are not meaningful unless combined with `needs`.

```yaml
# ❌ INCORRECT / MEANINGLESS CONDITIONALS
jobs:
  train:
    runs-on: ubuntu-latest
    if: success()   # always runs (no upstream to fail)
    steps:
      - run: python train.py
  evaluate:
    runs-on: ubuntu-latest
    if: failure()   # never runs (no upstream job could have failed yet)
    steps:
      - run: python evaluate.py
```

### Job Level `if` — With `needs`
When a job has `needs`, it waits for the upstream job to finish, then evaluates its `if` condition against the upstream result.

```yaml
# ✅ CORRECT JOB-LEVEL CONDITIONALS
jobs:
  train:
    runs-on: ubuntu-latest
    steps:
      - run: python train.py

  deploy:
    runs-on: ubuntu-latest
    needs: train
    if: success()   # runs only if train passed (this is the default behavior)
    steps:
      - run: python deploy.py

  notify:
    runs-on: ubuntu-latest
    needs: train
    if: failure()   # runs only if train failed
    steps:
      - run: echo "Training failed!"

  report:
    runs-on: ubuntu-latest
    needs: train
    if: always()    # runs whether train passed or failed
    steps:
      - run: python generate_report.py
```

---

## 4. Kubeflow Pipelines vs. GitHub Actions Workflows

While both tools let you define multi-step ML workflows, they are built on fundamentally different models. GitHub Actions is a **general-purpose CI/CD runner**, whereas Kubeflow is a **dedicated ML orchestrator** built to manage compute resources, data, and pipeline state natively.

### GitHub Actions: Just a Runner
GHA schedules and runs jobs on VMs. It has no awareness of ML concepts (models, datasets, GPU allocations). You are responsible for installing dependencies, transferring data, and tearing down systems.

```
trigger (push/PR)
│
▼
┌─────────┐         ┌──────────┐         ┌────────┐
│  train  │────────▶│ evaluate │────────▶│ deploy │
│  VM #1  │         │  VM #2   │         │  VM #3 │
└─────────┘         └──────────┘         └────────┘
     │                    ▲
     └──── model.pkl ─────┘
       (artifact upload/
           download)
```

### Kubeflow: A Resource-Aware ML Orchestrator
Kubeflow Pipelines runs on Kubernetes. Each step in a pipeline is a container scheduled onto a node. Because it sits on top of Kubernetes, Kubeflow can:
- **Request specific resources per step**: e.g., CPUs, GPUs, memory limits. Kubernetes will automatically bin-pack these requests onto appropriate nodes.
- **Mount shared storage**: All steps in a pipeline share the same Persistent Volume (PV), so files written by one step are immediately readable by the next with no upload/download overhead.
- **Cache step outputs**: If a step's inputs (code + parameters + input data) haven't changed, Kubeflow skips running it and reuses the cached output automatically.

```
pipeline run
│
▼
┌─────────────┐         ┌──────────────┐         ┌────────────┐
│  preprocess │────────▶│    train     │────────▶│   deploy   │
│  container  │         │  container   │         │ container  │
│  (2 CPU)    │         │ (1 GPU, 8GB) │         │  (1 CPU)   │
└─────────────┘         └──────────────┘         └────────────┘
       │                       ▲                       ▲
       └─────── shared Persistent Volume (/mnt/data) ──┘
```

### Data Sharing: GHA Artifacts vs. Kubeflow Shared Volume

#### GitHub Actions
Each job is on a different machine, so you must explicitly package and ship outputs:
```yaml
# Job 1: train — uploads model to artifact storage
- uses: actions/upload-artifact@v4
  with:
    name: trained-model
    path: model.pkl

# Job 2: evaluate — downloads model before it can use it
- uses: actions/download-artifact@v4
  with:
    name: trained-model
```

#### Kubeflow Pipelines
Steps communicate by writing to and reading from file paths on a shared volume. You define an output path for one step and pass it as the input path to the next:
```python
@component
def train(output_model_path: OutputPath(str)):
    import pickle, sklearn
    model = sklearn.linear_model.LogisticRegression().fit(X, y)
    with open(output_model_path, "wb") as f:
        pickle.dump(model, f)

@component
def evaluate(input_model_path: InputPath(str)):
    import pickle
    with open(input_model_path, "rb") as f:
        model = pickle.load(f)
    # evaluate...

@pipeline
def ml_pipeline():
    train_step = train()
    evaluate_step = evaluate(input_model_path=train_step.output)
```

---

### Step Caching in Kubeflow
Kubeflow has built-in step caching. If a step's inputs are identical to a previous run, Kubeflow skips the step and reuses the cached output.

```python
@component
def preprocess(raw_data_path: str, output_path: OutputPath(str)):
    # heavy data cleaning...
    pass

# In the pipeline definition:
preprocess_step = preprocess(
    raw_data_path="gs://bucket/raw.csv",
    output_path="/mnt/pipeline/clean.parquet"
)
preprocess_step.execution_options.caching_strategy.max_cache_staleness = "P30D"
# ↑ reuse cached output if inputs haven't changed in the last 30 days
```
GitHub Actions has no equivalent native caching for step outputs. You can cache installed dependencies (`actions/cache`) but not the result of running your ML code.

---

### Side-by-Side Comparison

| Feature | GitHub Actions | Kubeflow Pipelines |
|---|---|---|
| **Primary purpose** | CI/CD runner | ML pipeline orchestrator |
| **Resource management** | You manage runners yourself | Declares CPU/GPU/memory per step |
| **Step isolation** | Each job on a separate VM | Each step in a separate container |
| **Data sharing** | Must upload/download artifacts | Shared Persistent Volume |
| **Step communication** | Artifact storage or registry | Input/output file paths on shared volume |
| **Step caching** | No native output caching | Built-in, based on input fingerprint |
| **ML awareness** | Generic runner | Built for ML pipelines (metadata, lineage) |
| **Where it runs** | GitHub-hosted or self-hosted VMs | Kubernetes cluster |
| **Best for** | CI/CD, lightweight trigger automation | Production ML pipelines with resource control |

---

## 5. Why Replicas in Kubernetes but Not in Kubeflow

This distinction relates directly to the type of workload and who the clients are.

### Replicas in Kubernetes: Serving a Model to Real Users
When you deploy a trained model as an inference service (e.g., in standard K8s), real users or applications are sending requests to it — potentially thousands per second. This workload is:
- **Stateless**: Each request is independent, and any replica can handle it.
- **Latency-sensitive**: Users are waiting for a real-time response.
- **Unpredictably concurrent**: Traffic spikes need to be absorbed.

To provide **high availability and high concurrency**, you run multiple replicas of the same container behind a load balancer. If one replica is busy, another handles the request. If one crashes, the others keep serving.

```yaml
# Kubernetes Deployment — model serving
apiVersion: apps/v1
kind: Deployment
metadata:
  name: churn-model-server
spec:
  replicas: 3             # 3 identical pods behind a load balancer
  template:
    spec:
      containers:
        - name: model-server
          image: churn-model:v1
```

```
                 clients (users / apps)
                           │
                     load balancer
             ┌─────────────┼─────────────┐
             ▼             ▼             ▼
         replica1      replica2      replica3   (serving model)
```

---

### No Replicas in Kubeflow: No Clients, Just Computation
A Kubeflow pipeline step has no external clients. Nothing is waiting for it to respond in real-time. It runs once, does its work (preprocessing, training, or evaluation), writes its output, and exits. Running three copies of a training step simultaneously would be wasteful — they would overwrite each other's outputs.

What Kubeflow does instead is **distribute the work within a single step** using frameworks like PyTorch Distributed or TensorFlow's distributed strategy. Instead of duplicating the pipeline step, the step itself spawns multiple workers that cooperatively process shards of the data and synchronize gradients to produce a single model faster.

```
                  Kubeflow pipeline step: train
                 ┌─────────────────────────────┐
                 │  worker 0  ──┐              │
                 │  worker 1  ──┼─ sync grads ─┼──▶ model.pkl
                 │  worker 2  ──┤              │
                 │  worker 3  ──┘              │
                 └─────────────────────────────┘
                  (no load balancer / clients)
```

---

### Core Distinction: Replicas vs. Distributed Steps

| Attribute | Kubernetes Replicas (Serving) | Kubeflow Distributed Step (Training) |
|---|---|---|
| **Why run multiple instances?** | Handle concurrent external requests | Process data faster in parallel |
| **Who calls them?** | Real users / applications | Nobody — self-contained computation |
| **Output** | Each replica responds independently | Workers cooperate to produce one result |
| **State** | Stateless — each request is isolated | Stateful — workers share/sync gradients |
| **Failure behavior** | Other replicas keep serving | Whole step typically restarts |
| **Scaling trigger** | Traffic load (concurrency) | Dataset size / model parameter size |

---

## 6. Continuous Delivery vs. Continuous Deployment

These two terms share the same abbreviation (**CD**), but the difference comes down to where the pipeline stops and who triggers the final release.

```
Continuous Integration (CI)
    │   - Build & Test Code
    ▼
Continuous Delivery (CD)
    │   - Deploy to Staging / Production-like environment
    ▼   - STOP here for Manual Approval
[ Manual Approval ]
    │
    ▼
Continuous Deployment (CD)
        - Deploy to Live Production automatically (No human gate)
```

### Continuous Delivery
The pipeline automatically builds, tests, and delivers the artifact to a staging or production-like environment for final validation. It stops there. A human reviews the result and manually decides when to promote it to production.
- **In MLOps:** A new model is trained, evaluated, and deployed to a staging/shadow endpoint automatically. A data scientist reviews the metrics and shadow traffic results before manually promoting it to the live serving endpoint.

### Continuous Deployment
Every step is automated end-to-end, all the way to production. If all quality gates pass, the artifact goes live automatically with no human in the loop.
- **In MLOps:** A new model trains, hits the accuracy threshold, and is swapped into the live serving endpoint without anyone manually approving it.

### Key Difference Summary

| Feature | Continuous Delivery | Continuous Deployment |
|---|---|---|
| **Pipeline stops at** | Staging / Pre-prod environment | Live Production environment |
| **Who triggers production?** | A human, manually | The pipeline, automatically |
| **Human involvement** | Required before going live | Only needed if something breaks |
| **Risk control** | Human judgment acts as the final gate | Relies entirely on automated quality gates |

* **Which to use in MLOps?** Most teams start with **Continuous Delivery**. ML models affect real-world decisions, and having a human review metrics before going live is worth the friction. **Continuous Deployment** makes sense once the automated evaluation suite is mature and trustworthy enough to catch silent regressions on its own.
