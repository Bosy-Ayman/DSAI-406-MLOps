

```yaml

name: ML CI-CD Pipeline

on:
  push:

jobs:
  lint:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.10"

      - name: Install dependencies
        run: pip install -r requirements.txt

      - name: Run lint
        run: flake8 src/

  train:
    needs: lint
    runs-on: ubuntu-latest

    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.10"

      - name: Install dependencies
        run: pip install -r requirements.txt

      - name: Train model
        run: python train.py

      - name: Save model artifact
        uses: actions/upload-artifact@v4
        with:
          name: model
          path: model.pkl

  deploy:
    needs: train
    runs-on: ubuntu-latest

    if: success() && github.ref == 'refs/heads/main'

    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Download model artifact
        uses: actions/download-artifact@v4
        with:
          name: model

      - name: Build Docker image
        run: docker build -t myapp:latest .

      - name: Login to Docker Hub
        run: echo "${{ secrets.DOCKER_PASSWORD }}" | docker login -u "${{ secrets.DOCKER_USERNAME }}" --password-stdin

      - name: Push Docker image
        run: |
          docker tag myapp:latest myrepo/myapp:latest
          docker push myrepo/myapp:latest
```


---

```yaml

name: Gatekeeper CI/CD Pipeline

on:
  push:
    branches:
      - "*"

jobs:
  code-check:
    name:  Linter
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v4

      - name: Run linter
        run: |
          echo "Running lint checks..."
          echo "No issues found"

  model-training:
    name: Training Job
    needs: code-check
    runs-on: ubuntu-latest

    if: >
      needs.code-check.result == 'success' &&
      github.ref_name == 'main' &&
      contains(github.event.head_commit.message, '[run-train]')

    steps:
      - uses: actions/checkout@v4

      - name: Run training
        run: |
          echo "Training started..ert"
          echo "Simulating failurde.."
          exit 1

      - name: Create error logs (on failure)
        if: failure()
        run: echo "Training failed logs" > error_logs.txt

      - name: Upload logs
        if: failure()
        uses: actions/upload-artifact@v4
        with:
          name: error_logs
          path: error_logs.txt

      - name: Cleanup resources
        if: always()
        run: echo "Cleaning up .."


  training-status:
    name: Training Status Report
    runs-on: ubuntu-latest
    needs: model-training
    if: always()

    steps:
      - name: Show final status
        run: |

          if [ "${{ needs.model-training.result }}" = "success" ]; then
            echo "STATUS: SUCCESS"
          elif [ "${{ needs.model-training.result }}" = "failure" ]; then
            echo "STATUS: FAILURE"
          else
            echo "STATUS: SKIPPED"
          fi

```