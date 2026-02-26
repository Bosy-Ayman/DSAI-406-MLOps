---
theme: neversink
class: 'text-center'
transition: slide-left
title: MLOps (DSAI 406)
author: Mohamed Ghalwash
year: Spring 2025-2026
venue: Zewail City
mdc: true
lecture: 2
slide:
  disableSlideNumbers: true
slide_info: false
---

# ML Engineering for Production <br> (DSAI 406)
## Lecture 2

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

# Lecture 1 Recap

:: content :: 

- Model Development 
- Hidden Technical Debt
- "Ops" family
  - DevOps
  - DataOps
  - MLOps

---
layout: top-title
---

:: title :: 

# What We Learned From Assignment 1?

:: content :: 

-  **Dependency Hell:** Student A has scikit-learn 1.2, Student B has 0.24
-  **Python Versions:** 3.8 vs 3.11 changes everything
-  **Path Issues:** `C:\Users\StudentA\Desktop\data.csv` does not exist on Student B's Mac
-  **Ghost Data:** Where did this cleaned_data.csv come from?

<br>

> If the software isn't reproducible with one command, MLOps doesn't exist.

---
layout: section
---

# Versioning (Git)

---
layout: top-title
---

:: title :: 

# Development Environments: Conda vs. Pip

:: content :: 

<v-click> 

- Before you Dockerize, you must isolate your environment 

- Never use your "Base" Python environment. If you `pip install` globally, you lose the ability to reproduce your work
  
- Standard Python (`pip`) and **Conda** solve the same problem: "Project A needs Pandas 1.0, but Project B needs Pandas 2.0."

</v-click> 

<v-click> 


| Feature | `pip` + `venv` | Conda / Mamba |
| :--- | :--- | :--- |
| **Focus** | Python packages only | Python + Non-Python (C++, CUDA, R) |
| **ML Use Case** | Best for simple web APIs/microservices | The Standard for Data Science (GPU/Cuda drivers) |

</v-click> 


---
layout: top-title
---

:: title :: 

# Essential Conda Commands

:: content :: 

- Isolate: `conda create --name ENVNAME python=3.7`
- Activate: `conda activate ENVNAME`
- Install 
  - `conda install XXX`
  - `pip install XXX`
- Deactivate: `conda deactivate`
- Clean: `conda env remove --name ENVNAME --all`

---
layout: top-title
---

:: title :: 

# A Conda Story in 6 Steps

:: content :: 

```bash {all|1-2|4-5|7-8|10-11|13-14|16-17}
# 1. Create an environment for a Python 3.11 project
$ conda create --name rl_project python=3.11

# 2. Step into the environment
$ conda activate rl_project

# 3. Install some libraries
(rl_project) $ conda install numpy

# 4. Grab a niche library from the Python Package Index
(rl_project) $ pip install biopython_special_plugin==1.3

# 5. Back to normal life
(rl_project) $ conda deactivate

# 6. Clean up when done with the project
$ conda env remove --name rl_project --all
```

---
layout: top-title 
---

:: title ::


# Reproducibility: How to move from your Laptop to Docker

:: content :: 

To build a Docker image, you first need to "freeze" your current working environment into a file

<div class="grid grid-cols-2 gap-4">
<div>

Using Pip/Venv:
```bash
# Create the list
pip freeze > requirements.txt

# What it looks like:
# pandas==2.1.0
# scikit-learn==1.3.0
```

</div>
<div>

Using Conda:
```bash
# Create the list
conda env export --no-builds > environment.yml

# What it looks like:
# dependencies:
#   - python=3.9
#   - pandas=2.1.0
```

</div>
</div>

<v-click class="mt-4">

> Tip: In Docker, we prefer requirements.txt because it is faster to install. If you use Conda, consider using Micromamba in Docker for much smaller/faster images!

</v-click>

---
layout: section
---

# Containerization

---
layout: top-title-two-cols
columns: is-6
---

:: title :: 

# The Solution: Containers

:: left :: 

A **Docker Image** is a lightweight, standalone, executable package that includes everything needed to run a piece of software:
* Code
* Runtime (Python)
* System tools & libraries
* Settings

:: right ::

<div class="flex justify-center mt-10">
  <img src="./images/2_docker.png" class="h-40" />
</div>

Daemon `sudo systemctl start docker`

- Docker Engine 
  `docker run ...`
- Docker Build
  `docker build ...` BuildX sends a build request to the server (BuildKit)
- Docker Compose

<!-- <blockquote class="mt-10">
  "It works on my machine" becomes "Then we shall ship your machine."
</blockquote> -->



---
layout: top-title
---

:: title :: 

# Anatomy of a Dockerfile


:: content :: 

Turning infrastructure into code
  
```dockerfile {all|1,2|4,5|7,8|10,11|13|15,16|all}
# The foundation image (OS + Python). [Base images](https://hub.docker.com/_/python)
FROM python:3.9-slim

# Setting the working directory for any instruction that follow it in the Dockerfile
WORKDIR /app

# Copies files from source(s) to destination 
COPY requirements.txt .

# Executes any commands to create a new layer on top of the current image, at the time you build the image 
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# The "Go" signal, at the run-time when the container starts
CMD ["python", "train.py"]

```

<v-click>

Docker treats every line in a Dockerfile as a "layer" that it tries to save (cache) for later

</v-click>

---
layout: top-title
---

:: title :: 

# Layer Caching: Why Order Matters

:: content :: 

**MLOps efficiency trick**

- Docker builds in **layers**. If you change your **Code**, you don't want to wait 5 minutes to re-download all **libraries** in `requirements.txt`.

<div class="grid grid-cols-2 gap-4">

<div>
❌ The "Slow" Way
```dockerfile
FROM python:3.9
# Copy everything first
COPY . /app 
WORKDIR /app
# If 1 line of code changes, 
# this RUN starts from scratch
RUN pip install -r requirements.txt
```

</div>

<div>
✅ The "MLOps" Way

```dockerfile
FROM python:3.9
WORKDIR /app
# Copy ONLY requirements first
COPY requirements.txt .
RUN pip install -r requirements.txt
# Now copy the code
COPY . . 
```

</div>
</div>

<v-click>

<br> 

> Docker caches the RUN pip install layer. As long as requirements.txt doesn't change, rebuilding takes seconds, not minutes.

</v-click>

---
layout: center
class: text-center
---

# Learn More

[Course Homepage](https://github.com/m-fakhry/DSAI-406-MLOps)
