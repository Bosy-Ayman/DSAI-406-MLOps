# 🐙 GitHub Actions — 50 Tricky, Edge-Case & Exam-Style Questions

> **Topic:** Advanced CI/CD, Runner Internals, Security Traps, YAML Syntax Gotchas, and MLOps Pipeline Orchestration.
> **Target Audience:** Students preparing for the DSAI-406 MLOps Exam who need to excel at "between-the-lines" tricky questions designed by demanding professors.

---

## 🗺️ Topic Breakdown & VM Boundary Context

To answer these tricky questions, always keep the **VM Boundary and Execution Context** in mind:

```text
┌────────────────────────────────────────────────────────────────────────┐
│                      GITHUB ACTIONS RUNNER WORKFLOW                    │
│                                                                        │
│ ┌──────────────────────────────────┐ ┌───────────────────────────────┐ │
│ │ JOB 1: "train" (Runs on VM 1)    │ │ JOB 2: "deploy" (Runs on VM 2)│ │
│ │                                  │ │                               │ │
│ │  ┌────────────────────────────┐  │ │  ┌──────────────────────────┐  │ │
│ │  │ Step 1 (Shell Process A)   │  │ │  │ Step 1 (Shell Process X) │  │ │
│ │  │ - Sets $VAR (local to shell)│ │ │  │ - Cannot see VM 1 disk   │  │ │
│ │  │ - Appends to $GITHUB_ENV   │  │ │  │ - Needs download-artifact│  │ │
│ │  └─────────────┬──────────────┘  │ │  └──────────────────────────┘  │ │
│ │                │ (Persists)      │ │                               │ │
│ │  ┌─────────────▼──────────────┐  │ │                               │ │
│ │  │ Step 2 (Shell Process B)   │  │ │                               │ │
│ │  │ - Reads $VAR from $GITHUB_ENV │ │                               │ │
│ │  │ - Writes to $GITHUB_OUTPUT │  │ │                               │ │
│ │  └────────────────────────────┘  │ │                               │ │
│ └──────────────────┬───────────────┘ └───────────────────────────────┘ │
└────────────────────┼───────────────────────────────────────────────────┘
                     │ (Artifact / Output Channel)
                     ▼
```

---

## 🗂️ Table of Contents

- [Chapter 1: Runner Architecture, Filesystems, & VM Persistence (Qs 1-8)](#chapter-1-runner-architecture-filesystems--vm-persistence-qs-1-8)
- [Chapter 2: Advanced Triggers, Filtering, & Event Contexts (Qs 9-15)](#chapter-2-advanced-triggers-filtering--event-contexts-qs-9-15)
- [Chapter 3: Complex YAML Syntax, Job Needs, & Matrix Strategies (Qs 16-23)](#chapter-3-complex-yaml-syntax-job-needs--matrix-strategies-qs-16-23)
- [Chapter 4: Conditional Execution & Status Check Functions (Qs 24-30)](#chapter-4-conditional-execution--status-check-functions-qs-24-30)
- [Chapter 5: Security, Secrets, Fork Restrictions, & Token Permissions (Qs 31-38)](#chapter-5-security-secrets-fork-restrictions--token-permissions-qs-31-38)
- [Chapter 6: Caching, Artifacts, & Action Integrations (Qs 39-44)](#chapter-6-caching-artifacts--action-integrations-qs-39-44)
- [Chapter 7: Real-World "Bug Hunt" & YAML Debugging Scenarios (Qs 45-50)](#chapter-7-real-world-bug-hunt--yaml-debugging-scenarios-qs-45-50)
- [🔑 Master Answer Key (With Deep-Dive Explanations)](#-master-answer-key-with-deep-dive-explanations)

---

## Chapter 1: Runner Architecture, Filesystems, & VM Persistence (Qs 1-8)

#### Q1. The Shell Variable Mirage
A junior MLOps engineer tries to set a training hyperparameter in Step 1 and read it in Step 2:
```yaml
- name: Configure Hyperparameters
  run: export BATCH_SIZE=64
- name: Run Training
  run: python train.py --batch $BATCH_SIZE
```
What happens when this job runs on `ubuntu-latest`?
- (a) The script receives `--batch 64` because steps run on the same VM.
- (b) The workflow crashes in Step 1 with a syntax error because `export` is not a GHA keyword.
- (c) The script receives `--batch ` (empty string) because each step runs in a completely separate shell process.
- (d) GHA automatically detects the export and puts it in the global context.

#### Q2. The Workspace Cleanliness Fallacy
You have a multi-job workflow. Job 1 trains a model and writes `model.pt` to the runner's workspace (`/home/runner/work/repo/repo/model.pt`). Job 2 is scheduled to deploy the model:
```yaml
jobs:
  train:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: python train.py # saves model.pt
  deploy:
    runs-on: ubuntu-latest
    needs: train
    steps:
      - run: python deploy.py --model model.pt
```
What is the outcome of the `deploy` job?
- (a) Success: Job 2 runs on the same VM, so `model.pt` is readily available.
- ==(b) Failure: Job 2 runs on a freshly provisioned, separate VM with an empty workspace. `model.pt` does not exist.==
- (c) Success: GHA automatically syncs the workspace directory across all jobs.
- (d) Failure: Job 2 cannot run because it does not contain the `actions/checkout@v4` step first, which is syntactically required for every single job.

#### Q3. The Root Privilege Trap
An engineer wants to install a custom library using `sudo apt-get` in a runner step. Which of the following is true?
- (a) The step will fail because GitHub-hosted runners run as a standard restricted user and do not support `sudo`.
- (b) The step will prompt for a password, stalling the pipeline until it times out.
- (c) The step will succeed because the default user on GitHub-hosted runners runs as a passwordless `sudoer`.
- (d) The step will only succeed if the runner is configured with `runs-on: ubuntu-latest-privileged`.

#### Q4. Modifying the System Path
You are installing a specific version of CUDA in your CI pipeline to test model latency. You download it to `/opt/cuda/bin`. How do you make sure that all subsequent steps in the same job can execute `nvcc` directly without typing the full path?
- (a) `- run: export PATH="/opt/cuda/bin:$PATH"`
- ==(b) `- run: echo "/opt/cuda/bin" >> $GITHUB_PATH`==
- (c) `- run: echo "PATH=/opt/cuda/bin" >> $GITHUB_ENV`
- (d) `- run: set-env -name PATH -value /opt/cuda/bin`

#### Q5. The Stalled Process Billing Nightmare
A PyTorch model training script gets stuck in an infinite loop due to a dataloader deadlock. You did not specify a `timeout-minutes` value in your workflow. What is the default time limit before GitHub terminates this stuck runner?
- (a) 60 minutes (1 hour)
- (b) 120 minutes (2 hours)
- ==(c) 360 minutes (6 hours)==
- (d) 1440 minutes (24 hours)

#### Q6. The Windows Shell Default Gotcha
You set up a workflow that runs on a matrix of operating systems: `[ubuntu-latest, windows-latest]`. You write a step like this:
```yaml
- name: Clean up temporary logs
  run: rm -rf ./logs/
```
What happens when this step executes on `windows-latest`?
- (a) It succeeds because GHA translates standard bash commands to PowerShell equivalents on Windows.
- ==(b) It fails because the default shell on Windows runners is PowerShell Core (`pwsh`), which does not natively support `rm -rf` without threw errors or syntax differences (like empty params).==
- (c) It succeeds because Windows runners use Git Bash as their default shell.
- (d) It fails because Windows does not support directories ending in a trailing slash in shell scripts.

#### Q7. Workspace Contents on Job Boot
If a job starts and its very first step is:
```yaml
- name: List Files
  run: ls -la
```
Assuming the repository has 100 Python files, what is printed in the logs?
- (a) A complete list of all 100 Python files in the repository.
- (b) Only the `.github/workflows/` directory.
- (c) An empty directory (except for standard hidden runner metadata/directories like `.`, `..`).
- (d) A compilation error, because you are not allowed to run bash commands before checking out code.

#### Q8. The PowerShell Exit Code Blindspot
On a `windows-latest` runner, you write a multi-line PowerShell script:
```yaml
- name: Run Checks
  shell: pwsh
  run: |
    Get-Item "non_existent_file.txt"
    Write-Output "Successfully finished checks!"
```
The first command (`Get-Item`) fails because the file doesn't exist. Does GHA mark this step as failed or successful?
- (a) Failed: PowerShell Core always exits on the first error.
- (b) Successful: GHA runs PowerShell with `$ErrorActionPreference = 'Continue'` by default, so it prints the error, runs the next line, and exits with code 0.
- (c) Failed: GHA explicitly wraps PowerShell runs with a wrapper that checks `$ErrorActionPreference = 'Stop'` dynamically, forcing an immediate exit.
- (d) Successful: Because the last command `Write-Output` completed with exit code 0, masking the previous error.

---

## Chapter 2: Advanced Triggers, Filtering, & Event Contexts (Qs 9-15)

#### Q9. Overlapping Path Filters
You want to run model checks only when code in `src/` changes, but NOT when documentation in `src/docs/` changes. You write:
```yaml
on:
  push:
    paths:
      - 'src/**'
    paths-ignore:
      - 'src/docs/**'
```
What happens when you push a commit that changes `src/train.py` and `src/docs/api.md` simultaneously?
- (a) The workflow does not run because `paths-ignore` takes absolute precedence.
- (b) The workflow runs because at least one path matches `paths` and is not ignored.
- (c) GitHub rejects this YAML configuration as syntax error because you cannot combine `paths` and `paths-ignore` for the same event.
- (d) The workflow runs only if the commit message contains `[run-ci]`.

#### Q10. The Reusable Workflow Secrets Context
You build a reusable workflow in a central DevOps repo to validate Docker images. In your MLOps repo, you call this workflow:
```yaml
jobs:
  call-validation:
    uses: central-org/devops-workflows/.github/workflows/docker-check.yml@main
```
The reusable workflow needs access to your MLOps repo's `DOCKER_PASSWORD` secret to push images. How is the secret inherited?
- (a) Reusable workflows automatically inherit all secrets of the caller repository by default.
- (b) The workflow fails because reusable workflows have no access to caller secrets unless `secrets: inherit` is explicitly passed in the caller job.
- (c) The caller must pass the secret through the `inputs` block.
- (d) The reusable workflow must define the secrets in its own repository, not the caller's.

#### Q11. Triggering Workflows via GITHUB_TOKEN
You write a Python script that runs inside a workflow on `push`. The script commits a formatted version of the code and pushes it back to the repository using the automatically provided `GITHUB_TOKEN`. 
What happens when this new commit is pushed?
- (a) It triggers any workflow configured to run on `push: branches: [main]`, creating an infinite CI loop.
- (b) It does NOT trigger any subsequent workflows to prevent accidental infinite recursion loops.
- (c) It triggers the workflow only if the runner is self-hosted.
- (d) It triggers subsequent workflows, but they are limited to a maximum depth of 3 runs.

#### Q12. The `workflow_run` vs `workflow_call` Trap
What is the primary operational difference between using the `workflow_run` trigger and a Reusable Workflow (`workflow_call`)?
- (a) `workflow_run` runs in the same runner container; `workflow_call` runs on a separate VM.
- (b) `workflow_run` is triggered asynchronously after another workflow completes (running with the default branch's configuration), whereas `workflow_call` runs inline as a synchronous job dependency of the caller workflow.
- (c) `workflow_call` does not support inputs, while `workflow_run` does.
- (d) `workflow_run` is only available for private repositories, while `workflow_call` is for public.

#### Q13. The Dynamic Event JSON File
Where does GHA store the full webhook payload JSON (containing pull request details, commit messages, sender metadata, etc.) of the event that triggered the current workflow?
- (a) In the global context variable `${{ github.payload }}`.
- (b) In a local environment variable `$GITHUB_EVENT_CONTEXT`.
- (c) In a file located at the path specified by the `$GITHUB_EVENT_PATH` environment variable.
- (d) In the hidden system directory `/etc/github/event.json`.

#### Q14. The Branch Deletion Event Gotcha
You have a cleanup workflow configured to delete ephemeral model endpoints when a feature branch is deleted:
```yaml
on:
  delete:
```
If a developer deletes the branch `feature/hyperopt` from the GitHub UI, what configuration dictates which version of the YAML file is executed?
- (a) The YAML file inside the deleted `feature/hyperopt` branch is parsed and executed.
- (b) The YAML file on the repository's default branch (usually `main`) is executed.
- (c) The workflow is skipped because the branch no longer exists to fetch the YAML file.
- (d) GitHub searches for the YAML file in the most recently updated active branch.

#### Q15. Triggering on Fork PRs (The GITHUB_TOKEN Write Trap)
A public open-source project has a CI workflow that runs on:
```yaml
on:
  pull_request:
```
A malicious user forks the repository, modifies a test script to print `secrets.API_KEY`, and submits a Pull Request. What happens when the CI runs?
- (a) The workflow runs, prints `***` (masked), but does not leak the key because the workflow runs with a read-only `GITHUB_TOKEN` and has **zero access** to secrets from the base repository.
- (b) The workflow runs, accesses the secrets, and leaks the key because the PR is targeting the base repository.
- (c) The workflow fails to start because GitHub blocks forks from triggering workflows entirely.
- (d) The workflow runs and has write access to the repository because `pull_request` defaults to administrative access.

---

## Chapter 3: Complex YAML Syntax, Job Needs, & Matrix Strategies (Qs 16-23)

#### Q16. The Simultaneous Run/Uses Error
A developer wants to check out the codebase and print a message in a single step to save lines of code:
```yaml
- name: Prepare Workspace
  uses: actions/checkout@v4
  run: echo "Workspace ready!"
```
What is the result when this workflow is parsed?
- (a) The code is checked out, and "Workspace ready!" is printed to the logs.
- ==(b) The step executes, but only the `uses` block runs; the `run` block is ignored.==
- (c) The workflow fails with a YAML parser syntax error: a step cannot contain both `uses` and `run` keys.
- (d) The runner executes the checkout and passes `echo "Workspace ready!"` as an input parameter to the action.

#### Q17. The Missing Needs Cascade
You have the following job definitions:
```yaml
jobs:
  job_a:
    runs-on: ubuntu-latest
    run: exit 1 # Fails!
  job_b:
    runs-on: ubuntu-latest
    # no "needs" defined
    run: echo "Job B running"
  job_c:
    runs-on: ubuntu-latest
    needs: [job_a, job_b]
    run: echo "Job C running"
```
What happens to `job_b` and `job_c`?
- (a) `job_b` and `job_c` are both marked as "Skipped" because `job_a` failed.
- (b) `job_b` runs and succeeds in parallel with `job_a`. `job_c` is skipped because one of its prerequisites (`job_a`) failed.
- ==(c) `job_b` runs and succeeds. `job_c` runs because `job_b` succeeded, ignoring the failure of `job_a`.==
- (d) The workflow crashes immediately before running any jobs because `job_a` has no `steps` key (only `run` at the job level).

#### Q18. Matrix Fail-Fast Dynamics
You run a large hyperparameter sweep using GHA matrices:
```yaml
strategy:
  fail-fast: true
  matrix:
    learning_rate: [0.1, 0.01, 0.001]
```
The job for `learning_rate: 0.1` starts first, encounters a division-by-zero error, and fails after 3 minutes. The job for `learning_rate: 0.01` was estimated to run for 2 hours. What happens to the running `0.01` job?
- (a) It continues running until completion because matrix jobs are independent.
- (b) It is immediately cancelled by GitHub Actions to save CI/CD billing minutes.
- (c) It is paused and retried with the next learning rate in the list.
- (d) It is marked as successful by default to prevent pipeline blockages.

#### Q19. The Missing Needs Output Trap
You are trying to pass a dynamically calculated model accuracy from Job A to Job B.
```yaml
# Job A
job_a:
  runs-on: ubuntu-latest
  steps:
    - id: calc
      run: echo "ACCURACY=0.94" >> $GITHUB_OUTPUT

# Job B
job_b:
  runs-on: ubuntu-latest
  needs: job_a
  steps:
    - run: echo "The model accuracy is ${{ needs.job_a.outputs.ACCURACY }}"
```
When Job B runs, it prints `The model accuracy is ` (empty). Why?
- (a) You must write to `$GITHUB_ENV` instead of `$GITHUB_OUTPUT` to cross job boundaries.
- (b) Job B did not download the artifacts from Job A.
- ==(c) Job A did not declare the output at the **job level** mapping to the step output.==
- (d) The syntax inside Job B must be `${{ steps.calc.outputs.ACCURACY }}`.

#### Q20. Matrix Include Override Behavior
Consider this matrix configuration:
```yaml
strategy:
  matrix:
    os: [ubuntu-latest, windows-latest]
    python: ['3.9', '3.10']
    include:
      - os: ubuntu-latest
        python: '3.10'
        gpu: true
```
How many total jobs are spawned, and how many of them have the `gpu` variable set to `true`?
- (a) 5 jobs spawned; only 1 has `gpu: true`.
- (b) 4 jobs spawned; 2 have `gpu: true`.
- ==(c) 4 jobs spawned; only 1 has `gpu: true` (specifically the one matching `ubuntu-latest` and `3.10`).==
- (d) 5 jobs spawned; 2 have `gpu: true`.

#### Q21. The Expression Formatting Trap
You write a conditional to ensure your deployment step only runs on the main branch:
```yaml
- name: Deploy
  if: ${{ github.ref == 'refs/heads/main' }}
  run: ./deploy.sh
```
What is the result when GHA processes this step?
- (a) It throws a syntax error because `${{ }}` is forbidden in the `if:` key.
- (b) It executes perfectly; GHA parses the expression and proceeds.
- (c) It runs the step on EVERY branch because the `${{ }}` syntax evaluates to a string literal which is always truthy.
- ==(d) It executes only on main, but displays a warning in the runner logs recommending the removal of the outer `${{ }}` brackets.==

#### Q22. The Double Quotes JSON Parsing Error
You have a step that dynamically writes JSON data containing environment variables:
```yaml
- run: echo "{\"version\": \"${{ github.sha }}\"}" > metadata.json
```
If the commit message or property evaluated contains double quotes, what happens?
- (a) GHA automatically escapes any special characters inside `${{ ... }}` expressions.
- ==(b) GHA crashes before starting because expressions are evaluated literally, and raw double quotes in the expanded string will break the shell command syntax.==
- (c) The shell automatically fixes the quotes using bash translation rules.
- (d) It writes to the file successfully, but masks the whole file as a secret.

#### Q23. Matrix Exclude Edge Case
Consider this matrix configuration:
```yaml
strategy:
  matrix:
    os: [ubuntu-latest, macos-latest, windows-latest]
    version: [1, 2]
    exclude:
      - os: macos-latest
```
What is the effect of this `exclude` statement?
- ==(a) It excludes all `macos-latest` runs entirely (spawning 4 total jobs instead of 6).==
- (b) It throws an invalid syntax error because `exclude` requires specifying the `version` key as well.
- (c) It excludes only the `macos-latest` with `version: 1` job.
- (d) It runs all 6 jobs because the exclude filter is incomplete.

---

## Chapter 4: Conditional Execution & Status Check Functions (Qs 4-30)

#### Q24. Overriding the Implicit Success Safeguard
In GHA, every step has an implicit condition that it only runs if the job is succeeding. You want to run a cleanup step if the previous steps fail, so you write:
```yaml
- name: Cleanup Cloud GPU
  if: failure()
  run: ./cleanup.sh
```
If the workflow run is **cancelled** by a developer manual intervention, does this cleanup step run?
- (a) Yes, because `failure()` covers cancellations as well.
- ==(b) No, it does not run. Only `always()` or `cancelled()` runs on manual cancellations.==
- (c) Yes, because cancellation is classified as a job-level failure.
- (d) No, because step cleanup scripts are automatically blocked on cancellations.

#### Q25. The Blind Condition Trap
An engineer wants a step to run only if a custom environment variable `RUN_TESTS` is `'true'`. They write:
```yaml
- name: Run Integration Tests
  if: env.RUN_TESTS == 'true'
  run: pytest tests/
```
If the previous linting step in this job **failed**, does this integration test step run?
- (a) Yes, because the custom `if:` condition overrides the default GHA "Stop on Failure" safety check, making the step status-blind.
- ==(b) No, because custom `if:` conditions that do not contain explicit status functions (like `always()` or `failure()`) automatically inherit the implicit `success()` check under the hood.==
- (c) Yes, because environment checks are evaluated at the runner level, bypassing job status.
- (d) No, because environment variables cannot be accessed within `if:` blocks.

#### Q26. The Outcome vs Conclusion Riddle
You configure a step to continue running the rest of the job even if this specific step fails:
```yaml
- id: test-step
  run: python train.py --smoke-test
  continue-on-error: true
```
The step fails during run. What are the values of `steps.test-step.outcome` and `steps.test-step.conclusion`?
- (a) `outcome: failure`, `conclusion: failure`
- (b) `outcome: success`, `conclusion: success`
- ==(c) `outcome: failure`, `conclusion: success`==
- (d) `outcome: success`, `conclusion: failure`

#### Q27. Always() vs Cancelled() Hierarchy
If a workflow job times out (e.g. hits the 6-hour limit), which of the following steps will be executed?
```yaml
- name: Step 1
  if: always()
  run: echo "Always!"

- name: Step 2
  if: cancelled()
  run: echo "Cancelled!"
```
- ==(a) Both Step 1 and Step 2 will execute.==
- (b) Only Step 1 will execute.
- (c) Only Step 2 will execute.
- (d) Neither step will execute because the virtual machine is instantly destroyed upon timeout.

#### Q28. Nested Condition Boolean Algebra
You want a step to run only when:
- The trigger is a `push` to the `main` branch.
- The previous steps succeeded.
What is the correct syntax?
- (a) `if: github.event_name == 'push' && github.ref == 'refs/heads/main'`
- (b) `if: success() && github.event_name == 'push' && github.ref == 'refs/heads/main'`
- ==(c) Both (a) and (b) are functionally identical and correct.==
- (d) Neither; status checks cannot be combined with context variables in the same `if` block.

#### Q29. The Masked Status Context
What is the behavior of the `success()` function when placed inside a job-level `if` conditional, compared to a step-level `if` conditional?
- (a) It behaves identically in both locations.
- ==(b) At the job level, `success()` checks the status of all **upstream parent jobs** listed in the `needs` key; at the step level, it checks the status of **previous steps** within that same job.==
- (c) It is invalid syntax at the job level and will fail validation.
- (d) At the job level, it checks if the workflow trigger was successful.

#### Q30. The Hidden `success()` Concept
If you have a workflow step like this:
```yaml
- name: Post-Training Check
  if: always() && steps.train.outputs.status == 'complete'
```
Under what circumstances does this step run?
- (a) It runs only if the training step completed and succeeded.
- ==(b) It runs regardless of previous steps' success/failure status, as long as the train step emitted the specific output.==
- (c) It fails parsing because you cannot combine `always()` with step outputs.
- (d) It runs only if the training step failed but emitted the output.

---

## Chapter 5: Security, Secrets, Fork Restrictions, & Token Permissions (Qs 31-38)

#### Q31. The Substring Masking Accident
You store your production database password in GHA Secrets. The password is `prod`. In your workflow, you run:
```yaml
- run: echo "Welcome to the production deployment server!"
```
What is printed in the job logs?
- (a) `Welcome to the production deployment server!`
- ==(b) `Welcome to the ***uction deployment server!`==
- (c) `Welcome to the *** deployment server!`
- (d) `***` (The entire line is masked)

#### Q32. The Process Tree Secret Leak
You pass a database API secret to a Python script via command-line arguments:
```yaml
- run: python train.py --db-key ${{ secrets.DB_KEY }}
```
How does this impact security on the runner?
- (a) Highly secure: GitHub logs will mask it, ensuring complete protection.
- ==(b) Insecure: Any process running on the same VM (e.g. compromised third-party actions) can read the secret by inspecting the process command lines (e.g. running `ps aux`). Environment variables should be used instead.==
- (c) Syntax error: GHA does not allow placing secret expressions inside a `run:` string.
- (d) Secure: GHA virtualizes each step in a sandboxed process group that hides command-line arguments from other processes.

#### Q33. Base64 Encoding Secret Leak Bypass
An engineer suspects that a third-party action is malicious and wants to verify if it can access secrets. The engineer runs:
```yaml
- name: Debug Secret
  run: |
    echo "${{ secrets.SUPER_SECRET }}" | base64
```
What is printed in the logs?
- (a) `***`
- ==(b) The plain-text base64 encoded string of the secret, completely unmasked.==
- (c) A GHA security violation error, blockading the log write.
- (d) The string `***` encoded in base64.

#### Q34. GITHUB_TOKEN Default Permission Principle
If you do not explicitly define a `permissions:` block in your workflow YAML, what are the default permissions of the automatic `GITHUB_TOKEN` provided to your runner?
- (a) Read-only access across all scopes.
- (b) Read/Write access across all scopes.
- ==(c) It depends on the repository or organization settings, which might default to Read/Write (insecure) or Read-only (secure).==
- (d) Admin access to all repository operations.

#### Q35. The Pull Request Target Danger
What is the major security risk associated with triggering a workflow on `pull_request_target` instead of `pull_request`?
- (a) Workflows run 50% slower.
- ==(b) `pull_request_target` runs in the context of the base repository (having write access and secrets). If you check out the untrusted fork code (`github.event.pull_request.head.sha`) and run scripts from it, the fork contributor can steal your secrets or write to your repository.==
- (c) `pull_request_target` runs without a runner VM, forcing local command compilation.
- (d) Fork PRs are blocked from building Docker containers on `pull_request_target`.

#### Q36. Secrets Masking in Files
You download a secret to a configuration file:
```yaml
- run: echo "${{ secrets.CONFIG_FILE_DATA }}" > config.json
- run: cat config.json
```
Does GHA mask the output of the second step (`cat config.json`)?
- (a) No, GHA only masks secrets when they are explicitly referenced inside `${{ }}` in the same step.
- ==(b) Yes, GHA scans all stdout and stderr streams dynamically and will mask any string match of your configured secrets, regardless of how they are printed.==
- (c) No, because GHA does not scan file read streams.
- (d) Yes, but only if the file name ends in `.txt` or `.log`.

#### Q37. Environment vs Repository Secrets Scope
You configure a secret named `AWS_SECRET` at the **Repository level**, and another secret also named `AWS_SECRET` inside an **Environment** named `production`. Your job is configured as follows:
```yaml
jobs:
  deploy:
    environment: production
    runs-on: ubuntu-latest
    steps:
      - run: echo "AWS Key is ${{ secrets.AWS_SECRET }}"
```
Which secret is printed (masked)?
- (a) The Repository-level secret, because repository scope overrides environment scope.
- ==(b) The Environment-specific secret, because environment-level secrets override repository-level secrets of the same name.==
- (c) Both values are concatenated.
- (d) The step throws a variable naming conflict error.

#### Q38. Third-Party Action Version Pinning
What is the most secure way to reference a third-party community action in your workflow file to prevent dependency hijack or malicious update injection?
- (a) Pin to a major tag: `uses: third-party/action@v3`
- (b) Pin to a branch: `uses: third-party/action@main`
- (c) Pin to a full commit SHA: `uses: third-party/action@8ade135a41bc03ea155e62e844d188df1fd717b0`
- (d) Reference the HTTPS URL of the action.

---

## Chapter 6: Caching, Artifacts, & Action Integrations (Qs 39-44)

#### Q39. Caching Dynamic Dependencies
You set up a Cache Action for Python packages:
```yaml
- name: Cache dependencies
  uses: actions/cache@v4
  with:
    path: ~/.cache/pip
    key: ${{ runner.os }}-pip-${{ hashFiles('**/requirements.txt') }}
    restore-keys: |
      ${{ runner.os }}-pip-
```
You push a commit that modifies `requirements.txt` by adding `pandas`. What happens during the workflow run?
- (a) Cache hit: GHA restores the old cache and ignores `pandas` to save time.
- ==(b) Cache miss: `hashFiles` evaluates to a new value. GHA does not find the key, falls back to the restore key (restoring the old cache), runs `pip install` which quickly updates it with `pandas`, and saves a new cache under the new key at the end of the job.==
- (c) Syntax error: GHA does not allow multi-line strings in `restore-keys`.
- (d) Cache miss: The old cache is deleted completely, and all packages are re-downloaded from scratch.

#### Q40. Cache Size Limits in MLOps
You are caching trained model weights (approx. 14GB) using `actions/cache` to speed up deployment testing. What is the total storage limit for caches per repository, and what happens when you exceed it?
- (a) Limit is 2GB; GHA aborts the workflow run with a storage quota error.
- ==(b) Limit is 10GB; GHA will evict older caches using a Least Recently Used (LRU) policy until the total fits within the limit.==
- (c) Limit is 50GB; GHA bills your account for the extra storage.
- (d) There is no cache size limit for public repositories.

#### Q41. The Checkout Fetch Depth Trap
Your MLOps workflow has a step that calculates the code version dynamically using Git history (e.g. `git describe --tags`). The checkout step is defined as:
```yaml
- uses: actions/checkout@v4
```
The versioning script fails to find any parent tags or history. Why?
- (a) GHA runs checkout in a detached HEAD state where tags are deleted.
- ==(b) `actions/checkout` defaults to `fetch-depth: 1`, which only fetches the single latest commit (shallow clone), discarding git history and tags.==
- (c) The runner VM doesn't have Git installed.
- (d) GHA blockades all read-only git operations inside workflow VMs.

#### Q42. Caching vs Artifacts Lifetime
What is the fundamental functional difference between `actions/cache` and `actions/upload-artifact` in GHA?
- (a) Caches are used to pass data between jobs; Artifacts are used to save files.
- ==(b) Caches are preserved across different workflow runs to speed up dependencies; Artifacts are associated with a specific workflow run and are designed for downloading build/model outputs.==
- (c) Caches are private, whereas Artifacts are public.
- (d) Caches are stored in the repo; Artifacts are stored in S3.

#### Q43. Artifact Retention Limits
You upload your training plots and model binaries as artifacts. What is the default retention period for these artifacts before GHA automatically purges them?
- (a) 14 days
- (b) 30 days
- ==(c) 90 days==
- (d) 365 days

#### Q44. Submodule Checkout Trap
Your MLOps repository depends on a submodule named `data-utils` which holds your preprocessing code. Your step is:
```yaml
- uses: actions/checkout@v4
```
When you run `python preprocess.py`, it fails with `ModuleNotFoundError: No module named 'data_utils'`. Why?
- ==(a) `actions/checkout` does not check out submodules by default. You must pass `submodules: true` or `submodules: recursive` in the input configuration.==
- (b) Submodules are not supported on standard GHA runner architectures.
- (c) You must run `git pull submodules` manually in a separate step.
- (d) GHA requires submodules to be checked out inside a separate job.

---

## Chapter 7: Real-World "Bug Hunt" & YAML Debugging Scenarios (Qs 45-50)

#### Q45. The Multi-line Indentation Trap
Identify the syntax or parser error in this multiline script block:
```yaml
- name: Validate Model
  run: |
  python -c "import torch; print(torch.__version__)"
  pytest tests/smoke_test.py
```
- (a) The pipe character `|` is invalid on Windows systems.
- ==(b) The shell commands are not indented relative to the `run:` key, which breaks YAML formatting rules.==
- (c) Python inline execution `-c` must be written in a single-line step.
- (d) Double quotes are forbidden inside a multiline script block.

#### Q46. Missing Checkout on Pytest
This workflow fails instantly. Why?
```yaml
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.10'
      - name: Run Tests
        run: pytest tests/
```
- (a) `setup-python` requires a custom compiler path.
- ==(b) You forgot the `actions/checkout@v4` step. The runner VM workspace is completely empty; there are no files or `tests/` directory to run.==
- (c) `pytest` is not supported on `ubuntu-latest`.
- (d) The Python version must be enclosed in double quotes without single quotes.

#### Q47. The GitHub Context vs Env Variable Confusion
An engineer writes this workflow:
```yaml
env:
  STAGE: dev
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - name: Echo Stage
        run: echo "Deploying to ${{ STAGE }}"
```
What is printed in the logs, and why?
- (a) `Deploying to dev`
- ==(b) It crashes with a GHA parser error: `STAGE` is not defined in the `github` context. To access environment variables via expression syntax, you must write `${{ env.STAGE }}`.==
- (c) `Deploying to ` (empty string) because shell variables cannot be accessed via expression syntax.
- (d) It executes, but prompts a warning recommending using `$STAGE` directly.

#### Q48. Missing Needs Dependency Execution
Look at this YAML configuration:
```yaml
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - run: echo "Building..."
  deploy:
    runs-on: ubuntu-latest
    steps:
      - run: echo "Deploying..."
```
If you run this workflow, what is the execution sequence?
- (a) `build` runs, completes, and then `deploy` starts.
- (b) `build` and `deploy` run concurrently in parallel on separate VMs.
- (c) `deploy` fails because it does not have the `needs: build` parameter explicitly defined.
- (d) The workflow is rejected because you cannot have two jobs in a single YAML file.

#### Q49. The Double Curly Brackets Secret Access Trap
A student writes this deployment step:
```yaml
- name: Login to Docker
  run: docker login -u admin -p {{ secrets.DOCKER_PASSWORD }}
```
What is the result when parsing this workflow?
- (a) Perfect execution: the secret is expanded correctly.
- ==(b) It fails validation because the expression syntax must have **double** curly braces wrapped in a string with a dollar prefix: `${{ secrets.DOCKER_PASSWORD }}`.==
- (c) The step runs but passes the literal string `{{ secrets.DOCKER_PASSWORD }}` as the password, leaking nothing but failing the login.
- (d) The secret is successfully passed but it throws a warning.

#### Q50. The Custom Shell Script Permissions Trap
You checkout your codebase and try to run a custom build script that is in your repository:
```yaml
- name: Run Build
  run: ./scripts/build.sh
```
The step fails instantly with `Permission denied (error 13)` on `ubuntu-latest`. Why?
- (a) The script requires `sudo` privileges.
- ==(b) The file `build.sh` does not have executable permissions (+x) inside the Git tree. You must run `chmod +x ./scripts/build.sh` before running it, or invoke it via `bash ./scripts/build.sh`.==
- (c) GHA runners block custom shell scripts for security reasons.
- (d) You cannot execute scripts outside the root workspace directory.

---

## 🔑 Master Answer Key (With Deep-Dive Explanations)

### Chapter 1: Runner Architecture, Filesystems, & VM Persistence
* **Q1: (c)** **Explanation:** Each step runs in an entirely separate, sandboxed shell process. Exporting a variable in Step 1 only changes the environment of that step's shell. When the step ends, that shell process dies, and the variable is lost. To persist it, write it to `$GITHUB_ENV` (`echo "BATCH_SIZE=64" >> $GITHUB_ENV`).
* **Q2: (b)** **Explanation:** Jobs in GitHub Actions run on completely different virtual machines. The filesystem of Job 1's VM is discarded when Job 1 finishes. Job 2 boots on a clean VM. To pass files between jobs, you must use `actions/upload-artifact@v4` in Job 1 and `actions/download-artifact@v4` in Job 2.
* **Q3: (c)** **Explanation:** GitHub-hosted runners run as a standard user with passwordless `sudo` privileges enabled. You can run commands like `sudo apt-get install -y library` without providing a password.
* **Q4: (b)** **Explanation:** To persist a directory change to the system `PATH` across all subsequent steps, append it to the special GHA system file: `$GITHUB_PATH`. Writing `export PATH=...` only persists for the *current* step's shell.
* **Q5: (c)** **Explanation:** The default timeout for a GitHub Actions job is 360 minutes (6 hours). If your training code hangs, it will run for 6 hours, consuming 360 minutes of billing time. Always define `timeout-minutes: 15` (or a reasonable limit) for safety!
* **Q6: (b)** **Explanation:** The default shell on Windows runners in GitHub Actions is PowerShell Core (`pwsh`). While standard bash scripts might fail, `rm -rf` works on Linux/macOS bash but throws syntax/argument errors on PowerShell. You must define `shell: bash` on Windows to run bash commands natively.
* **Q7: (c)** **Explanation:** The runner workspace starts as a clean, empty directory. GHA does **not** automatically download your repository code. You must explicitly call `- uses: actions/checkout@v4` to populate the directory.
* **Q8: (b)** **Explanation:** Unlike Linux bash which runs GHA scripts with `set -e` (fail-fast), PowerShell Core running inside GHA has complex exit code tracking. If a middle command like `Get-Item` fails, it prints an error but continues executing the next line unless `$ErrorActionPreference = 'Stop'` is caught. If the final command `Write-Output` succeeds, the script returns exit code 0, masking the error! GHA resolves this by evaluating internal PowerShell execution parameters, but standard custom scripts often mask failures unless configured with `$ErrorActionPreference = 'Stop'`.

---

### Chapter 2: Advanced Triggers, Filtering, & Event Contexts
* **Q9: (b)** **Explanation:** If a push contains changes to both matched and ignored paths, the workflow **will** trigger because there is at least one file (`src/train.py`) that matches the triggering paths criteria.
* **Q10: (b)** **Explanation:** Reusable workflows are isolated. They do not inherit caller secrets unless you pass them explicitly under the `with` / `secrets` parameters, or pass `secrets: inherit` in the caller job.
* **Q11: (b)** **Explanation:** To prevent infinite recursive loops (where CI pushes code, triggering CI again, forever), commits pushed using the runner's default `GITHUB_TOKEN` do **not** trigger any new GitHub Actions workflow runs. If you *want* to trigger another workflow, you must push using a Personal Access Token (PAT).
* **Q12: (b)** **Explanation:** `workflow_run` triggers a workflow asynchronously after a separate workflow completes. The triggered workflow runs on the default branch config. A Reusable Workflow (`workflow_call`) is imported synchronously inline, acting exactly like a nested job inside the caller workflow run.
* **Q13: (c)** **Explanation:** The full event payload JSON is saved to a file on the runner VM disk. The absolute path to this file is stored in the environment variable `$GITHUB_EVENT_PATH`. You can read it in Python via `json.load(open(os.environ['GITHUB_EVENT_PATH']))`.
* **Q14: (b)** **Explanation:** When a branch is deleted, there is no longer a branch copy to parse. GHA looks for the `on: delete` workflow in the default branch (usually `main`) and executes that copy.
* **Q15: (a)** **Explanation:** When a workflow is triggered by `pull_request` from a fork, GitHub automatically downgrades the runner permissions: the `GITHUB_TOKEN` becomes strictly read-only, and all repository secrets are **completely redacted/empty**. The secret `API_KEY` cannot be read, protecting the base repository from exploitation.

---

### Chapter 3: Complex YAML Syntax, Job Needs, & Matrix Strategies
* **Q16: (c)** **Explanation:** A step in a GHA workflow cannot have both a `uses` and a `run` key simultaneously. Doing so violates GHA schema and will result in a syntax validation error.
* **Q17: (b)** **Explanation:** Since `job_b` has no `needs` dependencies, it starts immediately in parallel with `job_a`. `job_c` defines `needs: [job_a, job_b]`. Because `job_a` failed, `job_c` is immediately skipped.
* **Q18: (b)** **Explanation:** By default, matrix strategies have `fail-fast: true`. If any job in the matrix fails, GHA immediately cancels all other currently running and queued matrix jobs to save billing minutes.
* **Q19: (c)** **Explanation:** Step outputs are local to the job they run in. To access them in another job, you must explicitly bubble them up to the **Job Level Outputs** block in the YAML:
  ```yaml
  job_a:
    outputs:
      ACCURACY: ${{ steps.calc.outputs.ACCURACY }}
  ```
* **Q20: (c)** **Explanation:** The `include` key adds a value or overrides configuration for a combination that *already exists* in the matrix. It does not spawn a new 5th job; it matches the existing `os: ubuntu-latest` + `python: '3.10'` combination and appends `gpu: true` to it. Total jobs: 4 (2x2 matrix).
* **Q21: (d)** **Explanation:** In the `if:` key, you do not need to wrap expressions in `${{ }}`. GHA automatically treats the value of the `if:` key as an expression. While wrapping it might execute on some versions, it triggers warnings or parsing quirks and is strongly discouraged.
* **Q22: (b)** **Explanation:** Expressions are evaluated raw before the shell command runs. If the expanded text contains quotes or shell control characters, it will break the shell command execution structure, resulting in a shell parser error.
* **Q23: (a)** **Explanation:** If you provide only a subset of matrix keys in `exclude` (e.g. only `os: macos-latest`), it excludes **all** combinations containing `os: macos-latest`.

---

### Chapter 4: Conditional Execution & Status Check Functions
* **Q24: (b)** **Explanation:** If a workflow is cancelled, standard jobs and steps stop. The `failure()` status check function evaluates to `true` if previous steps failed, but it returns `false` if the job was cancelled. To run a cleanup step on cancellation or failures alike, use `if: always()`.
* **Q25: (b)** **Explanation:** If a custom `if` condition does not contain an explicit status check function, GHA automatically appends `&& success()` to it under the hood. So `if: env.RUN_TESTS == 'true'` becomes `if: success() && env.RUN_TESTS == 'true'`. Since the previous step failed, this step is skipped.
* **Q26: (c)** **Explanation:** If a step has `continue-on-error: true` and fails: the **outcome** is `failure` (representing the real script exit status), but the **conclusion** is `success` (representing the GHA workflow status). The job proceeds normally.
* **Q27: (a)** **Explanation:** When a job is cancelled or times out, it goes into a cancelled state. GHA executes steps with `always()` and steps with `cancelled()`.
* **Q28: (c)** **Explanation:** GHA's parser automatically injects the `success()` condition if no status checks are present. Thus, writing `if: github.event_name == 'push'` implicitly includes `success()`. Explicitly adding it is functionally identical.
* **Q29: (b)** **Explanation:** Status functions operate context-dependently. At the Job level, `success()` checks the status of all `needs` jobs. At the Step level, it checks the status of previous steps in the same job.
* **Q30: (b)** **Explanation:** Because `always()` is explicitly checked, the step is status-blind. It will run regardless of previous failures, provided that the training step ran and generated the expected output matching `'complete'`.

---

### Chapter 5: Security, Secrets, Fork Restrictions, & Token Permissions
* **Q31: (b)** **Explanation:** GitHub Action's secret masking is naive and search-based. It scans stdout/stderr for exact matches of configured secrets and replaces them with `***`. Because the database secret is `prod`, every occurrence of the string `prod` in the logs (including inside the word "production") gets masked as `***uction`. **Best Practice:** Avoid extremely short or common words as secrets!
* **Q32: (b)** **Explanation:** Command-line arguments are visible to any process running on the host system (via process listing tools like `ps` or `/proc`). If a third-party action is compromised, it can read your secret from the command line process tree. Pass secrets via environment variables (`env:`) instead, which are isolated to that process environment.
* **Q33: (b)** **Explanation:** GHA masks the exact string of the secret. If you pipe the secret into `base64`, the output stream contains the base64 encoded representation (e.g. `U3VwZXJTZWNyZXQ=`), which does not match the plain-text secret. GHA will print this encoded string unmasked. A malicious script can easily leak secrets by encoding them first.
* **Q34: (c)** **Explanation:** Default permissions vary depending on organization or repository settings. GITHUB_TOKEN may default to full read-write access. **Security Standard:** Always explicitly declare read-only permissions in your YAML:
  ```yaml
  permissions:
    contents: read
  ```
* **Q35: (b)** **Explanation:** `pull_request_target` executes in the context of the base repository and has full access to secrets. If the workflow checks out the PR fork code and runs test scripts from it, a malicious PR contributor can inject code to extract and upload secrets to an external server.
* **Q36: (b)** **Explanation:** GHA's log-masking filter scans all standard output streams. Even if you write the secret to a file and later `cat` that file, GHA intercepts the stdout stream and replaces the secret content with `***`.
* **Q37: (b)** **Explanation:** Environment-specific configurations take precedence. GHA prioritizes secrets defined within the active target environment over repository-level secrets of the same name.
* **Q38: (c)** **Explanation:** Community tags (like `v3` or `main`) can be moved or hijacked. Pinning to a specific git commit SHA (e.g. `8ade135...`) ensures you are running the exact, audited code, preventing supply chain attacks.

---

### Chapter 6: Caching, Artifacts, & Action Integrations
* **Q39: (b)** **Explanation:** When `requirements.txt` changes, the cache key becomes a miss. GHA uses the `restore-keys` fallback to load the older cache. Pip uses this old cache to perform an incremental install (only downloading `pandas`), and GHA saves the newly updated cache under the new key at the end of the run.
* **Q40: (b)** **Explanation:** GitHub limits total cache storage to 10GB per repository. If this limit is exceeded, GHA automatically deletes older caches using an LRU eviction policy.
* **Q41: (b)** **Explanation:** `actions/checkout` defaults to a fetch depth of 1 (shallow clone) to maximize performance. If versioning tools need historical commits or tags to determine build releases, you must explicitly set:
  ```yaml
  with:
    fetch-depth: 0 # Fetches all history and tags
  ```
* **Q42: (b)** **Explanation:** Caching is designed to share dependency directories *across different workflow runs* to optimize build times. Artifacts are designed to preserve specific output assets of a *single workflow run* (such as trained model files or reports) for manual download or downstream jobs.
* **Q43: (c)** **Explanation:** By default, GHA preserves uploaded artifacts for 90 days before deletion. You can configure a shorter retention period using `retention-days: 1` in the `upload-artifact` step.
* **Q44: (a)** **Explanation:** By default, `actions/checkout` ignores submodules. You must explicitly configure:
  ```yaml
  with:
    submodules: true
  ```

---

### Chapter 7: Real-World "Bug Hunt" & YAML Debugging Scenarios
* **Q45: (b)** **Explanation:** YAML is whitespace-sensitive. Commands under a multi-line pipe block `run: |` must be indented relative to the `run:` key (usually by 2 spaces).
* **Q46: (b)** **Explanation:** The workflow fails because there is no checkout step. The runner VM starts with an empty working directory.
* **Q47: (b)** **Explanation:** GHA evaluates expression syntax `${{ STAGE }}` inside the GHA parser context before executing the command. Since `STAGE` is an environment variable on the runner (not a GHA context variable), it will throw a parser error. The correct expression is `${{ env.STAGE }}` or referencing it as a shell variable `$STAGE` directly.
* **Q48: (b)** **Explanation:** If no `needs` dependency is specified, GHA executes all listed jobs in parallel concurrently, provided runner machines are available.
* **Q49: (b)** **Explanation:** GitHub Actions uses `${{ }}` for expressions. A single curly brace `{ }` is treated as standard YAML or string literal characters and will fail validation or pass plain text.
* **Q50: (b)** **Explanation:** Git does not preserve file execution flags (+x) unless configured. To execute `./scripts/build.sh`, you must first run `chmod +x ./scripts/build.sh` or run it as an argument to bash: `bash ./scripts/build.sh`.

---

## 💡 Summary of Core GHA Exam Gotchas
1. **Scope Boundaries:** Steps share a VM, Jobs do not.
2. **Persistence:** Write to `$GITHUB_ENV` for steps, use `upload/download-artifact` for jobs.
3. **Implicit `success()`:** Custom `if` statements implicitly require `success()` unless you explicitly add status check functions like `always()` or `failure()`.
4. **Fork Security:** Fork PRs run on read-only tokens and have absolutely **zero** access to repository secrets.
5. **No `uses` and `run` together:** A single step cannot contain both keywords.
