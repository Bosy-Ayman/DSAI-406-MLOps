---
layout: center
title: References
---
References: 

- Chip Huyen, *Designing ML Systems*, Chapter 10.3

- [Nice Tutorial for Kubernetes](https://www.youtube.com/watch?v=s_o8dwzRlu4&t=104s)

- [How to remotely SSH (connect) Visual Studio Code to AWS EC2](https://www.youtube.com/watch?v=sQQjMnEkGjs&t=1s)


---
layout: top-title
---

:: title  :: 

# Evolution: From GHA to Kubeflow

:: content :: 

Can't we just use GitHub Actions (GHA) for everything? Yes, but...

| Feature | GHA-Centric (CI/CD) | Kubeflow-Centric (MLOps) |
| :--- | :--- | :--- |
| **Trigger** | Code Push | Data Event (File saved to cluster) |
| **Reproducibility** | Versioned Code + MLFlow | Lineage (Code + Data + Pod State) |
| **Compute** | External / Self-Hosted | Native K8s Scheduling (GPU sharing) |
| **Caching** | Re-runs everything | Step-level caching (Saves time/GPU) |

---
layout: top-title 
---

:: title :: 

# The Shift: From CI/CD to Orchestration

:: content :: 

| Feature | **GitHub Actions (CI/CD)** | **Kubeflow (ML Orchestrator)** |
| :--- | :--- | :--- |
| **Primary Goal** | Building & Testing | Managing the ML Factory |
| **Infrastructure** |  General Cloud VMs |  Inside the K8s Cluster |
| **Resource Logic** |  Assigns a whole VM |  Fine-grained Bin-Packing |
| **Scaling** |  Isolated VMs |  Multi-Node Training  |
| **Data Handling** |  Upload/Download |  Mounts Persistent Volumes (PV) |
| **State & Failure** |  Restarts from Step 1 | Step-Level Caching |
| **The "Wall"** | Network Latency (Slow) | Shared Storage (Instant) |


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
