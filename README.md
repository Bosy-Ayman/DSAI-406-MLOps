#  Machine Learning Engineering for Production (MLOps) (DSAI 406) - 2025-2026

Repository for the MLOps undergraduate course (DSAI 406) for the 2025-2026 academic year at Zewail City University. 

---

### Logistics

Course | MLOps - DSAI 406
---|----
Webpage| [https://github.com/m-fakhry/DSAI-406-MLOps](https://github.com/m-fakhry/DSAI-406-MLOps)
Structure | 2-hour lecture (Mon 10-12) and 3-hour lab (Sun 8-11, Tue 10-1, 1-4, Wed 1-4, Thu 11-2)
TAs | Aya Nageh and Osama Ghandour
Grades | (final), (midterm and quizzes), (lab)
Lab Policy| Assignments and quizzes
Book | "_Practical MLOps: Operationalizing Machine Learning Models_", Noah Gift and Alfredo Deza, 2021
Supplementary Book | "_Reliable Machine Learning: Applying SRE Principles to ML in Production_", Cathy Chen, Niall Richard Murphy, Kranti Parisa, D. Sculley, and Todd Underwood, 2022
Other Resourse | [Indian Institute of Technology Course](https://study.iitm.ac.in/ds/course_pages/BSDA5014.html)
Objective | Streamlining ML workflows through automation, including data management, model training, continuous integration/delivery, and monitoring to ensure reliability and efficiency. Students learn to build scalable pipelines using tools like MLflow, Docker, and cloud platforms, with focusing on reproducibility and real-world adaptability.
Prerequitstis | Machine Learning, Deep Learning, PyTorch

---
### Topics

- Intro: what is MLOps, tasks for MLOps engineer, difference between MLOps and DevOps.
- ML Pipelines & Data Management: Overview of data engineering tools and practices, data management principles for ML models, ML pipeline automation
- ML Life cycle
- Tracking model training & experimentation using MLFlow and Tensorboard, hyperparameter tuning and optimization.
- MLOps Tools and Version Control
	- Github 
	- CI/CD: continuous integration and delivery, github actions
	- Containers: environment, containers, docker files and structure, 
- Model Serving Architectures: python packaging: microservices 
- Cloud MLOps
- Monitoring and Observability for Models: Monitoring and logging for ML models in production, techniques for monitoring model performance in production, logging and error tracking for ML systems, performance optimization and scaling strategies
- Governance: Fairness, privacy and responsible AI 


---
### Lectures

Week| Date |Topic | Contents | Lecture | Assignment
---|---|---|---|---|---
1| 02-09 | | | | 
2| 02-16 | Introduction | Model development, DevOps, DataOps, MLOps | [Lecture 1](lectures/lec1.md) | [Assignment 1](assignments/assign1.md)
3| 02-23 | Reproducibility | Conda, Git, Docker | [Lecture 2](lectures/lec2.md) | [Assignment 2](assignments/assign2.md)
4| 03-02 | Tracking | MLflow, tracking API, experiments, runs, metrics, artifacts  | [Lecture 3](lectures/lec3.md) | [Assignment 3](assignments/assign3.md)
5| 03-09 | CI/CD | Continuous integration and delivery, github actions, anatomy of a workflow yaml file, dependencies | [Lecture 4](lectures/lec4.md) | [Assignment 4](assignments/assign4.md)
6| 03-16 | | | | 
7| 03-23 | Eid | | | 
8| 03-30 | Midterm? | | | 
9| 04-06 | | | | 
10| 04-13 | Sham El Nessim? | | | 
11| 04-20 | | | | 
12| 04-27 | | | | 
13| 05-04 | | | | 
14| 05-11 | | | | 
15| 05-18 | Prepare for Final | | | 

Please note that the syllabus content is subject to change throughout the semester. Topics may be added or removed based on the instructor’s discretion, student progress, and available time. Your feedback and participation will inform these adjustments to ensure alignment with course goals and schedule constraints.

--- 

### Grading Policy 

Topic| Percentage | Notes
---|---|---
Lab Assignments | 15% |
Final Lab | 10% | 
Quizzes | 15% | 
Midterm | 20% | 
Final | 40% | 
