Perfect — this is exactly how you get good at this 🔥
I’ll give you **tricky exam-style scenarios**. You say: **RUN / SKIP + why**

---

# 🧪 Rules reminder (you’ll need them)

* default = `if: success()`
* writing `if:` removes that default
* `success()` = all previous (steps/jobs) succeeded
* `failure()` = something failed before
* `needs.X.result` = specific job result

---

# 🧩 Question 1

```yaml
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - run: exit 1

  deploy:
    needs: build
    runs-on: ubuntu-latest
```

👉 Does `deploy` run?
**asnwer:** Skip

---

# 🧩 Question 2

```yaml
deploy:
  needs: build
  if: github.ref == 'refs/heads/main'
```

### Case:

* branch = main
* build FAILED ❌

👉 RUN or SKIP?
**answer:** Run , because there is no if success() in the condition

---

# 🧩 Question 3

```yaml
deploy:
  needs: build
  if: success() && github.ref == 'refs/heads/main'
```

### Case:

* branch = main
* build FAILED ❌

👉 RUN or SKIP?
**Answer:** skip

---

# 🧩 Question 4

```yaml
steps:
  - name: Step1
    run: exit 1

  - name: Step2
    if: failure()
    run: echo "recover"
```

👉 Does Step2 run?
**Answer:** RUN 

---

# 🧩 Question 5

```yaml
steps:
  - name: Step1
    run: exit 1

  - name: Step2
    if: github.ref == 'refs/heads/main'
    run: echo "hello"
```

### Case:

* branch = main

👉 RUN or SKIP?
**Answer:** RUN

---

# 🧩 Question 6

```yaml
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - run: exit 1

  train:
    needs: test
    if: success()
```

👉 Does `train` run?
**Answer:** Skip

---

# 🧩 Question 7 (VERY TRICKY)

```yaml
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - run: exit 1

  train:
    needs: test
    if: needs.test.result == 'success'
```

👉 RUN or SKIP?
**Answer:** SKIP
- `needs.test.result` = `"failure"`

```
failure == success → false
```
Therefore skipped

---

# 🧩 Question 8

```yaml
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - run: exit 1

  train:
    needs: test
    if: failure()
```

👉 RUN or SKIP?
**Answer:** RUN
because test ==  failure

---

# 🧩 Question 9 (MULTIPLE NEEDS)

```yaml
jobs:
  linter:
    steps:
      - run: echo ok

  test:
    steps:
      - run: exit 1

  train:
    needs: [linter, test]
    if: success()
```

👉 RUN or SKIP?
**Answer:** SKIP
because
linter == success
test == failure

---

# 🧩 Question 10 (FINAL BOSS 😈)

```yaml
jobs:
  linter:
    steps:
      - run: echo ok

  test:
    steps:
      - run: exit 1

  train:
    needs: [linter, test]
    if: needs.linter.result == 'success'
```

👉 RUN or SKIP?
**Answer**: RUN

needs.linter.result ==  'success'

