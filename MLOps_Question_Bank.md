# 📝 DSAI-406 MLOps — Comprehensive Question Bank

> **Course:** ML Engineering for Production (DSAI 406)
> **Purpose:** Exam preparation covering all lectures, assignments, and midterm-style tricks
> **Total Questions:** 150+ (MCQ, True/False, Short Answer, Code Debugging, Scenario-Based)

---

## Table of Contents

- [Section A: Conceptual MCQs (40 Questions)](#section-a-conceptual-mcqs)
- [Section B: True or False (30 Questions)](#section-b-true-or-false)
- [Section C: Short Answer (25 Questions)](#section-c-short-answer)
- [Section D: Code & YAML Debugging (25 Questions)](#section-d-code--yaml-debugging)
- [Section E: Scenario-Based Analysis (15 Questions)](#section-e-scenario-based-analysis)
- [Section F: Mock Final Exam (15 Questions)](#section-f-mock-final-exam)
- [Answer Key](#answer-key)

---

## Section A: Conceptual MCQs

### Lecture 1 — Introduction

**Q1.** What is MLOps primarily about?
- (a) Building the most accurate ML model possible
- ==(b) Automation of ML workflows and shipping models to production==
- (c) Replacing DevOps with ML-specific tools
- (d) Data collection and labeling only

**Q2.** According to the "Hidden Technical Debt in ML Systems" paper (NeurIPS 2015), the ML code in a real-world ML system is:
- (a) The largest component
- (b) About half of the system
- ==(c) Only a small fraction of the entire system==
- (d) Not necessary once the model is trained

**Q3.** Which of the following is a **DataOps** task?
- (a) Deploying a binary/service
- ==(b) Data Versioning using DVC==
- (c) Unit and integration tests
- (d) Model Registry management

**Q4.** What distinguishes MLOps from DevOps?
- (a) MLOps doesn't require version control
- ==(b) MLOps adds data versioning, model registry, and data drift monitoring==
- (c) MLOps only focuses on deployment
- (d) DevOps is a subset of MLOps

**Q5.** Models in production can decay due to:
- (a) Code refactoring
- ==(b) Data drift==
- (c) Better hardware
- (d) Faster internet

---

### Lecture 2 — Reproducibility

**Q6.** Why should you never use your "Base" Python environment for an ML project?
- (a) It's slower than virtual environments
- ==(b) You lose the ability to reproduce your work when projects need different dependency versions==
- (c) Base environments can't install ML libraries
- (d) It violates Docker requirements

**Q7.** Which command exports a Conda environment to a YAML file?
- (a) `conda env export > requirements.txt`
- ==(b) `conda env export --no-builds > environment.yml`==
- (c) `pip freeze > environment.yml`
- (d) `conda save --env > environment.yml`

**Q8.** In a Dockerfile, what does `RUN` do?
- (a) Executes a command when the container starts
- ==(b) Executes a command at **build time** to create a new image layer==
- (c) Defines the entry point of the container
- (d) Copies files from host to container

**Q9.** Why should you copy `requirements.txt` BEFORE copying the rest of the code in a Dockerfile?
- (a) It's a Docker syntax requirement
- ==(b) To leverage **layer caching** — if code changes but dependencies don't, pip install is cached==
- (c) To make the image smaller
- (d) To avoid permission errors

==**Q10.**== Which Docker instruction runs at container **startup** time?
- (a) `RUN`
- (b) `COPY`
- ==(c) `CMD`==
- (d) `FROM`

---

### Lecture 3 — MLflow

**Q11.** Which are the **three pillars** of MLflow?
- ==(a) Tracking, Models, Registry==
- (b) Training, Testing, Deployment
- (c) Data, Code, Infrastructure
- (d) Logging, Monitoring, Alerting

**Q12.** What MLflow API call wraps an experiment run?
- (a) `mlflow.create_run()`
- ==(b) `mlflow.start_run()`==
- (c) `mlflow.init_experiment()`
- (d) `mlflow.begin()`

**Q13.** What is an MLflow **Artifact**?
- (a) A metric logged during training
- ==(b) Any file produced by your code that is stored with a specific run==
- (c) A Git commit hash
- (d) A Docker image

**Q14.** How does MLflow support collaboration?
- (a) Via email notifications
- ==(b) Through a **Client-Server** architecture with a shared tracking server==
- (c) By pushing to GitHub
- (d) Through Slack integration

**Q15.** What does `mlflow.pytorch.log_model(model, name="model")` do?
- (a) Saves the model to the local disk only
- ==(b) Logs the model artifact with its environment details to MLflow==
- (c) Uploads the model to Docker Hub
- (d) Registers the model for production deployment

---

### Lecture 4 — CI/CD

**Q16.** What is Continuous Integration (CI)?
- (a) Manually deploying code to production
- ==(b) Every `git push` triggers automated build and test==
- (c) Running code only on the main branch
- (d) Continuous monitoring of deployed models

**Q17.** In a GitHub Actions YAML file, the `on:` key specifies:
- (a) The operating system for the runner
- ==(b) The event(s) that trigger the workflow==
- (c) The list of steps to execute
- (d) The environment variables

==**Q18.**== Where must a GitHub Actions workflow YAML file be stored?
- (a) In the repository root
- ==(b) In `.github/workflows/`==
- (c) In `/actions/`
- (d) Anywhere in the repository

**Q19.** In GitHub Actions, the `needs:` keyword is used to:
- (a) Install dependencies
- ==(b) Define job **dependencies** (run after another job completes)==
- (c) Specify required secrets
- (d) List required artifacts

**Q20.** Which trigger should you use for your **Testing** YAML?
- (a) `push: branches: [main]`
- ==(b) `pull_request: branches: [main]`==
- (c) `workflow_dispatch`
- (d) `schedule`

---

### Lecture 5 — Advanced CI/CD & DVC

**Q21.** What are the three levels of automated testing in MLOps?
- (a) Syntax, Logic, Performance
- ==(b) Unit Tests, Integration Tests, Validation Tests==
- (c) Local, Staging, Production
- (d) Code, Data, Model

**Q22.** In the CI/CD pipeline, what does `get_best_model.py` do?
- (a) Trains a new model
- ==(b) Searches MLflow for the best model by accuracy and saves its URI==
- (c) Downloads a model from Docker Hub
- (d) Validates the model against test data

**Q23.** Why does DVC exist?
- (a) To replace Git for code versioning
- ==(b) Because Git is broken for large binary data files — it stores full copies and can't track data lineage==
- (c) To provide a graphical interface for Git
- (d) To speed up model training

**Q24.** What does a `.dvc` file contain?
- (a) The actual data
- (b) A compressed version of the data
- ==(c) A **pointer** (MD5 hash, size, path) to the actual data stored elsewhere==
- (d) Training logs

**Q25.** What command does a teammate run to fetch the actual data tracked by DVC?
- (a) `git pull`
- ==(b) `dvc pull`==
- (c) `dvc fetch`
- (d) `dvc download`

---

### Lecture 6 — Conditional Execution

**Q26.** In GitHub Actions, every step has a hidden default condition. What is it?
- (a) `if: always()`
- (b) `if: failure()`
- ==(c) `if: success()`==
- (d) `if: cancelled()`

**Q27.** What happens when you add a custom `if:` condition to a step WITHOUT including `success()`?
- (a) The step is skipped
- ==(b) The default "Stop on Failure" safety is **disabled** — the step becomes "status blind"==
- (c) The step runs twice
- (d) GitHub throws an error

**Q28.** How do you pass data between two **different Jobs** in GitHub Actions?
- (a) Using shared environment variables
- ==(b) Using `actions/upload-artifact` and `actions/download-artifact`==
- (c) Using local file system
- (d) Using Docker volumes

**Q29.** What does `if: failure()` do in a step?
- (a) Causes the step to always fail
- ==(b) Runs the step **only if** a previous step in the same job failed==
- (c) Marks the step as optional
- (d) Retries the failed step

**Q30.** In this YAML, what is the problem?
```yaml
steps:
  - run: echo "RUN_123" > id.txt
  - name: Train
    env:
      MLFLOW_URI: secrets.MLFLOW_URI
    run: python train.py
```
- (a) No issue
- ==(b) Secrets must use `${{ secrets.MLFLOW_URI }}` syntax==
- (c) The env block is in the wrong location
- (d) `echo` cannot write to files

---

### Lectures 7-8 — Kubernetes

**Q31.** What is the **smallest deployable unit** in Kubernetes?
- (a) Container
- ==(b) Pod==
- (c) Node
- (d) Service

**Q32.** Why do we need **Services** in Kubernetes?
- (a) To run containers
- ==(b) Because Pods are ephemeral and get new IPs when restarted — Services provide stable addresses==
- (c) To store data
- (d) To manage Docker images

**Q33.** What does the **Scheduler** in the K8s Control Plane do?
- (a) Stores the cluster state
- (b) Validates API requests
- ==(c) Matches Pods to the best available Node (based on CPU/GPU/RAM)==
- (d) Manages container images

**Q34.** What is the valid range for a `nodePort` in a Kubernetes Service?
- (a) 1-1024
- (b) 8000-9000
- ==(c) 30000-32767==
- (d) Any port number

**Q35.** What happens when a Pod exceeds its **memory limit** in K8s?
- (a) K8s throttles the memory usage
- ==(b) K8s **immediately kills** the process (OOM)==
- (c) K8s migrates the Pod to another Node
- (d) Nothing — it's just a suggestion

**Q36.** What happens when a Pod exceeds its **CPU limit** in K8s?
- (a) K8s kills the Pod
- ==(b) K8s **throttles** the CPU (slows down, but doesn't kill)==
- (c) K8s ignores it
- (d) K8s restarts the Pod

**Q37.** In a Deployment YAML, the `selector.matchLabels` must match:
- (a) The deployment name
- (b) The container image tag
- ==(c) The Pod template's `labels`==
- (d) The service port

**Q38.** What does this command do: `kubectl scale deployment backend --replicas=10`?
- (a) Creates 10 new deployments
- (b==) Scales the `backend` deployment to maintain 10 running Pod instances==
- (c) Limits the deployment to 10 nodes
- (d) Sets the memory limit to 10GB

---

### Lecture 9 — Kubeflow & Monitoring

**Q39.** Why is Kubeflow preferred over GHA for heavy AI workloads?
- (a) Kubeflow is free, GHA is paid
- ==(b) Kubeflow handles data locality, GPU scheduling, and step-level caching natively within the K8s cluster==
- (c) Kubeflow replaces Kubernetes
- (d) Kubeflow doesn't require Docker

**Q40.** What is a "Silent Failure" in production ML?
- (a) A system crash with no error logs
- ==(b) Infrastructure looks healthy but the model serves degraded predictions==
- (c) A Docker container that doesn't start
- (d) A CI pipeline that times out

---

## Section B: True or False

**Q41.** MLOps only applies to deep learning models. → **____false____**

**Q42.** In Docker, `CMD` is executed at build time. → **_____False___**

==**Q43.**== `RUN` creates a new layer in the Docker image. → **____True____**

**Q44.** In GitHub Actions, jobs run **sequentially** by default. → **____False____**  --> in parallel

**Q45.** In GitHub Actions, jobs run **in parallel** by default. → **___True_____**

**Q46.** Each Job in GHA runs on a **separate VM** with its own empty disk. → **____True____**

==**Q47.**== Local variables set in one Step persist to the next Step in the same Job. → **__False______**

**Q48.** DVC stores the actual data files inside the Git repository. → **______False__**

**Q49.** MLflow Tracking logs code, data, config, and results in one place. → **___True_____**

**Q50.** In Kubernetes, a Pod always has the same IP address throughout its lifecycle. → **____False____**

**Q51.** Kubernetes Services provide a stable/permanent IP address. → **____True____**

**Q52.** The `etcd` component in K8s stores the cluster's desired and current state. → **___True_____**

**Q53.** In K8s, if you exceed the CPU limit, the Pod gets killed. → **____False____**

**Q54.** In K8s, if you exceed the memory limit, the Pod gets killed. → **____True____**

**Q55.** Kubeflow provides step-level caching, meaning if Step 3 fails, Steps 1 and 2 don't need to re-run. → **___True_____**

**Q56.** Data Drift means the relationship between input features and target labels changes over time. → **_False_______** -->concept drift

**Q57.** Concept Drift means the input data distribution changes compared to training data. → **___False_____**

**Q58.** In Docker, copying `requirements.txt` first and then installing before copying the rest of the code is an optimization trick for layer caching. → **_True_______**

**Q59.** `pip freeze > requirements.txt` exports the current environment to a file. → **____True____**

**Q60.** In GitHub Actions, `${{ secrets.NAME }}` is the correct way to access secrets. → **____True____**

**Q61.** A Kubernetes Deployment ensures the desired number of Pod replicas are always running. → **____True____**

**Q62.** `kubectl` is the imperative way to interact with Kubernetes. → **_True_______**

**Q63.** Kubeflow replaces GitHub Actions entirely. → **___False_____**

**Q64.** The `branches-ignore` key in GHA triggers the workflow on all branches **except** the listed ones. → **___True_____**

==**Q65.**== Minikube runs a multi-node production K8s cluster. → **False_______**

**Q66.** TensorBoard is used for real-time monitoring of the training process (loss curves, histograms). → **___True_____**

**Q67.** Docker Compose orchestrates multiple containers with a single command. → **____True____**

**Q68.** In K8s, a Service with `type: NodePort` is accessible from outside the cluster. → **True______**

**Q69.** In a GitHub Actions YAML, the `always()` function ensures a step runs regardless of success or failure. → **___True_____**

**Q70.** DVC uses MD5 hashes to track data file versions. → **___True_____**

---

## Section C: Short Answer

**Q71.** List the six layers of the complete MLOps lifecycle as taught in the course.

**Q72.** Explain the difference between `RUN` and `CMD` in a Dockerfile. Give an example of each.

**Q73.** What is the difference between Data Drift and Concept Drift? Provide a real-world example for each.

**Q74.** Explain why Docker layer caching matters in MLOps and how to optimize Dockerfile ordering.

**Q75.** What is the "Hidden Technical Debt" paper about, and why is it relevant to MLOps?

**Q76.** Describe the three pillars of MLflow and what each one does.

**Q77.** In GitHub Actions, explain the difference between communication **within Steps** vs. **between Jobs**. How is data passed in each case?

**Q78.** What is the purpose of the `needs:` keyword in GitHub Actions? What happens if you don't use it?

**Q79.** Explain the Kubernetes self-healing mechanism. What happens when a Pod crashes?

**Q80.** What are the three dimensions of monitoring in production MLOps? List the key metrics for each.

**Q81.** Explain the closed-loop system for fixing "Silent Failures" in production (all 3 steps).

**Q82.** What is DVC and why can't Git handle large data files? What does a `.dvc` file contain?

**Q83.** Compare GHA and Kubeflow across at least 4 dimensions (data handling, caching, resources, trigger).

**Q84.** What are the key components of the Kubernetes Control Plane? Explain each.

**Q85.** In a K8s Service YAML, explain the difference between `port`, `targetPort`, and `nodePort`.

**Q86.** What is the difference between `requests` and `limits` in K8s resource specifications? What happens when each is exceeded?

**Q87.** Explain how GHA secrets work and why you should use `${{ secrets.NAME }}` instead of plain text.

**Q88.** What does `actions/checkout@v4` do in a workflow, and what happens if you forget it?

**Q89.** Describe the lifecycle of a K8s Deployment from YAML submission to running Pods (4 steps).

**Q90.** What is the purpose of `mlflow.set_experiment()` and `mlflow.start_run()` in an MLflow script?

**Q91.** What are Kubeflow's advantages for hyperparameter tuning over GHA?

**Q92.** Explain the traffic flow when a user accesses a Kubernetes app via NodePort.

**Q93.** What is a "Smoke Test" in CI/CD, and why is it used for model validation?

**Q94.** In the context of Docker, explain **Bind Mounts** vs. **Volumes**. When would you use each?

**Q95.** What does `conda env export --no-builds > environment.yml` do, and why use `--no-builds`?

---

## Section D: Code & YAML Debugging

**Q96.** Find and fix ALL bugs in this GitHub Actions YAML:
```yaml
jobs:
  train:
    runs-on: ubuntu-latest
    steps:
      - run: pip install -r requirements.txt
      - name: Checkout Code
      - name: Train
        env:
          MLFLOW_URI: secrets.MLFLOW_URI
        run: python train.py
      - uses docker build ml-app:latest .
```

**Answer**:

```yaml
jobs:
  train:
    runs-on: ubuntu-latest
    steps:
      - run: pip install -r requirements.txt
      - name: Checkout Code
      - name: Train
        env:
          MLFLOW_URI: ${{secrets.MLFLOW_URI}}
        run: python train.py
      - uses docker build ml-app:latest .
```

**Q97.** This Dockerfile is written the "slow way." Rewrite it for optimal layer caching:
```dockerfile
FROM python:3.9
COPY . /app
WORKDIR /app
RUN pip install -r requirements.txt
CMD ["python", "train.py"]
```

**Answer**:

```dockerfile
FROM python:3.9
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "train.py"]
```


**Q98.** What is wrong with this pipeline? The `deploy` job tries to read `model_id.txt` created by `train`, but the file is not found:
```yaml
jobs:
  train:
    runs-on: ubuntu-latest
    steps:
      - run: echo "RUN_12345" > model_id.txt

  deploy:
    needs: train
    runs-on: ubuntu-latest
    steps:
      - run: cat model_id.txt
```

**Answer**:

```yaml
jobs:
  train:
    runs-on: ubuntu-latest
    steps:
	    run: actions/download-artifact@v4
      - run: echo "RUN_12345" > model_id.txt
        path:
	        with:
	        

  deploy:
    needs: train
    run: actions/upload-artifact@v4
    runs-on: ubuntu-latest
    steps:
      - run: cat model_id.txt
```

**Q99.** This Dockerfile has a conceptual misunderstanding. What will happen?
```dockerfile
FROM python:3.10-slim
WORKDIR /app
RUN date > /app/build_time.txt
CMD ["cat", "/app/build_time.txt"]
```
Will the date shown be the build time or the run time? Explain.
of the build time not the run time, run excute at build time and the file become a permanent layer. cmd only reads it at runtime.
**Q100.** Find the issue with this conditional step:
```yaml
steps:
  - name: compile
    run: make build

  - name: test
    run: pytest tests/

  - name: publish
    if: github.ref == 'refs/heads/main'
    run: ./publish.sh
```

**Answer:**

```yaml
steps:
  - name: compile
    run: make build

  - name: test
    run: pytest tests/

  - name: publish
    if: sucess() && github.ref == 'refs/heads/main'
    run: ./publish.sh
```

**Q101.** Fix this K8s Deployment — the Service won't find the Pods:
```yaml
# deployment.yaml
spec:
  selector:
    matchLabels:
      app: web-frontend
  template:
    metadata:
      labels:
        app: web-app     # ← Is this correct?
---
# service.yaml
spec:
  selector:
    app: web-frontend
```

**Answer:**

```yaml
# deployment.yaml
spec:
  selector:
    matchLabels:
      app: web-frontend
  template:
    metadata:
      labels:
        app: web-frontend    # ← Is this correct?
---
# service.yaml
spec:
  selector:
    app: web-frontend
```

**Q102.** What's wrong with this MLflow code?
```python
mlflow.set_experiment("MyExperiment")
mlflow.log_params({"lr": 0.01, "epochs": 10})
mlflow.log_metric("accuracy", 0.95)
mlflow.pytorch.log_model(model, name="model")
```

**Answer:**

```python
with mlflow.start_run():
	mlflow.set_experiment("MyExperiment")
	mlflow.log_params({"lr": 0.01, "epochs": 10})
	mlflow.log_metric("accuracy", 0.95)
	mlflow.pytorch.log_model(model, name="model")
```

**Q103.** Fix this GitHub Actions YAML that has a multi-line indentation error:
```yaml
- name: Model Dry Test
  run: |
python -c "import torch; print('Ready!')"
```

**Answer:**
```yaml
- name: Model Dry Test
  run: |
	python -c "import torch; print('Ready!')"
```

==**Q104.**== What's wrong with this DVC-based CI pipeline step?
```yaml

- name: Pull Data
  run: dvc pull
```
(Hint: What step is missing before this?)

**Answer:**

```yaml
run: actions/checkout@v4
- name: Pull Data
  run: dvc pull
```


**Q105.** This Service YAML has an error. The app runs on port 8501 inside the container but the Service doesn't work:
```yaml
spec:
  type: NodePort
  selector:
    app: streamlit-web
  ports:
    - protocol: TCP
      port: 80
      targetPort: 80    # ← What's wrong?
      nodePort: 30085
```

**Answer:**
```yaml
spec:
  type: NodePort
  selector:
    app: streamlit-web
  ports:
    - protocol: TCP
      port: 80
      targetPort: 89501   # ← What's wrong?
      nodePort: 30085
```

**Q106.** Identify the security issue in this workflow step:
```yaml
- name: Docker Login
  run: docker login -u "admin" -p "SuperSecret123" 
```

**Answer:**

```yaml
- name: Docker Login
  run: docker login -u ${{secrets.DOCKER_USERNAME}} -p {{secrets.DOCKER_PASSWORD}}
```

**Q107.** What happens when you run this pipeline?
```yaml
jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - run: python train.py --smoke-test

  deploy:
    runs-on: ubuntu-latest
    steps:
      - run: docker build -t app:latest .
```
(What is missing from the `deploy` job?)

```yaml
jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - run: python train.py --smoke-test

  deploy:
	needs: validate
    runs-on: ubuntu-latest
    steps:
      - run: docker build -t app:latest .
```


**Q108.** Fix this Dockerfile that accepts a model path:
```dockerfile
FROM python:3.10-slim
MODEL_PATH=/opt/model        
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "serve.py"]
```
(Hint: How do you define build-time arguments vs. runtime environment variables?)

Answer:

```dockerfile
FROM python:3.10-slim
ARG MODEL_PATH
ENV MODEL_PATH=/opt/model        
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "serve.py"]
```

**Q109.** This Kubeflow component is incorrect. What's the issue?
```python
@dsl.component(base_image='python:3.9')
def preprocess(data_path: str):
    cleaned = clean(data_path)
    return cleaned   # ← Problem?
```

**Answer:**


**Q110.** What is the issue with this Kubernetes command for scaling?
```bash
kubectl scale pod my-pod --replicas=5
```

Answer:

```bash
kubectl scale deployment my-deployment --replicas=5
```

**Q111.** Fix this GitHub Actions workflow. The linter step is empty:
```yaml
- name: Linter Check
```

Answer:

```yaml
- name: Linter Check
  run:| 
	  pip install flake8
	  flake8 .
```

**Q112.** This YAML deploys but the gateway never becomes accessible. Why?
```yaml
kind: Deployment
metadata:
  name: my-app
spec:
  replicas: 3
  selector:
    matchLabels:
      app: my-app
  template:
    metadata:
      labels:
        app: my-app
    spec:
      containers:
      - name: web
        image: my-image:latest
        ports:
        - containerPort: 5000
```
(Hint: What Kubernetes resource is missing entirely?)

**Answer:** Missing service yaml . the deployment creates Pods but there is no service to expose them.


**Q113.** What's wrong with this `if` condition?
```yaml
train:
  runs-on: ubuntu-latest
  if: >
    github.ref_name == 'main' &&
    contains(github.event.head_commit.message, '[run-train]')
```
(Hint: What check is missing for cost protection?)

**Answer:**  

```yaml
train:
  runs-on: ubuntu-latest
  needs: lint
  if: >
    github.ref_name == 'main' &&
    contains(github.event.head_commit.message, '[run-train]')
```

to avoid running expensive training on broken code

**Q114.** Fix the secret access in this step:
```yaml
- name: Train
  env:
    MLFLOW_URI: {{ secrets.MLFLOW_URI }}
  run: python train.py
```

**Answer:**  

```yaml
- name: Train
  env:
    MLFLOW_URI: ${{ secrets.MLFLOW_URI }}
  run: python train.py
```


**Q115.** This Docker command maps a directory but it won't work on a CI runner. Why?
```bash
docker run -v /home/mohamed/data:/app/data my-image
```

**Answer:**  
because it is host independent  and won't exist on CI runner. Use Docker volumes or download data in the pipeline


**Q116.** What's wrong with setting an env variable in one step and reading it in the next?
```yaml
steps:
  - name: Set Version
    run: VERSION="v1.2.3"
  - name: Tag Model
    run: echo "Tagging model as $VERSION"
```

**Answer:

```yaml

```

**Q117.** What is wrong with this K8s service definition?
```yaml
spec:
  type: NodePort
  selector:
    app: streamlit-web
  ports:
    - port: 80
      targetPort: 8501
      nodePort: 25000    # ← Problem?
```

**Answer:
Must be  between 30000- 32767 

```yaml
spec:
  type: NodePort
  selector:
    app: streamlit-web
  ports:
    - port: 80
      targetPort: 8501
      nodePort: 30000  # ← Problem?
```

**Q118.** Fix this pipeline to implement proper failure handling:
```yaml
steps:
  - name: Heavy Training
    run: python train.py   # might fail

  - name: Upload Logs
    uses: actions/upload-artifact@v4
    with:
      name: crash-report
      path: logs/
```
(What condition should the Upload Logs step have?)
**Answer:
add if failure()

```yaml
steps:
  - name: Heavy Training
    run: python train.py   # might fail
	
  - name: Upload Logs
    if: failure()
    uses: actions/upload-artifact@v4
    with:
      name: crash-report
      path: logs/
```

**Q119.** What will happen when this Kubeflow pipeline re-runs after a failure in `train_model`?
```python
@dsl.pipeline(name="my-pipeline")
def pipeline():
    prep = preprocess_data(data_path="s3://data/v1")  # Takes 2 hours
    train = train_model(data=prep.outputs['cleaned'], lr=0.01)  # Failed!
```

**Answer:**

```python
@dsl.pipeline(name="my-pipeline")
def pipeline():
    prep = preprocess_data(data_path="s3://data/v1")  # Takes 2 hours
    train = train_model(data=prep.outputs['cleaned'], lr=0.01)  # Failed!
```

**Q120.** What's the conceptual error in this Dockerfile?
```dockerfile
FROM python:3.9
COPY requirements.txt .
COPY . .
RUN pip install -r requirements.txt
CMD ["python", "app.py"]
```

**Answer:**
run pip install means any code change invalidates the pip install cache, should copy requirements first, install, then copy code

```dockerfile
FROM python:3.9

COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .

CMD ["python", "app.py"]
```

---

## Section E: Scenario-Based Analysis

**Q121.** You deploy a text-to-image model. K8s metrics show 200 OK, stable GPU, low latency. But users say the images look "soulless." What two types of drift could explain this? How would you design a monitoring system to detect and fix this?
<details>
<summary>Answer</summary>
 prompt drift + concept drift


**Q122.** Researcher A submits a 60GB RAM job. Researcher B submits an 8GB RAM + 1 GPU job. The server has 64GB RAM total. Compare what happens with:
(a) GitHub Actions self-hosted runner
(b) Kubeflow pipelines

<details>
<summary>Answer</summary>
(a) it will stop working because both jobs start simultianeously -->OOM kills one (68>64 GB)
(b) Queue Job B in pending until job A finishes, ensuring safe execution


**Q123.** Your CI pipeline has 5 steps: Checkout → Install → Lint → Train (4 hours) → Deploy. The training fails at hour 3. You re-run the pipeline. What happens with:
(a) GitHub Actions
(b) Kubeflow Pipelines
Which is more cost-effective and why?

<details>
<summary>Answer</summary>
(a)  it will rerun from the beginning ( the entire pipeline restart)
(b) it will run from step 3 (train)

**Q124.** A team of 5 data scientists is training models simultaneously. They all use different hyperparameters. Design a system using MLflow, Docker, and GitHub Actions that allows them to:
- Track all experiments centrally
- Compare results
- Deploy only the best model

<details>
<summary>Answer</summary>
shared MLflow for all experiments, each scientist trains with different params logged to MLFlow, CI pipeline with get_best_model.py finds top model. CD build docker with best model URI

**Q125.** You have a Kubernetes cluster with 3 worker nodes. You deploy a model with `replicas: 5`. One worker node goes down. What happens to the Pods on that node? Describe the K8s self-healing mechanism step by step.

<details>
<summary>Answer</summary>
the desired number of pods are 5 (default 1 pod per node) , it will create 3 pods and it will assign them to the 2 remaining nodes

**Q126.** Design a complete CI/CD pipeline (YAML structure) for a medical AI model that:
- Only trains on `main` branch with `[train]` in commit message
- Logs to MLflow
- Checks accuracy > 0.90
- Builds Docker only if threshold passes
- Uploads failure logs on failure
- Always cleans up cloud resources

<details>
<summary>Answer</summary>

**Q127.** Explain why you would use DVC in addition to Git for an ML project with a 5GB training dataset, 200MB model weights, and 500 lines of Python code. Which files go in Git vs. DVC?
<details>
<summary>Answer</summary>

**Q128.** Your PersonaCanvas app has a Streamlit frontend and an AI backend. Both are deployed in K8s. The frontend needs to call the backend API. Design the networking using K8s Services. Which service type do you use for each and why?

**Q129.** You want to implement a "Gatekeeper" logic in your CI/CD pipeline:
- Lint must pass first
- Training only on `main` branch
- Only when commit message contains `[run-train]`
- Upload failure logs if training fails
- Always print cleanup message
Write the YAML structure with proper conditionals.

**Q130.** A model's accuracy drops from 95% to 78% over 3 months. Infrastructure metrics are perfect. Describe what monitoring dimensions you would check, what types of drift you'd investigate, and how you'd implement a closed-loop system to fix it.

**Q131.** You have two YAML approaches for your pipeline: a single workflow with conditional jobs, or two separate workflows. Compare the pros and cons of each approach.

**Q132.** Your training pipeline has 3 stages: Data Prep (1hr), Feature Engineering (30min), Training (6hrs). If training fails, you don't want to redo the first two steps. Compare how GHA and Kubeflow handle this.

**Q133.** Design a K8s deployment for a system with:
- 3 replicas of a web frontend (256MB RAM, 0.25 CPU)
- 1 replica of an AI backend (4GB RAM, 2 CPU, 1 GPU)
- A NodePort service for the frontend
- An internal (ClusterIP) service for the backend

**Q134.** Explain the complete flow when `kubectl apply -f deployment.yaml` is executed, tracing through API Server → etcd → Controller Manager → Scheduler → Kubelet.

**Q135.** A junior engineer writes this Dockerfile and the image is 4GB. Suggest at least 3 optimizations:
```dockerfile
FROM python:3.9
RUN apt-get update && apt-get install -y vim curl wget git
COPY . /app
WORKDIR /app
RUN pip install tensorflow pytorch scikit-learn pandas numpy
CMD ["python", "train.py"]
```

---

## Section F: Mock Final Exam

> **Instructions:** Answer all questions. Time: 2 hours.

**Q136. (5 pts)** Define MLOps and explain how it differs from DevOps and DataOps. What additional concerns does MLOps address?

**Q137. (8 pts)** Given this broken YAML, find and fix ALL errors (minimum 5 bugs). Explain each fix:

```yaml
name: ML Pipeline
on:
  push:
    branches: main
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
        - name: Setup Python
            uses: actions/setup-python@v5
            with:
                python-version: '3.10'
        - name: Install
            run: pip install -r requirements.txt
        - name: Linter
        - name: Train
            run: |
            python train.py
  deploy:
    steps:
      - run: docker build -t app .
```
Answer:

```yaml
name: ML Pipeline
on:
  push:
    branches: [main]
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
        - name: Setup Python
            uses: actions/setup-python@v5
            with:
                python-version: '3.10'
        - name: Install
          run: pip install -r requirements.txt
        - name: Linter
        - run:: | pip install linter
	           flake8 .
        - name: Train
            run: |
            python train.py
  deploy:
	 needs: build
    steps:
      - run: docker build -t app .
```

**Q138. (6 pts)** Explain Docker layer caching. Draw or describe the optimal Dockerfile structure for an ML application and explain why each instruction is ordered as it is.

**Q139. (8 pts)** Write a complete GitHub Actions YAML for a two-job pipeline:
- **Job 1 (validate):** Checkout, setup Python 3.10, install deps, run `train.py`, save `model_info.txt` as artifact
- **Job 2 (deploy):** Depends on Job 1, downloads artifact, reads model ID, mocks Docker build

**Q140. (6 pts)** Explain the three types of automated testing in MLOps (Unit, Integration, Validation). Give a concrete example for each.

**Q141. (5 pts)** Compare `success()`, `failure()`, `always()`, and `cancelled()` in GitHub Actions. Give a use case for each. What is the critical warning about custom `if:` conditions?

**Q142. (6 pts)** Draw or describe the Kubernetes cluster architecture. Label: Control Plane (API Server, etcd, Scheduler, Controller Manager), Worker Nodes, Pods, Services.

**Q143. (8 pts)** Write a complete Kubernetes Deployment YAML for an AI backend with:
- 2 replicas
- Image: `myrepo/ai-model:v2`
- Container port: 5000
- Request: 2GB RAM, 1 CPU, 1 GPU
- Limit: 4GB RAM, 2 CPU, 1 GPU

**Q144. (5 pts)** Explain the difference between `port`, `targetPort`, and `nodePort` in a K8s Service. Trace the traffic flow when a user accesses the app.

**Q145. (8 pts)** Compare GitHub Actions and Kubeflow across these dimensions:
- Data Handling
- Caching/Failure Recovery
- Resource Management
- When to use each

**Q146. (6 pts)** Define Data Drift, Concept Drift, and Silent Failure. Explain the 3-step closed-loop system for handling drift in production.

**Q147. (5 pts)** Explain what DVC is, how it works (the `.dvc` pointer concept), and why Git alone is insufficient for ML data management.

**Q148. (4 pts)** Write the MLflow code to: create an experiment, start a run, log 3 parameters, log accuracy per epoch, and save a PyTorch model.

**Q149. (5 pts)** Given a Kubeflow pipeline with a 2-hour preprocessing step and a 6-hour training step, explain what happens if:
(a) Training fails on the first run
(b) You fix the bug and re-run the pipeline
How does Kubeflow's caching mechanism save time?

**Q150. (5 pts)** Explain the full MLOps pipeline workflow end-to-end:
`Git Push → ? → ? → ? → ? → Deployment`
Fill in all intermediate steps and explain each.

---

## Answer Key

### Section A — MCQs

| Q | Answer | Explanation |
|---|--------|-------------|
| 1 | **(b)** | MLOps = Automation + Shipping |
| 2 | **(c)** | The ML code is a small fraction; most is infrastructure |
| 3 | **(b)** | DVC versioning is a DataOps task |
| 4 | **(b)** | MLOps adds data versioning, model registry, drift monitoring |
| 5 | **(b)** | Data drift causes model decay in production |
| 6 | **(b)** | Isolation prevents version conflicts between projects |
| 7 | **(b)** | `conda env export --no-builds > environment.yml` |
| 8 | **(b)** | `RUN` executes at build time, creating image layers |
| 9 | **(b)** | Layer caching — pip install is cached if requirements unchanged |
| 10 | **(c)** | `CMD` runs when the container starts |
| 11 | **(a)** | Tracking, Models, Registry |
| 12 | **(b)** | `mlflow.start_run()` is the correct API call (used with `with`) |
| 13 | **(b)** | Any file (models, plots, configs) stored with a run |
| 14 | **(b)** | Client-Server architecture with shared tracking server |
| 15 | **(b)** | Logs model artifact + environment details to MLflow |
| 16 | **(b)** | Every push triggers automated build & test |
| 17 | **(b)** | The event(s) that trigger the workflow |
| 18 | **(b)** | `.github/workflows/` |
| 19 | **(b)** | Defines job dependencies |
| 20 | **(b)** | `pull_request: branches: [main]` for testing |
| 21 | **(b)** | Unit, Integration, Validation |
| 22 | **(b)** | Searches MLflow for best model by accuracy, saves URI |
| 23 | **(b)** | Git can't handle large binaries (full copies, no lineage) |
| 24 | **(c)** | Pointer with MD5 hash, size, and path |
| 25 | **(b)** | `dvc pull` fetches actual data |
| 26 | **(c)** | Every step has a hidden `if: success()` |
| 27 | **(b)** | The default "Stop on Failure" is disabled |
| 28 | **(b)** | Upload/download artifacts |
| 29 | **(b)** | Runs only if a previous step failed |
| 30 | **(b)** | Must use `${{ secrets.MLFLOW_URI }}` |
| 31 | **(b)** | Pod is the smallest unit |
| 32 | **(b)** | Pods are ephemeral with changing IPs; Services are stable |
| 33 | **(c)** | Matches Pods to best available Node |
| 34 | **(c)** | 30000-32767 |
| 35 | **(b)** | Memory limit exceeded → OOM kill |
| 36 | **(b)** | CPU limit exceeded → throttled |
| 37 | **(c)** | Must match Pod template labels |
| 38 | **(b)** | Scales to maintain 10 Pod instances |
| 39 | **(b)** | Data locality, GPU scheduling, step-level caching |
| 40 | **(b)** | Infra looks healthy but predictions are degraded |

### Section B — True/False

| Q | Answer | Explanation |
|---|--------|-------------|
| 41 | **False** | MLOps applies to ALL ML models, not just deep learning |
| 42 | **False** | `CMD` runs at **runtime** (when container starts) |
| 43 | **True** | Each `RUN` creates a cacheable image layer |
| 44 | **False** | Jobs run in **parallel** by default |
| 45 | **True** | Jobs run in parallel unless `needs:` is specified |
| 46 | **True** | Each job = separate VM, empty disk |
| 47 | **False** | Each step = separate shell; local variables die |
| 48 | **False** | DVC stores **pointers** in Git; data is in external storage |
| 49 | **True** | MLflow Tracking centralizes experiment data |
| 50 | **False** | Pods are ephemeral and get new IPs when restarted |
| 51 | **True** | Services provide permanent Virtual IPs |
| 52 | **True** | etcd is the cluster's source of truth |
| 53 | **False** | CPU excess → **throttled**, not killed |
| 54 | **True** | Memory excess → immediately **killed** (OOM) |
| 55 | **True** | Kubeflow provides step-level caching |
| 56 | **False** | That's **Concept Drift**. Data Drift = input distribution changes |
| 57 | **False** | That's **Data Drift**. Concept Drift = relationship between I/O changes |
| 58 | **True** | This is the "MLOps Way" for Dockerfile ordering |
| 59 | **True** | `pip freeze` exports packages to requirements.txt |
| 60 | **True** | `${{ secrets.NAME }}` is the correct syntax |
| 61 | **True** | Deployments maintain desired replica count |
| 62 | **True** | `kubectl` commands = imperative approach |
| 63 | **False** | They complement each other: GHA for CI, Kubeflow for MLOps |
| 64 | **True** | `branches-ignore` excludes the listed branches |
| 65 | **False** | Minikube runs a **single-node** local cluster |
| 66 | **True** | TensorBoard shows real-time training process data |
| 67 | **True** | Docker Compose orchestrates multi-container apps |
| 68 | **True** | NodePort makes services accessible externally |
| 69 | **True** | `always()` runs regardless of outcome |
| 70 | **True** | DVC uses MD5 hashes in `.dvc` pointer files |

### Section C — Short Answer (Key Points)

**Q71.** The six layers: (1) Foundations (DevOps, Git, Conda), (2) Reproducibility (Docker, DVC, MLflow), (3) Automation (CI/CD, GitHub Actions), (4) Orchestration (K8s, Nodes, Pods), (5) Networking (Services, Deployments), (6) Operations & Feedback (Kubeflow, Monitoring, Logging)

**Q72.** `RUN` executes at **build time** to create layers (e.g., `RUN pip install -r requirements.txt`). `CMD` executes at **runtime** when the container starts (e.g., `CMD ["python", "app.py"]`).

**Q73.** **Data Drift:** Input distribution changes (e.g., users switch from simple to complex prompts). **Concept Drift:** The relationship between inputs and outputs changes (e.g., model trained for "art" but users now expect "photos").

**Q74.** Docker caches layers. If `requirements.txt` is copied and installed first, code changes don't trigger re-installation. Order: `FROM` → `WORKDIR` → `COPY requirements.txt` → `RUN pip install` → `COPY . .`

**Q75.** Google's paper showing ML code is a tiny part of the system. The rest is infrastructure (data pipelines, serving, monitoring). MLOps addresses this by automating the surrounding infrastructure.

**Q76.** (1) **Tracking:** Log experiments, metrics, params. (2) **Models:** Standard packaging format ("Flavors"). (3) **Registry:** Lifecycle management (Staging → Production).

**Q77.** **Within Steps:** `env` variables or local files. **Between Jobs:** `actions/upload-artifact` and `actions/download-artifact` because each job runs on a **separate VM**.

**Q78.** `needs:` makes a job wait for another to complete. Without it, jobs run **in parallel**, potentially deploying a broken model before validation.

**Q79.** If a Pod crashes, the Controller Manager detects the gap between current state and desired state, creates new Pod definitions, and the Scheduler assigns them to available nodes.

**Q80.** (1) **Service:** Latency, performance cliffs, cost. (2) **Data:** Quality checks, data drift, concept drift. (3) **Model:** Real-time actuals, delayed actuals, proxy measures.

### Section D — Code Debugging (Key Fixes)

**Q96.** Bugs: (1) Missing `actions/checkout@v4` at beginning, (2) Checkout step has no `uses:`, (3) Secret syntax wrong: `${{ secrets.MLFLOW_URI }}`, (4) `uses` syntax wrong: should be `run: docker build ...` not `uses docker build ...`, (5) Steps ordering — checkout should be first.

**Q97.** Optimized:
```dockerfile
FROM python:3.9
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "train.py"]
```

**Q98.** Jobs run on **separate VMs**. Use `actions/upload-artifact@v4` in `train` and `actions/download-artifact@v4` in `deploy`.

**Q99.** The date shown is the **build time**, NOT the run time. `RUN` executes at build time and the file becomes a permanent layer. `CMD` only reads it at runtime.

**Q100.** The `publish` step will run even if `compile` or `test` fails because the custom `if:` overrides the hidden `success()`. Fix: `if: success() && github.ref == 'refs/heads/main'`

**Q101.** Labels mismatch! Deployment template has `app: web-app` but selector has `app: web-frontend`. Service looks for `app: web-frontend`. Fix: Template labels must match selector: `app: web-frontend`.

**Q102.** Missing `with mlflow.start_run():` wrapper. All logging should be inside the run context.

**Q103.** The Python command must be **indented** under `run: |`:
```yaml
- name: Model Dry Test
  run: |
    python -c "import torch; print('Ready!')"
```

**Q104.** Missing `actions/checkout@v4` before `dvc pull`. DVC needs the repo code (including `.dvc` files) to know what to pull.

**Q105.** `targetPort: 80` should be `targetPort: 8501` (the port the container is listening on).

**Q106.** Credentials are hardcoded in plain text. Should use secrets: `${{ secrets.DOCKER_USERNAME }}` and `${{ secrets.DOCKER_PASSWORD }}`.

**Q107.** Missing `needs: validate` in the deploy job. Both jobs will run in parallel.

**Q108.** Should use `ARG MODEL_PATH` for build-time and `ENV MODEL_PATH=...` for runtime:
```dockerfile
ARG MODEL_PATH
ENV MODEL_DIR=/opt/model
```

**Q109.** Kubeflow components should use `dsl.OutputPath()` to pass data between components, not Python `return`.

**Q110.** You scale **deployments**, not pods: `kubectl scale deployment my-deployment --replicas=5`

**Q111.** Empty step — add `run:` or `uses:`:
```yaml
- name: Linter Check
  run: |
    pip install flake8
    flake8 .
```

**Q112.** Missing a **Service** YAML. The Deployment creates Pods but there's no Service to expose them.

**Q113.** Missing linter dependency (`needs: lint`) to avoid running expensive training on broken code.

**Q114.** Wrong syntax. Use `${{ secrets.MLFLOW_URI }}` with dollar sign and double braces.

**Q115.** Bind mount path `/home/mohamed/data` is host-dependent and won't exist on a CI runner. Use Docker Volumes or download data in the pipeline.

**Q116.** Each step is a **separate shell**. Variables don't persist. Use `env:` block or write to a file.

**Q117.** `nodePort: 25000` is out of valid range. Must be between **30000-32767**.

**Q118.** Add `if: failure()` to the Upload Logs step so it only runs when training fails.

**Q119.** Kubeflow will **skip** `preprocess_data` (cached from prior successful run) and directly re-run only `train_model`, saving 2 hours.

**Q120.** `COPY . .` before `RUN pip install` means any code change invalidates the pip install cache. Should copy requirements first, install, then copy code.

### Section E — Scenario-Based (Summary Answers)

**Q121.** Prompt Drift (input complexity changed) + Concept Drift (user expectations shifted). Monitor with CLIP scores as sidecar, route anomalies to HITL labeling, trigger Kubeflow retraining at 1000 samples.

**Q122.** (a) GHA: Both jobs start simultaneously → OOM kills one (68GB > 64GB). (b) Kubeflow: Queues Job B in PENDING until Job A finishes, ensuring safe execution.

**Q123.** (a) GHA: Entire pipeline restarts (1hr checkout+install+lint + 4hr training again). (b) Kubeflow: Steps 1-3 cached, only training re-runs. Kubeflow saves 1.5+ hours.

**Q124.** Shared MLflow server for all experiments. Each scientist trains with different params logged to MLflow. CI pipeline with `get_best_model.py` finds top model. CD builds Docker with best model URI.

**Q125.** Controller Manager detects 2 running pods ≠ 5 desired. Creates 3 new Pod definitions. Scheduler assigns them to the 2 remaining healthy nodes. Pods start automatically.

### Section F — Mock Exam (Summary Answers)

**Q137.** Bugs: (1) Missing `actions/checkout@v4`, (2) Indentation of `uses:` and `with:` under steps, (3) `branches: main` should be `branches: [main]`, (4) Empty Linter step, (5) Multi-line indentation under `run: |`, (6) Deploy job missing `runs-on`, (7) Deploy missing `needs: build`.

**Q139.**
```yaml
name: ML Pipeline
on: [push]
jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.10'
      - run: pip install -r requirements.txt
      - run: python train.py
      - run: echo "RUN_$(date +%s)" > model_info.txt
      - uses: actions/upload-artifact@v4
        with:
          name: model-info
          path: model_info.txt

  deploy:
    needs: validate
    runs-on: ubuntu-latest
    steps:
      - uses: actions/download-artifact@v4
        with:
          name: model-info
      - run: echo "Building Docker for $(cat model_info.txt)"
```

**Q143.**
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: ai-backend
spec:
  replicas: 2
  selector:
    matchLabels:
      app: ai-model
  template:
    metadata:
      labels:
        app: ai-model
    spec:
      containers:
      - name: model-server
        image: myrepo/ai-model:v2
        ports:
        - containerPort: 5000
        resources:
          requests:
            memory: "2Gi"
            cpu: "1000m"
            nvidia.com/gpu: 1
          limits:
            memory: "4Gi"
            cpu: "2000m"
            nvidia.com/gpu: 1
```

**Q148.**
```python
import mlflow

mlflow.set_experiment("My_Experiment")

with mlflow.start_run():
    mlflow.log_params({"lr": 0.01, "epochs": 10, "batch_size": 32})
    
    for epoch in range(10):
        accuracy = train_epoch()
        mlflow.log_metric("accuracy", accuracy, step=epoch)
    
    mlflow.pytorch.log_model(model, name="model")
```

**Q149.** (a) First run: Preprocessing (2hrs) succeeds, training (6hrs) fails at hour 4. (b) Re-run: Kubeflow checks cache, sees preprocessing inputs unchanged → **skips** preprocessing. Resumes directly at training. Saves 2 hours of compute. The metadata store records input hashes per component.

**Q150.** `Git Push → Pull Data (DVC) → Run Tests (Pytest) → Log to MLflow → Build Docker Container → Deployment Approval`. Each step validates a different dimension: code quality, data quality, model quality, packaging, and gating.
