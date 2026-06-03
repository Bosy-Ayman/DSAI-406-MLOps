# MLOps Comprehensive Study Guide: Scaling Production & Live System Monitoring

**Course:** ML Engineering for Production (DSAI 406)

**Institution:** Zewail City of Science and Technology

**Instructor:** Dr. Mohamed Ghalwash

## Part 1: Scaling the Research Lifecycle (GHA vs. Kubeflow)

### 1.1 The Operational Wall: Why GitHub Actions is Insufficient for Heavy AI Workloads

While GitHub Actions (GHA) functions excellently for standard Continuous Integration (CI) tasks—such as linting code, running unit tests, building Docker containers, and pushing images to registries—it fails when tasked with large-scale machine learning training and orchestration. GHA operates as an isolated **Job Runner**, whereas robust MLOps requires a **Resource Scheduler**.

- **The Data Locality Tax:** GHA runners execute workloads in external virtual machines isolated from local cluster data. If a pipeline requires retraining on a newly collected 1TB dataset, GHA forces the system to physically move that 1TB across networks into the ephemeral runner VM. Conversely, an in-cluster orchestrator schedules workloads directly on nodes where storage volumes are already locally attached.
    
- **Hardware and Lifecycle Limitations:** Standard GHA environments rely on standard CPU runners. Managing self-hosted GPU nodes (e.g., NVIDIA A100/H100 clusters) via GHA is highly complex. Furthermore, deep learning jobs often require hours or days to execute. GHA imposes tight execution time-outs and lacks the resilience needed to survive infrastructural drops without full workflow restarts.
    
- **Linear Execution Limitations:** Hyperparameter optimization (AutoML) requires spinning up dozens of parallel training experiments simultaneously. GHA queues these tasks linearly or hits strict parallel runner limitations, making massive grid or random searches highly inefficient.
    

> **Core MLOps Axiom:** Use **GitHub Actions** to guarantee code integrity and handle software engineering CI/CD. Use **Kubeflow** within your cluster to ensure scientific reproducibility, data persistence, and deep-learning resource management.

### 1.2 The Three Critical Operational Gaps of Standard Kubernetes

Standard Kubernetes (K8s) excels at managing microservices, but it does not naturally comprehend the distinct lifecycle of data science experiments.

```
┌──────────────────────────────────────────────────────────┐
│              Standard Kubernetes Layer                   │
│  - Keeps services "Always-On"    - Tracks State (Health) │
└────────────────────────────┬─────────────────────────────┘
                             │  Missing Machine Learning Logic!
                             ▼
┌──────────────────────────────────────────────────────────┐
│                 Kubeflow Platform Layer                  │
│  - Run-and-Exit Pipelines      - Visualizes Data Lineage  │
│  - Tracks Model Metrics        - Event-Driven Triggering │
└──────────────────────────────────────────────────────────┘
```

1. **The Orchestration Gap:** Standard K8s resources (Deployments, Services) are designed to be "always-on" and respond continuously to web traffic. Machine learning pipelines, however, require sequential "run-and-exit" logic. Task B must execute only after Task A finishes cleanly, consuming massive resources during runtime and releasing them completely upon termination.
    
2. **The Visibility Gap:** While logging tools monitor health stats and model registries store end artifacts, K8s lacks native Directed Acyclic Graph (DAG) structures. It cannot map or visualize the end-to-end lineage of how raw scraped files flowed through preprocessing and training components down to the deployed service.
    
3. **The Trigger Gap:** K8s relies on configuration updates or human-driven commands. It lacks native mechanism hooks to listen to internal cluster storage events (e.g., triggering a pipeline automatically the moment 50,000 new images are written to object storage) without writing custom polling infrastructure.
    

### 1.3 Deep-Dive Architecture: GHA vs. Kubeflow Scenarios

The following architectural breakdowns demonstrate how Kubeflow natively solves complex production engineering roadblocks that cause traditional CI/CD setups to fail.

#### Scenario 1: The "Data Tax" Mystery (Data Sharing)

- **The Problem:** Moving 1TB of raw biological or visual data across isolated execution nodes.
    
- **GHA Architecture:** Executes on entirely separate VMs. Job A must explicitly package, compress, and upload the artifact to external cloud storage. Job B must then spend time downloading and unzipping that same file before starting work.
    
- **Kubeflow Architecture:** Leverages Kubernetes Persistent Volumes (PV) and Persistent Volume Claims (PVC). When Task A finishes, the data remains static on disk. Task B simply mounts the exact same volume path that Task A just wrote to, eliminating network transfer overhead completely.
    

|**Vector**|**GitHub Actions Approach**|**Kubeflow Pipelines (KFP) Approach**|
|---|---|---|
|**Mechanic**|Explicitly uploads and downloads compressed zip artifacts across network boundaries.|Attaches and mounts shared cluster Persistent Volumes (PV) natively.|
|**Data Flow**|`python clean.py --out data.zip` $\rightarrow$ `upload-artifact@v4` $\rightarrow$ `download-artifact@v4`|Pass `dsl.OutputPath` and `dsl.InputPath` file references directly between components.|
|**Performance**|Network-bound; throttled by storage read/write limits and external bandwidth costs.|Immediate disk-speed access; zero network transit overhead.|

#### Scenario 2: The "OOM" (Out of Memory) Issue (Resource Allocation)

- **The Problem:** Managing a shared cluster node containing 64GB RAM and 1 GPU when Researcher A submits a massive data preprocessing job (60GB RAM, 0 GPU) while Researcher B simultaneously submits a heavy model training job (8GB RAM, 1 GPU).
    
- **GHA Architecture:** GHA functions as an un-coordinated job runner. It sees that the self-hosted runner agent is online and accepts both jobs simultaneously. The host Operating System runs out of memory, triggers the Out-Of-Memory (OOM) killer, and abruptly terminates Researcher A's long-running script.
    
- **Kubeflow Architecture:** Kubeflow is fully resource-aware. It parses specific declarative container resource requests and constraints. It identifies that the combined RAM requirements ($60\text{GB} + 8\text{GB} = 68\text{GB}$) exceed the physical limits of the node ($64\text{GB}$). Kubeflow handles this gracefully by placing Researcher B's training job into a `PENDING` state, guaranteeing Researcher A's process completes safely before scheduling the next workload.
    

#### Scenario 3: The "Resume" Logic (Pipeline Caching)

- **The Problem:** A multi-step pipeline fails at Step 3 (Model Training) after Step 1 (Data Fetching) and Step 2 (Data Cleaning) spent hours processing.
    
- **GHA Architecture:** GHA executes jobs as monolithic units or isolated execution blocks. If an error occurs midway through a job step, the entire workflow must be restarted from absolute scratch, re-running completed upstream tasks and wasting expensive compute cycles.
    
- **Kubeflow Architecture:** Kubeflow components record individual execution hashes, configuration inputs, and output paths inside a unified Metadata Store. When a pipeline is restarted, Kubeflow checks if the inputs to upstream components match prior successful runs. If true, it skips execution entirely, instantly pulls the existing output from the cache, and resumes work directly at the failed component.
    

### 1.4 Production-Grade Python SDK Construction

The following script details how to programmatically implement a Kubeflow pipeline using the `kfp` SDK. It includes explicit volume handling, custom container resource constraints, and GPU configurations.

```python
from kfp import dsl, compiler

# Component 1: High-RAM Data Preprocessing
@dsl.component(
    base_image='python:3.9',
    packages_to_install=[]
)
def preprocess_data(data_path: str, cleaned_data: dsl.OutputPath(str)):
    """
    Reads raw data and exports the path containing cleaned binaries.
    Leverages shared cloud storage mounts instead of explicitly passing heavy files.
    """
    import os
    print(f"Reading raw data from source path: {data_path}")
    
    # Simulating data ingestion and cleaning pipeline
    processed_target_dir = "/mnt/data/cleaned_sequences.bin"
    
    # Write the pointer/metadata output directly to the shared storage layer
    with open(cleaned_data, 'w') as f:
        f.write(processed_target_dir)

# Component 2: Multi-Framework GPU Training 
@dsl.component(
    base_image='pytorch/pytorch:latest',
    packages_to_install=['mlflow']
)
def train_model(cleaned_data_path: dsl.InputPath(str), epochs: int, lr: float):
    """
    Imports the cleaned data path and boots up distributed GPU training routines.
    Logs metadata parameters directly back to the active MLflow tracking server.
    """
    import mlflow
    
    # Read the data pointer generated upstream
    with open(cleaned_data_path, 'r') as f:
        resolved_data_path = f.read().strip()
        
    print(f"Loading validated training binary from: {resolved_data_path}")
    print(f"Initializing Pytorch network for {epochs} epochs with learning rate: {lr}")
    
    # Communicating metrics back to tracking servers
    mlflow.set_tracking_uri("http://mlflow-service.k8s.local:5000")
    mlflow.log_param("learning_rate", lr)
    mlflow.log_param("epochs", epochs)
    mlflow.log_metric("accuracy", 0.945)

# Pipeline Construction and Declarative DAG Orchestration
@dsl.pipeline(
    name="personacanvas-research-lifecycle",
    description="Orchestrated production pipeline featuring rigid resource safety and execution caching."
)
def research_pipeline(data_path: str = "s3://production-bucket/raw-v1", lr: float = 0.01):
    
    # Instantiating Task 1 with explicit Memory and CPU limits
    prep_task = preprocess_data(data_path=data_path)
    prep_task.set_memory_limit('60Gi')
    prep_task.set_cpu_limit('4')
    
    # Instantiating Task 2 with explicit GPU resource tracking
    train_task = train_model(
        cleaned_data_path=prep_task.outputs['cleaned_data'], 
        epochs=10, 
        lr=lr
    )
    train_task.set_gpu_limit(1)  # Binds and requests exactly 1 physical GPU via native K8s scheduling
    train_task.set_memory_limit('8Gi')
    
    # Caching Policy configuration
    # By default, Kubeflow caches successful executions. If train_task encounters a runtime error, 
    # fixing the bug and re-triggering this execution will completely skip prep_task.

# Execution block to compile the pipeline code into declarative Kubernetes YAML manifests
if __name__ == "__main__":
    compiler.Compiler().compile(
        pipeline_func=research_pipeline, 
        package_path='research_pipeline.yaml'
    )
    print("Successfully compiled pipeline into 'research_pipeline.yaml'")
```

## Part 2: Monitoring, Logging & Live Feedback Loops

### 2.1 The Philosophy of Production Monitoring

Monitoring a live machine learning system requires tracking system uptime alongside model prediction quality. As real-world user habits shift over time, static models naturally experience performance degradation.

> _"If we can measure, then we can compare. And if we can compare, only then can we improve."_

An elite MLOps monitoring infrastructure focuses heavily on extracting **actionable business insights** rather than tracking resource uptime alone. An inference engine that maintains a flawless $0.00\text{ms}$ response latency but serves contextually irrelevant predictions damages business value.

### 2.2 The Three Dimensions of Monitoring Matrix

To prevent business degradation, teams must continuously track three core monitoring vectors:

```
                  ┌─────────────────────────────────────┐
                  │ 1. SERVICE DIMENSION (Infra)        │
                  │    - Prediction Latency             │
                  │    - Resource Utilization / Cost    │
                  └──────────────────┬──────────────────┘
                                     │
                  ┌──────────────────┴──────────────────┐
                  │ 2. DATA DIMENSION (Inputs/Outputs)   │
                  │    - Quality Checks / Missing Values │
                  │    - Feature & Target Drift         │
                  └──────────────────┬──────────────────┘
                                     │
                  ┌──────────────────┴──────────────────┐
                  │ 3. MODEL DIMENSION (Science/Logic)  │
                  │    - Real-Time / Delayed Actuals    │
                  │    - Downstream Proxy Measures      │
                  └─────────────────────────────────────┘
```

#### 1. Service Dimension (The Infrastructure)

- **Prediction Latency:** Spikes in request-response windows can indicate under-provisioned clusters or poorly optimized runtime inference graphs.
    
- **Performance Cliffs:** Sudden system breakdowns that occur under specific traffic loads or concurrent queue distributions.
    
- **Cost Efficiency:** Tracking whether allocated GPU/Memory resources map linearly to system throughput, avoiding expensive over-provisioning.
    

#### 2. Data Dimension (The Inputs & Outputs)

- **Schema & Quality Validation:** Catching corrupted strings, bad formatting, or unexpected missing values before they reach the model.
    
- **Data Drift:** Monitoring shifts in input data distributions relative to the original training baseline. This can be tracked by alerting when running summary statistics (e.g., mean, variance, or statistical distances like Population Stability Index) cross specific operational thresholds.
    
- **Concept Drift:** Changes in the relationships between input features and target predictions over time.
    

#### 3. Model Dimension (The Scientific Logic)

- **Real-time Actuals:** Instant feedback loops where ground truth is generated almost immediately (e.g., predicting delivery times versus actual transit durations).
    
- **Delayed Actuals:** Long-tail feedback loops where true labels take weeks or months to surface (e.g., credit risk modeling or long-term financial fraud tracking).
    
- **Proxy Measures:** Substring business tracking metrics utilized when true ground truth human labels are entirely missing or impossible to gather in real-time.
    

### 2.3 Anatomy of a "Silent Failure"

A **Silent Failure** occurs when a production system appears perfectly healthy on infrastructure dashboards but serves degraded predictions to users.

Consider an advanced **Text-to-Image generative model** deployed inside a Kubernetes cluster:

- **Inference Health Route:** `200 OK` (Healthy)
    
- **GPU Memory Footprint:** Stable at a safe `12GB VRAM` usage pattern
    
- **Inference Queue Latency:** Minimal; processing requests quickly
    

**The Production Breakdown:** Users report that the generated images look low-quality, repetitive, or "soulless." A specific text prompt like _"A sunset over Cairo"_ previously yielded highly artistic, detailed imagery. Today, that exact prompt yields distorted or low-fidelity visuals.

#### Root Cause 1: Prompt Drift (Input Space Degradation)

The distribution of user input strings has shifted significantly away from the data seen during training. Instead of simple inputs (_"A cat in a hat"_), users are supplying highly complex, lengthy strings filled with repetitive keywords, negative prompt styles, and weights. This pushes the inference request out toward the edge of the model's latent space, causing unstable image outputs.

#### Root Cause 2: Concept Drift (Output Space Degradation)

The real-world target definition of quality has transformed. The model was originally trained on data curated for illustrative artwork. However, user expectations have shifted toward hyper-realistic photography. The underlying reward function used during training no longer aligns with live user satisfaction metrics.

### 2.4 Designing a Production-Grade Closed-Loop System

To resolve silent failures automatically, we can build a resilient, automated self-healing feedback loop:

```
 ┌─────────────────────────────────────────────────────────────────┐
 │ STEP 1: AUTOMATED EVALUATION                                    │
 │ Deploys a sidecar container computing live CLIP scores.        │
 │ Triggers automated alert if the similarity index falls < 0.25.   │
 └───────────────────────────────┬─────────────────────────────────┘
                                 ▼
 ┌─────────────────────────────────────────────────────────────────┐
 │ STEP 2: HUMAN-IN-THE-LOOP (HITL) ORCHESTRATION                  │
 │ Routes low-confidence anomaly images to a dedicated curation UI. │
 │ Human labels generate a new "Gold Standard" training dataset.    │
 └───────────────────────────────┬─────────────────────────────────┘
                                 ▼
 ┌─────────────────────────────────────────────────────────────────┐
 │ STEP 3: AUTOMATED RE-TRAINING VIA KUBEFLOW                     │
 │ Reaching a 1,000-sample threshold triggers the KFP pipeline.    │
 │ Automatically fine-tunes and updates production models.         │
 └─────────────────────────────────────────────────────────────────┘
```

1. **Step 1: Automated Evaluation (The Monitor)** Deploy an independent sidecar container next to the inference engine. This sidecar calculates a live **CLIP Score** (Contrastive Language-Image Pre-training metric) for every transaction, measuring how well the generated image maps to the user's text prompt. If the running average similarity index falls below a threshold of $0.25$, the system triggers an operational alert.
    
2. **Step 2: Human-in-the-Loop Orchestration (HITL)** The system routes these low-confidence anomalies into an annotation UI. Human reviewers rate the outputs ($\text{Upvote}/\text{Downvote}$), establishing a high-quality **Gold Standard** dataset of challenging production examples.
    
3. **Step 3: Automated Re-training via Kubeflow** Once the curated evaluation dataset collects 1,000 new verified examples, an event trigger calls the compiled **Kubeflow Pipelines** workflow. The system automatically launches fine-tuning runs to adapt the model to new user preferences without requiring manual code changes.
    

## Part 3: The Complete MLOps Landscape

A mature MLOps architecture spans six progressive engineering layers:

```
┌───────────────────────────────────────────────────────────────────────────┐
│ 1. FOUNDATIONS                                                            │
│    Core principles: DevOps, Git versioning, Conda package isolation       │
├───────────────────────────────────────────────────────────────────────────┤
│ 2. REPRODUCIBILITY                                                        │
│    Artifact consistency: Docker containers, DVC data trackers, MLflow logs│
├───────────────────────────────────────────────────────────────────────────┤
│ 3. AUTOMATION                                                             │
│    Continuous workflows: CI/CD engines, GitHub Actions validation code     │
├───────────────────────────────────────────────────────────────────────────┤
│ 4. ORCHESTRATION                                                          │
│    Cluster management: Kubernetes platforms, Node groups, Pod resource spaces│
├───────────────────────────────────────────────────────────────────────────┤
│ 5. NETWORKING                                                             │
│    Traffic management: K8s Services, declarative Deployment manifests     │
├───────────────────────────────────────────────────────────────────────────┘
│ 6. OPERATIONS & FEEDBACK LOOPS                                            │
│    Production systems: Kubeflow Pipelines, real-time Drift monitors, Logs │
└───────────────────────────────────────────────────────────────────────────┘
```

- **The Software Architect Perspective (CI/CD):** Focuses on testing and deployment engineering. _"Is the source code validated? Does the target Docker Image build correctly without security vulnerabilities?"_ -> **Managed via GitHub Actions.**
    
- **The Research Scientist Perspective (MLOps):** Focuses on model performance and reproducibility. _"Is the model output accurate? Can we distribute training across local GPUs? Are the experiments scientific and reproducible?"_ -> **Managed via Kubeflow.**

[^1]: 

---

## Part 4: GitHub Actions & Workflows — MLOps Edition

### 4.1 Jobs, Machines, and Steps: How GitHub Workflows Execute in ML Pipelines

#### Jobs Run on Separate Machines (Runners)
In a GitHub Actions workflow, each **job** runs on its own fresh virtual machine (a runner). These machines are completely isolated from one another — they don't share a filesystem, environment variables, memory, or any state.

In an MLOps context, this is especially important because different stages of an ML pipeline have very different resource needs. Your training job might need a GPU runner, while your evaluation or deployment job can run on a cheap CPU machine. But that also means the trained model file produced on the GPU machine is invisible to the next job unless you explicitly pass it over.

```yaml
# ❌ THIS WILL FAIL
jobs:
  train:
    runs-on: gpu-runner          
    steps:
      - name: Train model
        run: python train.py     # expensive GPU machine, produces model.pkl

  evaluate:
    runs-on: ubuntu-latest       # ← brand new CPU machine, model.pkl doesn't exist here!
    steps:
      - name: Evaluate model
        run: python evaluate.py  # ❌ will fail — model.pkl was on the GPU machine
```

This is why artifacts exist. GitHub Actions provides `upload-artifact` and `download-artifact` actions to explicitly shuttle files between jobs through GitHub's storage layer.

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
        run: python evaluate.py  # ✅ model.pkl and metrics.json are now available

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

* **MLOps Tip:** For large model files (multi-GB checkpoints), GitHub artifact storage has size limits. In practice, teams push model artifacts to a model registry (MLflow, W&B, S3) during training and pull them by version in later jobs — using artifact storage only for lightweight metadata like metrics and configs.

#### Steps Run on the Same Machine — But in Separate Terminals
Within a single job, all **steps** run on the same machine sequentially. However, each step is executed in its own shell process — meaning the environment is not fully shared between steps.

* **The Key Implication:** Environment variables set with `export` in one step do NOT carry over to the next step.

In MLOps pipelines this commonly trips people up when, for example, a preprocessing step computes a dataset version hash or a split ratio and tries to pass it forward to the training step.

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
          # ❌ DATASET_VERSION is gone — this is a new shell
          python train.py --dataset-version $DATASET_VERSION
```

Each `run:` block spawns a new shell. When that shell exits, its environment dies with it.

The correct way to pass values between steps is via the `$GITHUB_ENV` file — a special file GitHub provides that persists environment variables across steps:

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

#### Summary: What Persists and What Doesn't

| Resource / Concept | Within a Job (Same Machine) | Across Jobs (Different Machines) |
|---|---|---|
| **Filesystem / Files** (e.g. `model.pkl`, datasets) | Shared | Need `upload`/`download-artifact` or a model registry |
| **`export VAR=...` env vars** (e.g. dataset version) | Dies with each step's shell | Does not cross jobs |
| **`$GITHUB_ENV` variables** (e.g. run ID, data hash) | Persists across steps | Dies with the machine; does not cross jobs |
| **`$GITHUB_OUTPUT` values** (e.g. accuracy, F1 score) | Accessible via `steps.<id>.outputs` | Does not cross jobs |
| **Installed packages / ML libraries** | Shared within the job | Must reinstall on each machine runner |
| **GPU / Hardware resources** | Same runner throughout job | Each job requests its own runner |

---

### 4.2 Environment Variable Scoping: Global, Job, and Step Level

GitHub Actions lets you define `env` variables at three levels. Each level controls how widely a variable is visible. Override priority (narrower scope wins):
$$\text{Step env} > \text{Job env} > \text{Global env}$$

#### Global Level — Visible to all jobs and all steps
```yaml
env:
  EXPERIMENT_NAME: churn-v2   # every job and step can read this

jobs:
  train:
    runs-on: ubuntu-latest
    steps:
      - run: echo $EXPERIMENT_NAME   # prints "churn-v2"
  deploy:
    runs-on: ubuntu-latest
    steps:
      - run: echo $EXPERIMENT_NAME   # prints "churn-v2"
```
Use this for things every stage needs: registry URLs, experiment names, Python version.

#### Job Level — Visible only to steps inside that job
```yaml
env:
  EXPERIMENT_NAME: churn-v2   # global

jobs:
  train:
    runs-on: ubuntu-latest
    env:
      BATCH_SIZE: "64"        # only the train job sees this
    steps:
      - run: echo $BATCH_SIZE        # prints "64"
      - run: echo $EXPERIMENT_NAME   # prints "churn-v2"
  deploy:
    runs-on: ubuntu-latest
    steps:
      - run: echo $BATCH_SIZE        # empty — BATCH_SIZE belongs to train
      - run: echo $EXPERIMENT_NAME   # prints "churn-v2"
```
Use this for hardware config (`CUDA_VISIBLE_DEVICES`), data paths, or anything specific to one stage.

#### Step Level — Visible only to that one step
```yaml
jobs:
  train:
    runs-on: ubuntu-latest
    steps:
      - name: Normal training
        run: echo $LOG_LEVEL         # empty, not set
      - name: Debug run
        env:
          LOG_LEVEL: DEBUG           # only this step sees it
        run: echo $LOG_LEVEL         # prints "DEBUG"
      - name: Back to normal
        run: echo $LOG_LEVEL         # empty again
```
Use this for one-off overrides like debug flags without affecting the rest of the pipeline.

#### Override Example — Step wins over Global
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

### 4.3 `if` Conditions: Controlling What Runs and When

`if` conditions can be placed at the **job level** or the **step level**. The three most important conditions are: `success()`, `failure()`, and `always()`.

#### Step Level `if`
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
        if: failure()           # runs only if train failed (e.g. notify is what makes it run specifically because train failed)
        run: echo "Training failed!"
      - name: Clean up temp files
        if: always()            # runs even if a previous step failed
        run: rm -rf /tmp/model_cache
```

#### Job Level `if` — Without `needs`
Without `needs`, all jobs start at the same time when the workflow triggers. A job-level `if` here is evaluated immediately at start — `success()` is always true since no upstream job has run yet, and `failure()` is always false. These conditions only become meaningful at the job level when combined with `needs`.

```yaml
# ❌ INCORRECT / MEANINGLESS CONDITIONALS WITHOUT NEEDS
jobs:
  train:
    runs-on: ubuntu-latest
    if: success()   # always runs — no upstream to fail
    steps:
      - run: python train.py
  evaluate:
    runs-on: ubuntu-latest
    if: failure()   # never runs — no upstream job could have failed yet
    steps:
      - run: python evaluate.py
```

#### Job Level `if` — With `needs`
When a job has `needs`, it waits for the upstream job to finish, then evaluates its `if` condition against the upstream results.

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
    if: success()   # runs only if train passed (Note: success() is the default — without any if, deploy would already be skipped if train failed)
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

### 4.4 Kubeflow Pipelines vs. GitHub Actions Workflows

Both tools let you define multi-step ML workflows, but they are built on fundamentally different models. GitHub Actions is a **general-purpose CI/CD runner**, whereas Kubeflow is a **dedicated ML orchestrator** built to manage compute resources, data, and pipeline state natively.

#### GitHub Actions: Just a Runner
GHA schedules and runs jobs on VMs. It has no awareness of ML concepts — it does not know what a model is, what a dataset is, or how much GPU memory a training job needs. You are responsible for installing dependencies, moving data around, and cleaning up.

Each job runs on a **fresh, isolated machine**. Nothing is shared between jobs by default — not files, not environment, not installed packages. You bridge this gap with artifacts or an external registry.

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

GHA does not provision GPUs for you — you either use a self-hosted runner with a GPU attached, or a third-party GPU runner. Once the job ends, the machine is gone.

#### Kubeflow: A Resource-Aware ML Orchestrator
Kubeflow Pipelines runs on Kubernetes. Each step in a pipeline is a container scheduled onto a node. Because it sits on top of Kubernetes, Kubeflow can:
- **Request specific resources per step**: e.g., CPUs, GPUs, memory limits. Kubernetes will automatically bin-pack these requests onto appropriate nodes.
- **Mount shared storage**: All steps in a pipeline share the same Persistent Volume (PV), so files written by one step are immediately readable by the next with no upload/download dance.
- **Cache step outputs**: If a step's inputs (code + parameters + input data) haven't changed since the last run, Kubeflow can skip re-running it and reuse the cached output automatically.

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

#### How Steps Communicate: Artifacts vs. Shared Volume

* **GitHub Actions** — each job is on a different machine, so you must explicitly package outputs and ship them:
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

* **Kubeflow** — steps communicate by writing to and reading from file paths on the shared volume. You define an output path for one step and pass it as the input path to the next:
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
  Kubeflow resolves the actual file path at runtime and mounts it correctly — you just declare the dependency and it handles the rest.

#### Step Caching in Kubeflow
Kubeflow has built-in step caching. If a step's inputs (code + parameters + input data) are identical to a previous run, Kubeflow skips the step and reuses the cached output. This is a major time-saver in MLOps iteration loops.

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
GitHub Actions has no equivalent native caching for step outputs — you can cache installed dependencies (`actions/cache`) but not the result of running your ML code. If you want to skip a training step because the data hasn't changed, you have to implement that logic yourself.

#### Side-by-Side Comparison

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

### 4.5 Why Replicas in Kubernetes but Not in Kubeflow

This is a question of **who the clients are** and **what the workload is doing**.

#### Replicas in Kubernetes: Serving a Model to Real Users
When you deploy a trained model as an inference service, real users or applications are sending requests to it — potentially thousands per second. The workload is:
- **Stateless**: Each request is independent, any replica can handle it.
- **Latency-sensitive**: Users are waiting for a response.
- **Unpredictably concurrent**: Traffic spikes need to be absorbed.

So you run multiple replicas of the same container behind a load balancer to ensure **high availability and high concurrency** for external clients. If one replica is busy, another handles the next request. If one crashes, the others keep serving.

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
Each replica is running the same code independently. Kubernetes keeps the desired count alive and restarts any that crash.

#### No Replicas in Kubeflow: No Clients, Just Computation
A Kubeflow pipeline step has no clients. Nothing is waiting for it to respond. It runs once, does its work (preprocessing, training, evaluation), writes its output, and exits. There is no reason to run three copies of a training step simultaneously — they would all produce the same model and overwrite each other.

What Kubeflow does instead is **distribute the work within a single step** using frameworks like PyTorch Distributed or TensorFlow's distributed strategy. Instead of duplicating the pipeline step, the step itself spawns multiple workers that each process a shard of the data cooperatively and synchronize gradients — producing one model faster.

```python
# Kubeflow step — distributed training, not replicas
@component(
    resources=ResourceSpec(
        accelerator=AcceleratorConfig(count=4)  # 4 GPUs for this one step
    )
)
def train(output_model_path: OutputPath(str)):
    import torch.distributed as dist
    # workers coordinate internally — one model comes out
    ...
```

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
One step, multiple internal workers, one output. The pipeline then moves on to the next step.

#### Core Distinction: Replicas vs. Distributed Steps

| Attribute | Kubernetes Replicas (Serving) | Kubeflow Distributed Step (Training) |
|---|---|---|
| **Why run multiple instances?** | Handle concurrent external requests | Process data faster in parallel |
| **Who calls them?** | Real users / applications | Nobody — self-contained computation |
| **Output** | Each replica responds independently | Workers cooperate to produce one result |
| **State** | Stateless — each request is isolated | Stateful — workers share/sync gradients |
| **Failure behavior** | Other replicas keep serving | Whole step typically restarts |
| **Scaling trigger** | Traffic load (concurrency) | Dataset size / model parameter size |

In short: replicas exist because external clients need availability and concurrency. Kubeflow steps have no external clients — they just need compute, which is handled by distributing the work internally rather than duplicating the step.

---

### 4.6 Continuous Delivery vs. Continuous Deployment

These two terms are often confused because they sound identical and share the same abbreviation (CD). The difference comes down to **where the pipeline stops** and **who triggers the final release**.

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

#### Continuous Delivery
The pipeline automatically builds, tests, and delivers the artifact to a staging environment — a production-like environment used for final validation. It stops there. A human reviews the result and manually decides when to promote it to production.

The model or code is always in a releasable state, but nothing goes live until someone says so.

In MLOps this looks like: a new model is trained, evaluated, and deployed to a staging endpoint automatically — but a data scientist reviews the metrics and shadow traffic results before manually promoting it to the live serving endpoint.

#### Continuous Deployment
Every step is automated end to end, all the way to production — the live environment real users interact with. If all quality gates pass, the artifact goes live automatically with no human in the loop.

In MLOps this looks like: a new model trains, hits the accuracy threshold, and is swapped into the live serving endpoint — all without anyone manually approving it.

#### Key Difference Summary

| Feature | Continuous Delivery | Continuous Deployment |
|---|---|---|
| **Pipeline stops at** | Staging / Pre-prod environment | Live Production environment |
| **Who triggers production?** | A human, manually | The pipeline, automatically |
| **Human involvement** | Required before going live | Only needed if something breaks |
| **Risk control** | Human judgment acts as the final gate | Relies entirely on automated quality gates |

* **Which to use in MLOps?** Most teams start with **Continuous Delivery** — ML models affect real decisions, and a human reviewing metrics before going live is worth the friction. **Continuous Deployment** makes sense once the automated evaluation suite is mature and trustworthy enough to catch regressions on its own.

[^2]: 
