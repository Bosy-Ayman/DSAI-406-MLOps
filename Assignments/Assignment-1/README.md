# Assignment 1: The Reproducibility Problem

The goal of this assignment is to experience firsthand the core challenges of machine learning engineering without MLOps governance: the **Reproducibility Problem**.

---

## Concept & Pitfalls

When multiple data scientists run machine learning code on different systems without orchestration, they run into three main categories of reproducibility failure:

| Failure Type | Pitfall Description | MLOps Solution |
|--------------|---------------------|----------------|
| **Dependency Hell** | Mismatch in libraries (e.g. PyTorch or Scikit-Learn versions) causes code runtime exceptions or silent drift. | Conda Environments & Docker Containers |
| **Non-Deterministic Runs** | Model parameters initialization and data shuffling generate different accuracy results on each run. | Explicit random seed fixing (`torch.manual_seed(42)`) |
| **Environment Leakage** | Hardcoded file paths (e.g. `/home/user/data/mnist.csv`) and direct local asset reads make code non-portable. | Relativized directory layouts and environment variables (`os.getenv`) |

---

## System Architecture

```
                 [ User A - Local Python (Python 3.9) ] 
                                  │
                                  ▼ (Hardcoded Path: C:/Users/...)
                             [ train.py ]  ──> Random Seed: None ──> Result: Accuracy 89.2%
                                  │
                                  ▼
                 [ User B - Local Python (Python 3.10) ]
                                  │
                                  ▼ (Path Error: File Not Found!)
                             [ train.py ]  ──> Random Seed: None ──> Result: Crash! / Accuracy 91.5%
```

Without strict version control, code execution dependencies, and deterministic initialization, a machine learning project behaves like a black box that cannot be integrated into automated production pipelines.
