---
theme: neversink
class: 'text-center'
transition: slide-left
title: MLOps (DSAI 406)
author: Mohamed Ghalwash
year: Spring 2025-2026
venue: Zewail City
mdc: true
lecture: 5
slide:
  disableSlideNumbers: true
slide_info: false
---


---
layout: top-title
---

:: title :: 

# Scaling & Self-Healing in Action

:: content ::

What happens when your PersonaCanvas store goes viral? Or when a container crashes?

- **Scaling Up (Horizontal Scaling)**
  You can increase the number of AI model instances instantly:
```bash
  kubectl scale deployment personacanvas-frontend --replicas=10
```

If you manually "kill" a pod to simulate a crash:
`kubectl delete pod <pod-name>` 

K8s notices the Actual State (2 pods) doesn't match the Desired State (3 pods) and starts a new one in seconds.


Updating your AI model to a new version without any downtime:
`kubectl set image deployment/frontend streamlit-app=new-ai-image:v2` 


---
layout: top-title
---

:: title :: 

# Steps

:: content ::

- `kubectl get node` to get all nodes in the cluster 
- `kubectl create deployment` deploy an app on the cluster (stateless app. for stateful use StateFulSet instead of deployment)
  - e.g. `kubectl create deployment my-app --image=gcr.io/google-samples/kubernetes-bootcamp:v1 --replicas=2`
    - searched for a suitable node where an instance of the application could be run
    - scheduled the application to run on that Node
    - configured the cluster to reschedule the instance on a new Node when needed
  - The instance is running inside a container on your node
- Or using YAML 
  ```yaml
  runs
  ```
  
  then `kubectl apply -f deployment.yaml`

- hybrid `... --dry-run=client -o yaml > deployment.yaml`
  
- Proxy or Service 
  - `kubectl proxy` to have a connection between the host (the terminal) and the Kubernetes cluster on port 8001
    - 
  
    ```
    export POD_NAME="$(kubectl get pods -o go-template --template '{{range .items}}{{.metadata.name}}{{"\n"}}{{end}}')"
    echo Name of the Pod: $POD_NAME
    ```
    - `kubectl get pods` to get all pods 
    - `kubectl describe pods` to get the Pod’s container information such as IP address and the ports
    - `kubectl exec -ti $POD_NAME -- bash` to open console on the container where we run our application

    - `http://localhost:8001/api/v1/namespaces/default/pods/$POD_NAME:8080/proxy/`
  - Service: 
    - `kubectl get services`
    - `kubectl expose deployment/my-app --type="NodePort" --port 8080` We have now a running Service called kubernetes-bootcamp
    - `kubectl describe services/my-app` to get the port 
    - 
    ```
    export NODE_PORT="$(kubectl get services/kubernetes-bootcamp -o go-template='{{(index .spec.ports 0).nodePort}}')"
    echo "NODE_PORT=$NODE_PORT"
    ```
    - `curl http://"$(minikube ip):$NODE_PORT"`

    - `kubectl describe deployment` see the name (the key) of the label for our Pod
    - `kubectl get pods -l app=kubernetes-bootcamp` to get the list of Pods
    - `kubectl get services -l app=kubernetes-bootcamp` to get the list of Services 
    - 
    ```
    export POD_NAME="$(kubectl get pods -o go-template --template '{{range .items}}{{.metadata.name}}{{"\n"}}{{end}}')"
    echo "Name of the Pod: $POD_NAME"
    ```
- Scaling: 
  - `kubectl scale deployments/kubernetes-bootcamp --replicas=4` scales the Deployment to 4 replicas
  - 

- 




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

[Nice Tutorial](https://www.youtube.com/watch?v=s_o8dwzRlu4&t=104s)


[How to remotely SSH (connect) Visual Studio Code to AWS EC2](https://www.youtube.com/watch?v=sQQjMnEkGjs&t=1s)


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
