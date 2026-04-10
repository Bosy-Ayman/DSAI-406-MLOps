---
theme: neversink
class: 'text-center'
transition: slide-left
title: MLOps (DSAI 406)
author: Mohamed Ghalwash
year: Spring 2025-2026
venue: Zewail City
mdc: true
lecture: 7
slide:
  disableSlideNumbers: true
slide_info: false
---

# ML Engineering for Production <br> (DSAI 406)
## Lecture 7

Mohamed Ghalwash
<Email v="mghalwash@zewailcity.edu.eg" />

---
layout: fact
---

# Recording is NOT allowed 

---
layout: cover
---

# Docker Storage

---
layout: two-cols
---

:: left :: 

# 1. Bind Mounts
**Host-Dependent.**
Maps a folder on your laptop/VM directly into the container.

* **Use Case:** Local development.
* **MLOps Risk:** If the folder path `/home/mohamed/data` doesn't exist on the Runner, the container crashes.

```bash
# Mounting a local folder
docker run -v /host/path:/container/path my-image
```

:: right   ::

# 2. Volumes
**Docker-Managed.**
Docker creates a managed space on the disk.

* **Use Case:** Production & DVC Caching.
* **Integrating with DVC:** * We use volumes to cache the `.dvc/cache`.
  * This prevents re-downloading 10GB of data every time the container restarts.
* **The Limit:** Volumes are local to the VM.

---
layout: cover
---

# Orchestration


---

# GHA: The Code-First Automator
### Strengths and Operational Limits

* **Primary Goal:** Code Integrity (Building, Testing, Pushing Images).
* **Trigger:** Git Events (Push, Pull Request).
* **The "Midterm" Workflow:**
  * Build a Docker Image.
  * Push to Registry.
  * Small scale training (<10GB) on a single Runner.

> **The Operational Wall:** GHA treats every job as an isolated "Clean Slate." It is a **Job Runner**, not a **Resource Scheduler**.

---

# The "Infrastructure Gap" 
### Why we are moving to Kubeflow

We have seen that:
1. **GHA Isolation:** Each job is a separate VM. (No easy data sharing).
2. **Docker Volumes:** Local to the VM. (If Job B starts on a *new* VM, the Volume is gone).

**The Question for Next Week:**
How do we get **Job B** to see the **Volume** created by **Job A** if they are on different physical machines?

**The Answer:** **Persistent Volume Claims (PVC)** and **Networked Storage** in Kubeflow.

---

# The Shift: From CI/CD to Orchestration
### Comparing the "Brain" of the System

| Feature | **GitHub Actions (CI/CD)** | **Kubeflow (ML Orchestrator)** |
| :--- | :--- | :--- |
| **Primary Goal** | **Code Integrity:** Building & Testing. | **Data Workflow:** Managing the ML Factory. |
| **Infrastructure** | **External:** General Cloud VMs. | **Native:** Inside the K8s Cluster. |
| **Resource Logic** | **Machine Labels:** Assigns a whole VM. | **Resource Requests:** Fine-grained Bin-Packing. |
| **Data Handling** | **Movement:** Upload/Download (Egress). | **Locality:** Mounts Persistent Volumes (PV). |
| **State & Failure** | **Linear:** Restarts from Step 1. | **Stateful:** Step-Level Caching. |
| **Scaling** | **Single Node:** Isolated VMs. | **Distributed:** Multi-Node Training (NCCL). |

---

# Final Comparison: GHA vs. Kubeflow

| Scenario | **GitHub Actions** | **Kubeflow (Orchestration)** |
| :--- | :--- | :--- |
| **Sharing a File** | Upload -> Download (Artifacts). | Both mount the same **Volume**. |
| **Sharing a Variable** | Needs `outputs` and `needs`. | Handled by the **Metadata Store**. |
| **The "Wall"** | Network Latency (Slow). | Shared Storage (Instant). |

**The Midterm Goal:** You learned how to build the "Bridge."
**The Post-Midterm Goal:** We will learn how to remove the "Wall" using a Cluster.


---
layout: section
---

# Scenario 1: The "Data Tax" Mystery
### Moving 500GB of Protein Sequences

---
layout: two-cols
---


:: left :: 

# GHA Logic (The "Mover")

In GHA, Job A and Job B are on different VMs. Data must be physically moved.

```yaml
# github-action.yaml
jobs:
  preprocess:
    runs-on: ubuntu-latest
    steps:
      - run: python clean.py --out data.zip
      - uses: actions/upload-artifact@v4
        with:
          path: data.zip # The "Tax" (Upload)

  train:
    needs: preprocess
    runs-on: ubuntu-latest-8-core
    steps:
      - uses: actions/download-artifact@v4 # The "Tax" (Download)
      - run: python train.py
```
:: right :: 

# Kubeflow Logic (The "Mount")

In Kubeflow, the data stays on the disk. The containers come to the data.

```yaml 
# kubeflow-dag.yaml
components:
  - name: preprocess
    container:
      image: my-cleaner:v1
      outputs: [data_path]
  - name: train
    container:
      image: my-trainer:v1
      inputs: [data_path]
```

# Operational Reality:
# Task B mounts the SAME Persistent 
# Volume (PV) Task A just wrote to.
# Zero Network Egress Cost.

Markdown
---
layout: section
---

# Scenario 2: The "OOM" & Resource Deadlock
### Forensic Case: High RAM vs. GPU Training

**The Incident:** You have one physical worker node with **64GB RAM** and **1 GPU**.
1. **Researcher A** starts a "Data Prep" job (Needs 60GB RAM, 0 GPU).
2. **Researcher B** starts a "Training" job (Needs 8GB RAM, 1 GPU).

---
layout: two-cols
---

:: left :: 

# The GHA Failure

**GHA sees a "Runner" is Online.**

GHA is a **Job Runner**, not a **Resource Scheduler**. It assumes the runner can handle the job if it's "Idle."

```yaml
# github-action.yaml
jobs:
  researcher_a:
    runs-on: [self-hosted, gpu-node]
    steps:
      - run: python heavy_prep.py # Uses 60GB

  researcher_b:
    runs-on: [self-hosted, gpu-node]
    steps:
      - run: python train.py # Uses 8GB
```

**Outcome**: The OS kills Job A because Job B pushed total RAM to **68GB**.

**System Crash (OOM)**.

:: right :: 

# The Kubeflow Success

Kubeflow checks the "Control Plane."

Kubeflow is Resource-Aware. It treats your cluster as a pool of Memory/CPU/GPU.

```yaml
# kubeflow-dag.yaml
- name: heavy-prep
  container:
    resources:
      requests:
        memory: "60Gi"
- name: train
  container:
    resources:
      requests:
        memory: "8Gi"
        [nvidia.com/gpu](https://nvidia.com/gpu): 1
```

# The Logic: 60 + 8 > 64. 
# Result: Kubeflow puts Job B in 
# "PENDING" state until Job A 
# releases the 60GB.

---
layout: section
---

# Scenario 3: The "Resume" Logic
### Why pay for the same work twice?

**The Incident:** Your Training container (Step 3 of 5) crashes at **Hour 4** because the Cloud Provider reclaimed the Spot Instance.

---
layout: two-cols
---

:: left :: 

# GitHub Actions (Linear)
**The "Restart" Problem.**

GHA is "all or nothing" per Job.

```yaml
# github-action.yaml
jobs:
  train:
    runs-on: ubuntu-latest
    strategy:
      # Only retries the WHOLE job
      max-parallel: 1 
    steps:
      - name: Fetch Data
        run: python get_data.py # 1 hr
      - name: Train
        run: python train.py # 4 hrs
```

**Outcome:** If `train.py` fails, GHA restarts the Job. You lose the 1-hour "Fetch Data" work every time.

:: right ::

# Kubeflow (Stateful)
**The "Memoization" Solution.**

Kubeflow treats every node as a **Stateful Entry**.

```yaml
# kubeflow-dag.yaml
- name: fetch-data
  container:
    image: fetcher:v1
  # DEFAULT: Enable Caching
  metadata:
    annotations:
      pipelines.kubeflow.org/cache_enabled: "true"

- name: train
  container:
    image: trainer:v1
  # If Train fails, it ONLY 
  # restarts the Train node.
```

**Outcome:** Kubeflow sees the `fetch-data` output in the Metadata Store. It **skips** the 1-hour fetch and goes straight to training.

---

# Summary: When to move to Kubeflow?

* **Caching:** When re-running early steps (Data Prep) is expensive or slow.
* **Data Locality:** When data is too large (>50GB) to "Upload/Download" between VMs.
* **Communication:** When you need **Distributed Training** (Runners talking to each other via NCCL/MPI).
* **Bin-Packing:** When you need to request specific CPUs/GPUs/RAM to ensure 100% hardware utilization.

---
layout: center
---

# Next Steps
### Exercise: Functional Decomposition 
### How to break your `midterm_script.py` into a Kubeflow DAG.

[Reference: Chip Huyen, *Designing ML Systems*, Chapter 10.3]
