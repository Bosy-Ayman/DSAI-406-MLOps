# Assignment 4

## Reading 

- Read Chapter 4 from the main book 


## Implementation 

**Objective**: Move from manual execution to automated validation by fixing and completing a GitHub Actions pipeline. 

- Create a new file in your repository at `.github/workflows/ml-pipeline.yml`. Copy and paste the code below. 

    ```yaml
    # .github/workflows/ml-pipeline.yml
    name: ML Model CI

    on:
        push:
            branches: main
        pull_request:

    jobs:
        validate-and-test:
            runs-on: ubuntu-latest
            steps:                
                - name: Set up Python
                    uses: actions/setup-python@v5
                    with:
                        python-version: '3.10'

                - name: Install Dependencies
                    run: pip install -r requirements.txt

                - name: Linter Check

                - name: Model Dry Test
                    run: |
                    python -c "import torch; print('Model environment ready!')"
    ```

- **Tasks**: 

  - Create a PDF report detailing all bugs in the yaml file and how it is solved. Your report should show 
    - Provide the GitHub link to your public repository.
    - Provide a screenshot of your GitHub "Actions" tab showing a successful (Green) run.
  - Modify the `on:` trigger to ensure that the pipeline runs on every `push` for all branches except `main`.
  - Add a final step to the job that uploads your project's README.md as an github artifact named `project-doc`.


- **Grading Rubric:**
  - Syntax Fixes (30): All bugs are reported 
  - Workflow Logic (30): Correctly configured `on` triggers.
  - Artifact Implementation (20): used the proper action with proper name and path.
  - Evidence and Reflection (20): Provided clear screenshot of "Green Check" and a logical explanation in README.

