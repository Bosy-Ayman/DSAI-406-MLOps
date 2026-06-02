Here are **doctor-style MCQ questions** designed to trap common misunderstandings in Kubeflow + YAML + pipelines. I’ll include the **correct answer + why the other options are traps**.

---

# 🧠 MCQ 1 — What is `prep_task`?

```python
prep_task = preprocess_data(data_path=data_path)
```

### Q: What does `prep_task` represent?

A. The cleaned dataset file  
B. The execution result of preprocessing  
==C. A pipeline node (task in DAG)==  
D. A Python variable holding data in memory

### ✅ Correct Answer: C

### 🔥 Trap explanation:

- A ❌: that’s `prep_task.outputs[...]`
    
- B ❌: execution hasn’t happened yet
    
- D ❌: nothing is executed at definition time  
    👉 It is just a **graph node**
    

---

# 🧠 MCQ 2 — What is `prep_task.outputs["cleaned_data"]`?

A. A real file already created  
==B. A pointer to future output artifact==  
C. A cached memory object  
D. The input dataset

### ✅ Correct Answer: B

### 🔥 Trap:

- A ❌: file doesn’t exist yet at definition time
    
- C ❌: not memory, it's metadata reference
    
- D ❌: input is `data_path`
    

---

# 🧠 MCQ 3 — Why use OutputPath?

A. To return Python variables  
B. To enable shared storage between containers  
C. To speed up training  
D. To compress data automatically

### ✅ Correct Answer: B

### 🔥 Trap:

- A ❌: Kubeflow does not return values like normal Python
    
- C ❌: indirect benefit, not the purpose
    
- D ❌: compression is unrelated
    

---

# 🧠 MCQ 4 — What happens if preprocess succeeds once?

A. It always reruns  
B. It is deleted immediately  
==C. It may be reused via cache==  
D. It becomes a Python variable

### ✅ Correct Answer: C

### 🔥 Trap:

- A ❌: wrong if caching enabled
    
- B ❌: outputs stored in artifact store
    
- D ❌: still not Python memory
    

---

# 🧠 MCQ 5 — What is Kubeflow pipeline compiled into?

```python
compiler.Compiler().compile(...)
```

A. Python bytecode  
B. Docker image  
==C. YAML specification==  
D. JSON database

### ✅ Correct Answer: C

### 🔥 Trap:

- A ❌: Python is only for definition
    
- B ❌: images used inside components, not pipeline itself
    
- D ❌: not primary format
    

---

# 🧠 MCQ 6 — If training uses:

```python
lr=0.01
```

and we change to:

```python
lr=0.001
```

What happens?

A. Whole pipeline is cached  
B. Only preprocess reruns  
==C. Train reruns, preprocess may be cached==  
D. Nothing reruns ever

### ✅ Correct Answer: C

### 🔥 Trap:

- A ❌: parameters affect cache key
    
- B ❌: preprocess independent of lr
    
- D ❌: always re-evaluated
    

---

# 🧠 MCQ 7 — Why does Kubeflow avoid moving large data like GitHub Actions?

A. Because YAML cannot handle files  
==B. Because it uses Persistent Volumes==  
C. Because it deletes artifacts  
D. Because it runs on CPU only

### ✅ Correct Answer: B

### 🔥 Trap:

- A ❌: YAML is not the limitation
    
- C ❌: opposite is true (stores artifacts)
    
- D ❌: Kubeflow supports GPU
    

---

# 🧠 MCQ 8 — What is the role of `.outputs`?

A. Stores real-time logs  
==B. Defines dependency between tasks==  
C. Executes training  
D. Converts data types

### ✅ Correct Answer: B

### 🔥 Trap:

- A ❌: logs are separate system
    
- C ❌: execution happens later
    
- D ❌: no type conversion
    

---

# 🧠 MCQ 9 — What is cached in Kubeflow?

A. Whole pipeline script  
B. Only final model  
==C. Component outputs==  
D. Kubernetes cluster state

### ✅ Correct Answer: C

### 🔥 Trap:

- A ❌: not code caching
    
- B ❌: model is just one possible output
    
- D ❌: unrelated system-level state
    

---

# 🧠 MCQ 10 — What does Kubeflow optimize most?

A. Python execution speed  
B. Network bandwidth only  
==C. ML workflow execution + resource scheduling==  
D. Git versioning

### ✅ Correct Answer: C

### 🔥 Trap:

- A ❌: not its goal
    
- B ❌: only part of system
    
- D ❌: handled by GitHub
    

---

# 🧠 FINAL “DOCTOR TRAP” QUESTION (VERY IMPORTANT)

### Q: If `prep_task.outputs["cleaned_data"]` is used, what is actually passed?

A. A file  
B. A memory object  
==C. A DAG dependency link==  
D. A Python return value

### ✅ Correct Answer: C

---

# 🎯 ONE SENTENCE YOU MUST REMEMBER FOR EXAM

> Kubeflow does NOT pass data like Python — it passes **dependencies between nodes in a DAG**, and data is resolved only at execution time.
