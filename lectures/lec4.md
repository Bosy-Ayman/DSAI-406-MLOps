
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