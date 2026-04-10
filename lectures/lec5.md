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

# ML Engineering for Production <br> (DSAI 406)
## Lecture 5

Mohamed Ghalwash
<Email v="mghalwash@zewailcity.edu.eg" />

---
layout: fact
---

# Recording is NOT allowed 

---
layout: top-title
---

:: title :: 

# Recap

:: content :: 

- CI/CD
- Githib Actions 
- Anatomy of YAML 
```yaml
name: ...
on: ...

jobs:
  ID:
    runs-on: ...
    steps:
      - name: ...
        uses/run: ...
        with:
          param: ...
```

---
layout: top-title
---

:: title :: 

# The CI/CD Workflow: End-to-End MLOps Pipeline

:: content :: 

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
    needs: test_and_validate # why?
    runs-on: ubuntu-latest
    steps:
      ...
```


---
layout: top-title
---

:: title :: 

# Automated Testing for ML

:: content :: 

In MLOps, we move beyond simple syntax checks. We need **three levels** of testing to ensure both the code and the model are healthy:

<div class="grid grid-cols-1 gap-4">

| Test Type | What it checks | Example |
| :--- | :--- | :--- |
| **Unit Tests** | Individual code components | `test_preprocess_nulls()`: Does the scaler handle NaNs? |
| **Integration Tests** | Data + Model pipeline | `test_input_shape()`: Does the model accept the current data? |
| **Validation Tests** | Model "Behavioral" Performance | `assert accuracy > 0.80`: Is the model good enough to deploy? |

</div>

---
layout: top-title
---

:: title :: 

# Validation Testing 

:: content :: 


```python
# tests/test_model_logic.py

def test_prediction_range():
    model = load_model("models/latest.pkl") # hmmmm?
    prediction = model.predict(test_sample)
    # Ensure probabilities are always between 0 and 1
    assert prediction >= 0 and prediction <= 1 

def test_overfitting_check():
    # A simple test to ensure loss isn't exactly zero
    assert metrics['train_loss'] > 1e-5
```

---
layout: top-title
---

:: title :: 

# From Experiment to Production

:: content :: 

Once the PR is approved, the **CD Pipeline** takes over. But where are the pieces?

<div class="grid grid-cols-3 gap-6 pt-4">

<div class="p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
  <h4 class="font-bold mb-2">1. The Blueprint</h4>
  <p class="text-xs">The <b>Dockerfile</b> is in your Git repo. It defines the OS, Python version, and system dependencies.</p>
</div>

<div class="p-4 bg-purple-50 dark:bg-purple-900/20 rounded-lg">
  <h4 class="font-bold mb-2">2. The Brain</h4>
  <p class="text-xs">The <b>Model Weights</b> are pulled from <b>MLflow</b>. We use a script to find the <code>Best Model</code> or <code>Production</code> tag.</p>
</div>

<div class="p-4 bg-green-50 dark:bg-green-900/20 rounded-lg">
  <h4 class="font-bold mb-2">3. The Container</h4>
  <p class="text-xs">Docker builds the image, downloads the model inside it, and starts the API service.</p>
</div>

</div>


---
layout: section
---

# Use Cases 

---
layout: top-title # -two-cols
---

:: title :: 

# Step 1: Simple Trigger

:: content :: 

**The Goal**: Automatically train the model when code changes

<v-click>

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

</v-click>

</br></br>

<v-click>

<Admonition title="Issue" color='red-light'>
This is "blind" training. It runs the code, but we don't know if the model is actually better than the previous one, and we aren't saving the results anywhere
</Admonition>

</v-click>


---
layout: top-title
---

:: title :: 

# Step 2: Adding Observability

:: content :: 

**The Goal**: Log results using MLFlow  


<v-switch>
  <template #1> 

  ```yaml
  # ... 
  # (same as previous)
      steps:
        - uses: actions/checkout@v4
        - uses: actions/setup-python@v5
          with:
            python-version: '3.10'
        - run: pip install -r requirements.txt mlflow
        - name: Train and Log
          run: python train.py --epochs 1 # Validation Test
  ```  

  </template>

  <template #2-4> 

  ```yaml
  # ... 
  # (same as previous)
      steps:
        - uses: actions/checkout@v4
        - uses: actions/setup-python@v5
          with:
            python-version: '3.10'
        - run: pip install -r requirements.txt mlflow
        - name: Train and Log
          env:
            MLFLOW_TRACKING_URI: ${{ secrets.MLFLOW_TRACKING_URI }}
          run: python train.py 
  ```

  </template>

</v-switch>

</br></br>

<v-click at="3">

<Admonition title="Issue" color='red-light'>
Great, we are logging! But we are just "blindly" pushing code. What if the model in this push is worse than the one currently in production? We need to fetch the best model to compare or deploy
</Admonition>

</v-click>



---
layout: top-title # -two-cols
columns: is-2
---

:: title :: 

# Step 3: Fetching the Best Model

:: content :: 

**The Goal**: Finds the best model 

<v-click at="2">

```yaml
# ...
  steps:
    # ... (install steps)
    - name: Fetch Best Model
      env:
        MLFLOW_TRACKING_URI: ${{ secrets.MLFLOW_TRACKING_URI }}
      run: python get_best_model.py
```

</v-click>

<v-click at="3">

<Admonition title="Issue" color='red-light'>
 This YAML validates the model but does not build the docker image 
 </Admonition>

</v-click>


<v-click at="1">


<StickyNote color="white" title="get_best_model.py" v-drag="[560,160,400,280,20]">

```python
# Finds the best model and saves its URI to a file
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

</StickyNote>

</v-click>

---
layout: top-title
---

:: title :: 

# Step 4: Building Docker 

:: content :: 

<v-switch>
  <template #1> 

  ```yaml
  # ...
    steps:
      # ... (as previous steps)
      - name: Docker Login
        uses: docker/login-action@v3
        with:
          username: ${{ secrets.DOCKER_USERNAME }}
          password: ${{ secrets.DOCKER_PASSWORD }}

      - name: Build and Push Docker Image
        run: |
          MODEL_URI=$(cat best_model_uri.txt)
          docker build -t ${{ secrets.DOCKER_USERNAME }}/ml-app:latest .
          docker push ${{ secrets.DOCKER_USERNAME }}/ml-app:latest
  ```

  </template>

  <template #2-4> 

  ```yaml
  # ...
    steps:
      # ... (as previous steps)
      - name: Docker Login
        uses: docker/login-action@v3
        with:
          username: ${{ secrets.DOCKER_USERNAME }}
          password: ${{ secrets.DOCKER_PASSWORD }}

      - name: Build and Push Docker Image
        run: |
          MODEL_URI=$(cat best_model_uri.txt)
          docker build --build-arg MODEL_PATH=$MODEL_URI -t ${{ secrets.DOCKER_USERNAME }}/ml-app:latest .
          docker push ${{ secrets.DOCKER_USERNAME }}/ml-app:latest
  ```

  </template>

</v-switch>

<v-click at="3">

<Admonition title="Issue" color='red-light'>
This YAML is getting huge. We need to separate Validation from Deployment. 
</Admonition>

</v-click>

---
layout: top-title
---

:: title :: 

# Step 5: Separation of Concerns (Multi-Job)

:: content :: 

<v-click>

```yaml
jobs:
  validate: # CI
    runs-on: ubuntu-latest
    steps:
      - run: python train.py --smoke-test
  
  deploy: # CD 
    runs-on: ubuntu-latest
    steps:
      - run: docker build ...
```
</v-click>

<v-click>

<Admonition title="Issue" color='red-light'>
Parallelism! GitHub runs jobs in parallel by default. The deploy job will start before the validate job finishes. We might deploy a broken model! 
</Admonition>


</v-click>

---
layout: top-title
---

:: title :: 

# Step 6: The Final Pipeline (Dependencies)

:: content :: 

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
    needs: validate # <--- THE FIX: Wait for validation to pass 🟢
    runs-on: ubuntu-latest
    steps:
      - name: Fetch the best model
        run: python get_best_model.py
      - name: Build docker 
        run: |
          docker build --build-arg MODEL_PATH=$(cat best_model_uri.txt) -t app:latest .
          docker push app:latest
```

---
layout: top-title
---

:: title :: 

# Docker 

:: content ::

```dockerfile
  # 1. Start with a lightweight Python base
  FROM python:3.10-slim

  # 2. Define the Build Argument. This will be passed from your GitHub Action
  ARG MODEL_PATH

  # 3. Set environment variables
  ENV MODEL_DIR=/opt/ml/model

  # 4. Install system dependencies & libraries
  COPY requirements.txt .
  RUN apt-get update && apt-get install -y --no-install-recommends build-essential 
  RUN pip install --no-cache-dir -r requirements.txt

  # 5. Fetch the Model from MLflow during Build
  RUN mkdir -p ${MODEL_DIR}
  RUN mlflow artifacts download --artifact-uri ${MODEL_PATH} --dst-path ${MODEL_DIR}

  # 6. Copy your code
  WORKDIR /app
  COPY src/ ./

  # 7. Start your app
  CMD ["python", "main.py"]
```

---
layout: section
---

# Data Version Control (DVC)
### Git for Data

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

# Connecting the Dots: Docker + MLflow + CI

:: content :: 

Every tool we have learned so far—**Docker**, **DVC**, and **MLflow**—now converges into a single automated pipeline. This is where MLOps becomes a "system" rather than just a collection of scripts.

* 🐳 **Docker:** The CI Runner uses your **Dockerfile** to ensure the test environment perfectly matches your development environment. No "it worked on my machine."
* 📈 **MLflow:** The CI process logs the results of the "Test Run" to your tracking server. You can compare CI performance against your local manual experiments.
* 🗂️ **DVC:** The CI pipeline pulls the specific version of the data from remote storage to run validation tests.

<div class="mt-6 p-4 bg-blue-500 bg-opacity-10 border-l-4 border-blue-500">
  <strong>The Pipeline Workflow:</strong> 
  <br><code>Git Push</code> ➔ <code>Pull Data (DVC)</code> ➔ <code>Run Tests (Pytest)</code> ➔ <code>Log to MLflow</code> ➔ <code>Build Container</code> ➔ <code>Deployment Approval</code> 
</div>

---
layout: center
class: text-center
---

# Learn More

[Course Homepage](https://github.com/m-fakhry/DSAI-406-MLOps)
