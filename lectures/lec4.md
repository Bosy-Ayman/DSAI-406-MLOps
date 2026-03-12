---
theme: neversink
class: 'text-center'
transition: slide-left
title: MLOps (DSAI 406)
author: Mohamed Ghalwash
year: Spring 2025-2026
venue: Zewail City
mdc: true
lecture: 4
slide:
  disableSlideNumbers: true
slide_info: false
---

# ML Engineering for Production <br> (DSAI 406)
## Lecture 4

Mohamed Ghalwash
<Email v="mghalwash@zewailcity.edu.eg" />

---
layout: fact
---

# Recording is NOT allowed 

---
layout: top-title
class: text-center
---

:: title :: 

# 🎓 Recap: From Manual Scripts to Automated Systems

:: content :: 

<div class="grid grid-cols-3 gap-6 mt-8 text-left">

<v-click> 

  <div class="p-4 bg-blue-500/5 border-t-4 border-blue-500 rounded-lg shadow-sm">
    <div class="flex items-center gap-2 mb-3">
      <div class="i-carbon-flow-model-er text-2xl text-blue-500" />
      <h3 class="font-bold">The "Ops" Family</h3>
    </div>
    <ul class="text-sm space-y-2 opacity-90">
      <li><b>DevOps:</b> Dev + Ops Collaboration</li>
      <li><b>DataOps:</b> Quality & Agility in Data</li>
      <li><b>MLOps:</b> The intersection of all three</li>
    </ul>
  </div>

</v-click> 
<v-click> 

  <div class="p-4 bg-green-500/5 border-t-4 border-green-500 rounded-lg shadow-sm">
    <div class="flex items-center gap-2 mb-3">
      <div class="i-carbon-box text-2xl text-green-500" />
      <h3 class="font-bold">Reproducibility</h3>
    </div>
    <ul class="text-sm space-y-2 opacity-90">
      <li><code class="text-xs">Git</code>: Versioning your Logic</li>
      <li><code class="text-xs">Conda</code>: Isolate Dependencies</li>
      <li><code class="text-xs">Docker</code>: Package the Environment</li>
    </ul>
  </div>

</v-click> 
<v-click> 

  <div class="p-4 bg-purple-500/5 border-t-4 border-purple-500 rounded-lg shadow-sm">
    <div class="flex items-center gap-2 mb-3">
      <div class="i-carbon-view text-2xl text-purple-500" />
      <h3 class="font-bold">Observability</h3>
    </div>
    <ul class="text-sm space-y-2 opacity-90">
      <li><b>MLflow:</b> Tracking Experiments</li>
      <li><b>Metrics:</b> Accuracy vs. Drift</li>
      <li><b>Artifacts:</b> Storing the "Brain"</li>
    </ul>
  </div>

</v-click> 

</div>

<v-click> 

<div class="mt-10 p-5 bg-gray-100 dark:bg-gray-800 rounded-xl border-l-8 border-orange-500">
  <div class="flex items-center gap-4">
    <div class="i-carbon-infinity text-4xl text-orange-500 animate-pulse" />
    <div>
      <p class="font-bold text-lg">The "Glue": CI/CD</p>
      <p class="text-sm opacity-80">Automating the lifecycle to rapidly validate and deliver applications to end-users.</p>
    </div>
  </div>
</div>

</v-click> 

---
layout: top-title
---

:: title :: 

# CI/CD in MLOps

:: content :: 

<v-clicks>

- **Continuous Integration (CI):** 
  - Every `git push` triggers an automated build and test.
  - Ensures developers can build, test, and validate code within a shared repository **without manual work**
- **Continuous Delivery / Deployment (CD):** 
  - Every successful build is ready to be deployed to a "Staging" environment (delivery).
  - Extend these automated steps to production testing and configuration for release management.

</v-clicks>

<v-click>

<div class="mt-8 p-4 bg-yellow-500 bg-opacity-10 border-l-4 border-yellow-500">
  <strong>Goal:</strong> No model should ever reach production without passing a battery of automated tests.
</div>

</v-click>

---
layout: top-title
---

:: title ::

# Tools for CI/CD 

:: content ::


<div class="grid grid-cols-2 gap-4 mt-4">

<div class="p-3 border-2 border-orange-500 rounded-lg bg-orange-500/5">
<div class="flex items-center gap-2 mb-1">
<div class="i-carbon-logo-gitlab text-xl text-orange-600" />
<h3 class="font-bold text-orange-600">GitLab CI/CD</h3>
</div>
<p class="text-xs font-bold mb-1">Best for: Private Enterprise & Security</p>
</div>

<div class="p-3 border-2 border-red-500 rounded-lg bg-red-500/5">
<div class="flex items-center gap-2 mb-1">
<div class="i-carbon-settings text-xl text-red-600" />
<h3 class="font-bold text-red-600">Jenkins</h3>
</div>
<p class="text-xs font-bold mb-1">Best for: Legacy Systems & Customization</p>
</div>

<div class="p-3 border-2 border-blue-500 rounded-lg bg-blue-500/5">
<div class="flex items-center gap-2 mb-1">
<div class="i-carbon-cloud text-xl text-blue-600" />
<h3 class="font-bold text-blue-600">Managed Cloud (AWS/GCP)</h3>
</div>
<p class="text-xs font-bold mb-1">Best for: Scaling & Massive Data</p>
</div>

<div class="p-3 border-2 border-purple-500 rounded-lg bg-purple-500/5">
<div class="flex items-center gap-2 mb-1">
<div class="i-carbon-kubernetes text-xl text-purple-600" />
<h3 class="font-bold text-purple-600">Kubeflow Pipelines</h3>
</div>
<p class="text-xs font-bold mb-1">Best for: Kubernetes-Native MLOps</p>
</div>

</div>

<div class="mt-4 text-center">
<p class="text-sm italic">"Tools change, but the YAML logic we will learn today stays the same."</p>
</div>

---
layout: fact
class: text-center
---

# Why GitHub Actions?
## In a sea of tools, it is the "Built-in" Choice

<div class="flex justify-center items-center gap-12 mt-10 opacity-50 filter grayscale">
  <div class="i-carbon-logo-gitlab text-4xl" />
  <div class="i-carbon-settings text-4xl" /> <div class="i-carbon-cloud text-4xl" />    </div>

<div class="flex justify-center items-center mt-4">
  <div class="i-carbon-logo-github text-8xl text-primary animate-bounce-in" />
</div>

<div class="mt-8 text-2xl font-bold bg-gradient-to-r from-blue-400 to-green-400 bg-clip-text text-transparent">
  Built-in. Automated. Free for Public Repos.
</div>

<p class="mt-4 opacity-60 text-sm">
  The standard for startups: No servers to manage, no credit cards required.
</p>


---
layout: top-title
---

:: title :: 

# The Lifecycle of a Pull Request

:: content :: 

### What happens when you `git push`?

A new Push triggers a **Pull Request (PR)**. Before merging, the "Robot" (CI) must:

<div class="grid grid-cols-2 gap-10 pt-4">

<div class="space-y-6">
  <div class="flex items-start gap-3">
    <div class="i-carbon-repo-source text-2xl text-blue-500" />
    <div>
      <p class="font-bold">1. Code Check (Lint & Unit Tests)</p>
      <p class="text-sm opacity-60 text-balance">Does the code follow standards? Do the preprocessing functions still work?</p>
    </div>
  </div>

  <div class="flex items-start gap-3">
    <div class="i-carbon-analytics text-2xl text-green-500" />
    <div>
      <p class="font-bold">2. Model Validation</p>
      <p class="text-sm opacity-60 text-balance">Run a "Smoke Test" training. Is the accuracy <code>> threshold</code>?</p>
    </div>
  </div>
</div>

<div class="bg-gray-100 dark:bg-gray-800 p-6 rounded-xl border-2 border-dashed border-gray-400 flex flex-col items-center justify-center text-center">
  <div class="i-carbon-git-pull-request text-5xl mb-4 text-orange-500" />
  <p class="font-mono text-sm">PR #42: Updated Optimizer</p>
  <div class="mt-4 flex gap-2">
    <span class="px-2 py-1 bg-green-500 text-white text-xs rounded">Pytest: Pass</span>
    <span class="px-2 py-1 bg-green-500 text-white text-xs rounded">MLflow: Logged</span>
  </div>
</div>

</div>


---
layout: top-title
---

:: title :: 

# The CI/CD YAML Pipeline Anatomy

:: content :: 

- **`name`**: (Optional) Name for your workflow that appears in the GitHub Actions tab of your repository
- **`on`**: (Required) Specifies the GitHub event(s) that automatically trigger the workflow, such as `push` (`branches`, `branches-ignore`), `pull_request`, `issues`, `workflow_dispatch` or `schedule` events
- **`jobs`**: (Required) A map that groups one or more jobs, which run in parallel by default


```yaml
# .github/workflows/NAME.yml
name: ...
on: [...]
jobs:
  ...
```

<v-click>

<div class="mt-8 p-4 bg-yellow-500 bg-opacity-10 border-l-4 border-yellow-500">
  Use `push: branches: [main]` for your Deployment YAML, but use `pull_request: branches: [main]` for your Testing YAML. This ensures that the code is tested before it's allowed to touch the main branch.
</div>

</v-click>

---
layout: top-title
---

:: title ::

# How to "Activate" Your Workflow

:: content ::

- Your YAML file must be stored here:
`[Project Root]/.github/workflows/your-pipeline.yml`

- The folder names `.github` and `workflows` must be lowercase

- Extension: Use `.yml` or `.yaml`

```bash
mkdir -p .github/workflows
cp your-pipeline.yml .github/workflows/
git add .
git commit -m "adding CI/CD pipeline"
git push
```


---
layout: top-title-two-cols
columns: is-10
align: l-lt-lt
class: overflow-hidden
---


:: title :: 

# Structure within a Job

:: left :: 

Each job within the jobs section has its own nested keys: 
- **<job_id>**: A unique string identifier for the job.
  - **`runs-on`**: (Required) Defines the type of virtual machine (runner) the job will execute on, such as `ubuntu-latest`
  - **`steps`**: (Required) A sequence of individual tasks that are executed in order on the runner
    - **`name`**: (Optional) Name for the step
    - **`run`**: Executes a command or script on the runner's shell 
    - **`uses`**: Specifies a pre-build action 
    - **`with`**: Used to pass inputs to an action specified by uses

:: right ::

```yaml
# .github/workflows/NAME.yml
name: ...
on: [...]
jobs:
  test_code:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Linting with flak8
        run: |
          pip install flake8
          flake8 .
```

---
layout: top-title
---

:: title :: 

# The CI/CD Workflow: End-to-End MLOps Pipeline

:: content :: 

```yaml{1|3-7|9-14|15-20|all}
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
layout: center
class: text-center
---

# Learn More

[Course Homepage](https://github.com/m-fakhry/DSAI-406-MLOps)
