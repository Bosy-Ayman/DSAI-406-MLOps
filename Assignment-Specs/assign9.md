# Assignment 9

## Implementation 

**Objective:** Get the PersonaCanvas frontend **AND backend** running on your local machine using Kubernetes.

**Task List:**
1.  Environment: Start your cluster using `minikube start`.
2.  Deployment: Create two `deployment.yaml` files (one for the web app and one for the AI app) and apply it to run 3 replicas of the web app and 2 instances of the AI app. Each one has difference resources. 
3.  Networking: Create `service_web.yaml` for the web app as a `NodePort` to expose the app.
4.  Networking: Create `service_ai.yaml` for the AI app to expose the service for internal use.
5.  Make sure that the web app can talk to the AI app as explained in the lecture. 
6.  Verification: Use `kubectl get pods` to ensure all pod instances are "Running."

**Success Criteria:**
While this assignment is for practice (not graded), a professional submission would include a screenshot of the app running in your browser:
