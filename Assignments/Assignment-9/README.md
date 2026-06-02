# Assignment 9: Kubernetes Frontend + Backend (Multi-Service)

## How to run:

1. **Start Minikube cluster:**
   ```bash
   minikube start
   ```

2. **Apply resources:**
   - Deploy backend AI model first:
     ```bash
     kubectl apply -f deployment_ai.yaml
     kubectl apply -f service_ai.yaml
     ```
   - Deploy frontend Streamlit application:
     ```bash
     kubectl apply -f deployment_web.yaml
     kubectl apply -f service_web.yaml
     ```

3. **Verify Deployment & Pods status:**
   ```bash
   kubectl get deployments
   kubectl get services
   kubectl get pods -o wide
   ```

4. **Verify Internal Communication:**
   The frontend Streamlit app accesses the backend generator using standard Kubernetes DNS:
   `http://ai-service:5000/predict` (since ClusterIP maps `ai-service` internally).

5. **Expose the Web Frontend to your browser:**
   ```bash
   minikube service streamlit-service
   ```
