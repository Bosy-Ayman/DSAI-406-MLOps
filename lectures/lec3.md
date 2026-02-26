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

# Assignment 2

:: content :: 

### Move your Lecture 1 project into a professional MLOps environment  

<br> 

1. **Environment (Docker):** Create a `Dockerfile` that builds your training environment.
2. **Efficiency (Caching):** Use the "Requirements-First" strategy to speed up builds.
3. **Data (DVC):** Version your dataset. Do **not** push the CSV to GitHub.
4. **The Handover:** Give your partner your `Dockerfile`, `.dvc` file, and `code`.

<div class="mt-8 bg-blue-500 bg-opacity-10 p-4 rounded border border-blue-500">
  <strong>Success Metric:</strong> Your partner runs <code>docker run</code> and gets your exact accuracy score without installing a single local library.
</div>

---

# 📋 The Student "Checklist"

Before you submit, ensure your folder structure looks like this:

```text
.
├── data/
│   ├── raw_data.csv.dvc     <-- Pointer for DVC
│   └── .gitignore           <-- Should ignore the actual .csv
├── src/
│   └── train.py             <-- Your ML logic
├── Dockerfile               <-- Your environment recipe
├── requirements.txt         <-- Your library versions
└── .dvc/                    <-- DVC configuration
```


---
layout: top-title
---

:: title :: 

# 💡 Tips

:: content :: 

## Hardcoded paths are the enemy of MLOps

- If your code says: `pd.read_csv('C:/Users/Professor/Desktop/data.csv')`, it will **fail** in Docker. 

- Use relative paths or environment variables: `pd.read_csv('./data/raw_data.csv')`

> **Remember:** A Docker container is a "Clean Room." It only knows what you explicitly put inside it.

---
layout: top-title
---

:: title :: 

# Coming Up: Lecture 3
### CI/CD: The "Ops" in MLOps

:: content ::

We have a **Container**. We have **Versioned Data**. 
Now, how do we automate the "Quality Control"?

* **Linting:** Automatically checking code style.
* **Unit Testing:** Ensuring the model doesn't crash on empty data.
* **GitHub Actions:** Building your Docker image on every `git push`.

<div class="flex justify-center mt-12">
  <div class="p-8 rounded-full bg-green-500 bg-opacity-10 animate-pulse">
    <carbon:cloud-service-management class="text-7xl text-green-500" />
  </div>
</div>

---
layout: center
class: text-center
---

# Questions?
## Time to go build.

<div class="mt-10 flex justify-center gap-4">
  <a href="https://docs.docker.com" target="_blank" class="px-4 py-2 rounded border border-white border-opacity-20 hover:bg-white hover:bg-opacity-10">Docker Docs</a>
  <a href="https://dvc.org" target="_blank" class="px-4 py-2 rounded border border-white border-opacity-20 hover:bg-white hover:bg-opacity-10">DVC Docs</a>
</div>

<div class="abs-br m-6 opacity-50">
  MLOps Course · Week 2
</div>



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
