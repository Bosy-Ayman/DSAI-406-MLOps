# Assignment 8

## Implementation 

**Objective:** Get the PersonaCanvas frontend running on your local machine using Kubernetes.

**Task List:**
1.  Environment: Start your cluster using `minikube start`.
2.  Deployment: Create `deployment.yaml` and apply it to run 3 replicas of the app.
3.  Networking: Create `service.yaml` as a `NodePort` to expose the app.
4.  Verification: Use `kubectl get pods` to ensure all 3 instances are "Running."

**Success Criteria:**
While this assignment is for practice (not graded), a professional submission would include a screenshot of the app running in your browser:
```bash
minikube service frontend-service
```

**Notes:**
- Keep the terminal window open while the minikube service is running.
- Try 'kubectl delete pod' to see the self-healing in action.
