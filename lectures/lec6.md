---
theme: neversink
class: 'text-center'
transition: slide-left
title: MLOps (DSAI 406)
author: Mohamed Ghalwash
year: Spring 2025-2026
venue: Zewail City
mdc: true
lecture: 6
slide:
  disableSlideNumbers: true
addons:
  - slidev-component-poll
  - slidev-addon-sync
  # - slidev-addon-qrcode
# defaults:
#   slide_info: false
zoom: 1
syncSettings:
  server: http://192.168.1.183:8080
  enabled: true
syncStates:
  poll:
    presenter: false
    init: false
  pollUsers:
    presenter: false
  # Add the following lines if you want to also sync slidev channels
  # shared: ["page", "clicks", "cursor", "lastUpdate"]
  drawings: true
pollSettings:
  anonymous: true # Highly recommended so they don't have to login
---

# ML Engineering for Production <br> (DSAI 406)
## Lecture {{$slidev.configs.lecture}}

Mohamed Ghalwash
<Email v="mghalwash@zewailcity.edu.eg" />

---
layout: fact
---

# Recording is NOT allowed 


---
layout: cover
---

# The Midterm Audit

<div>
  <span class="opacity-50 text-sm">Reviewing the "Tricks" in the midterm exam</span>
</div>

---
layout: top-title-two-cols
align: l-l-lb
---

:: title :: 

# Trick 1: YAML Structure Anatomy

:: left :: 

Identify and fix all errors in this YAML

```yaml{all|6|5,6|8,9|11|12-15|16-18|all}
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
        - name: Tag Model
          run: echo "Tagging model as $VERSION"
        - name: Set Model Version
          run: VERSION="v1.2.3"
	  deploy:
	    steps:
    	  - run: docker build ml-app:latest .
```

:: right :: 

<v-click> 

```yaml
	jobs:
	  train:
	    runs-on: ubuntu-latest
	    steps:
	      - name: Checkout Code
        	uses: actions/checkout@v4        
    	  - run: pip install -r requirements.txt
    	  - name: Train
        	env:
        		MLFLOW_URI: {{ secrets.MLFLOW_URI }}
	        run: python train.py
    	  - run: docker build ml-app:latest .          
        - name: Tag Model
          env:
            VERSION: "v1.2.3"
          run: echo "Tagging model as $VERSION"
	  deploy:
      needs: train
	    steps:
    	  - run: docker build ml-app:latest .
```

</v-click> 

---
layout: top-title-two-cols
columns: is-4
---
:: title :: 

# Trick 2: Dependencies 

:: left :: 

```yaml{all|9,17}
jobs:
  train:
    runs-on: ubuntu-latest
    steps:
        # assume it is filled in correctly to checkout the code 
      - uses: ... 
      - name: Generate ID
        # saves the ID into the file model_id.txt
        run: echo "RUN_12345" > model_id.txt 

  deploy:
    needs: train
    runs-on: ubuntu-latest
    steps:
      - name: Read ID
        # displays the content of the file model_id.txt
        run: cat model_id.txt  
```

:: right ::


<v-click>

<div :style="{ zoom: $slidev.configs.zoom }"> 

```yaml {9-12,19-23}
jobs:
  train:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Generate ID
        run: echo "RUN_12345" > model_id.txt 
      # Upload the file to GitHub's temporary storage
      - uses: actions/upload-artifact@v4
        with:
          name: model-id-storage
          path: model_id.txt

  deploy:
    needs: train
    runs-on: ubuntu-latest
    steps:
      # Pull the file 
      - uses: actions/download-artifact@v4
        with:
          name: model-id-storage
      - name: Read ID
        run: cat model_id.txt 
```
</div>

</v-click>


---
layout: top-title
columns: is-4
---
:: title :: 

# Trick 3: Docker - Build vs Run 

:: content :: 



```docker
FROM python:3.10-slim
WORKDIR /app

# Saves the date into a file 
RUN date > /app/build_time.txt

CMD ["cat", "/app/build_time.txt"]
```

<v-click>

**Image build time**: `docker build ...`

The `RUN` date command runs once and the output is saved into `build_time.txt`, which becomes a permanent part of the image layer

</v-click>
<v-click>

**Container run time**: `docker run ...`

The `CMD` instruction is executed days later, it doesn't run the date command again. It only runs cat. It simply reads the "frozen" file from the image layer

</v-click>

---
layout: top-title 
---

:: title :: 

# Lesson Learned

:: content :: 

1. Each Job is a separate VM. They start with an empty disk. No shared memory. No shared files

2. Each Step is a separate shell. Local variables (e.g., `VAR=1`) die when the step ends

3. 
   - Communication between Steps via `env` or local files
   - Communication between Jobs via Artifacts (for data/files)

4. 
   - `RUN`: Executed during **Image Build**
   - `CMD`: Executed at **Runtime**


<v-click>

> Global `env` blocks are **Read-Only** at runtime. You cannot update them to talk to the next Job

</v-click>

---
layout: center
---

# Discussion (POLL)



<Poll question="Which midterm trick was the most frustrating to debug?" editable=true controlled=true displayResults="poll" >

YAML Structure Anatomy

Dependencies

Docker - Build vs Run

</Poll>

# [http://192.168.1.183:3030](http://192.168.1.183:3030)

---
layout: cover
---

# Making the YAML "Smart" 

---
layout: top-title 
---

:: title :: 

# Architecture Decision

:: content :: 

Scenario: Test everything but only deploy from `main`, i.e., the `Train` job  should be triggered on **all branches** but the `Deploy` job should only be triggered on the **`main` branch**.

<div class="grid grid-cols-2 gap-4"> 
<v-click>
<div>

  - Single Workflow? 
  ```yaml
  on: [push]
  jobs:
    train_test: 
      ...
    deploy:
      ...
  ```
- Full visibility of the pipeline graph (DAG)
- Deploy needs Train and Test
- Shared environment and secrets

</div>
</v-click>
<v-click>
<div>

- Separate Workflows? 
  
  <div class="grid grid-cols-2 gap-1"> 
  
  <div>

  ```yaml
  on: [push]
  jobs:
    train_test: 
      ...



  ```
  </div>
  <div>

  ```yaml
  on: [push]
  jobs:
    deploy: 
      ...

      
  ```
  </div>
  </div>

- List of disconnected runs
- If the Test workflow in the other file failed?
- Redefine the environment, the Python version, and the MLflow secrets twice

</div>
</v-click>
</div>


---
layout: top-title
---

:: title ::

# Conditional Execution: Branch Protection

:: content ::

- Single Workflow: The model version we are deploying is the one that passed the tests

```yaml
on: [push] 
jobs:
  train: 
    runs-on: ubuntu-latest
    ...
  test: 
    needs: train
    runs-on: ubuntu-latest
    ...
  deploy:
    needs: test 
    if: github.ref == 'refs/heads/main'
    ...
```

![DAG](./images/6_ui.png)

---
layout: top-title
---

:: title ::

# Conditional Execution: Job Status (1)

:: content ::

When a 2-hour training job fails, you don't want to re-run it just to see the logs

<v-switch> 

<template #0>

```yaml{all}
jobs:
  train_model:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Heavy Training
        run: python train.py  # 2-hour training job fails ❌ 
```
</template>

<template #1-4>

```yaml{all|10-15}
jobs:
  train_model:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Heavy Training
        run: python train.py  # 2-hour training job fails ❌ 

      - name: Upload Training Logs on Failure
        if: failure() # Only runs if 'Heavy Training' failed
        uses: actions/upload-artifact@v4
        with:
          name: crash-report
          path: logs/debug_info.log
```
</template>

</v-switch> 


<v-click at="3">

<div :style="{ zoom: $slidev.configs.zoom }">

- You don't want to check GitHub every 5 minutes 
- You don't upload logs for every run (saving storage/bandwidth)
</div>
</v-click>

---
layout: top-title
---

:: title ::

# Conditional Execution: Job Status (2)

:: content ::

Dilemma: every step is executed even if one of the previous steps fails <v-click>because of the invisible Condition `if: success()`</v-click>


<div class="grid grid-cols-2 gap-10"> 

<v-click>
<div>

### 🔍 What you see:
```yaml
steps:
  - name: step1
    run: ... 

  - name: step2
    run: ... 

  - name: step3
    run: ... 
```

</div>
</v-click>
<v-click>
<div>

### 🔍 What GHA actually sees:
```yaml
steps:
  - name: step1
    if: success() # (Hidden) - True
    run: ...

  - name: step2
    if: success() # Hidden 
    run: ...

  - name: step3
    if: success() 
    run: ...
```

</div>
</v-click>
</div>

<v-click>

> Every step in your YAML has a **hidden default condition**
</v-click>

---
layout: top-title
---

:: title ::

# Conditional Execution: Job Status (3)

:: content ::

```yaml
steps:
  - name: compile
    run: ...

  - name: test
    run: ...

  - name: publish
    if: github.ref == 'refs/heads/main'
    run: ./publish.sh
```

What will happen when
- Compile and test succeed? <v-click at="1"> publish will be executed on the `main` branch </v-click> 
- Compile or test fails? <v-click at="2"> publish will also be executed on the `main` branch?! </v-click> 

<v-click at="3">

<div :style="{ zoom: $slidev.configs.zoom }">

> As soon as you write an `if:`, the default "Stop on Failure" safety is **disabled**. You must re-enable it manually.

```yaml
  - name: publish
    if: success() & github.ref == 'refs/heads/main'
    run: ./publish.sh
```
</div>
</v-click>

---
layout: top-title 
---

:: title :: 

# Summary of Status Functions

:: content :: 

|  |  |
| :--- | :--- |
| **`success()`** | (Default) Run only if no previous step/job failed |
| **`failure()`** | Run only if a previous step failed |
| **`cancelled()`** | Run only if a human clicked "Cancel" |
| **`always()`** | Run no matter what. Use for shutting down expensive GPU instances |

<br/>

**Operational Rule:**
> Never write a custom `if` condition without including `success()` or `failure()` unless you want that step to be 'Status Blind'

---
layout: top-title
---

:: title ::

# Conditional Execution: Selective Training

:: content ::

```yaml
on: [push]
jobs:
  gpu_train:
    runs-on: cloud-gpu # expensive! GPU bills!!
    steps:
      - run: python train.py # what if the changes does not affect training
```

- Issue: Every tiny typo commit on every branch triggers a full GPU run. **Your budget disappears.**

<v-click>
<div class="absolute inset-0 flex flex-col items-center justify-center pointer-events-none">
  <div class="text-4xl font-bold text-red-600 bg-white p-8 shadow-2xl rounded-xl border-4 border-red-600 transform -rotate-2">
    Homework
  </div>
</div>
</v-click>

---
layout: center
class: text-center
---

<!-- <div class="flex justify-center mt-10">
  <QRCode 
    :width="300" 
    :height="300" 
    data="http://192.168.1.183:8080" 
    :margin="10"
    :dotsOptions="{ type: 'extra-rounded', color: '#4F46E5' }"
    type="svg"
  />
</div> -->


# Learn More

[Course Homepage](https://github.com/m-fakhry/DSAI-406-MLOps)
