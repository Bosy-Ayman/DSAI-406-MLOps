# Assignment 6

## Implementation 

Current CI/CD configurations demonstrate a lack of resource governance, leading to non-trivial compute expenditures on suboptimal or erroneous code branches. Specifically, expensive GPU-accelerated jobs are triggered regardless of the branch's integrity or the necessity of the run Re-engineer the `workflow.yaml` to implement strict conditional execution. The system must enforce a "Gatekeeper" logic to prevent resource allocation for broken code or unauthorized development branches.

1. Modify your workflow so that the `train` job (the expensive one) only runs if all three of these conditions are met:
   - Dependency: A lightweight `linter` job must pass first
   - Branch Protection: The code must be on the `main` branch
   - Manual Intent: The commit message must contain the keyword `[run-train]`

2. If the `train` job fails, the pipeline must not just stop
   - Create a step that only runs on `failure()`
   - Upload a file named `error_logs.txt` as a GHA Artifact so the developer can investigate the issue without re-running the GPU

3. Create a final step using `always()` that prints "Cleaning up temporary cloud volumes..." to the console, regardless of success or failure

**Tasks:** You need to submit the following: 

1. Your final `pipeline.yaml` file
2. A screenshot of the GitHub Actions UI showing a Skipped training job (where the commit message lacked the `[run-train]` tag)
