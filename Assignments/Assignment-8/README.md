# Assignment 8: Kubernetes Frontend Deployment

## How to run:

1. **Start Minikube cluster:**
   ```bash
   minikube start
   ```

2. **Apply resources:**
   ```bash
   kubectl apply -f deployment.yaml
   ```
   ```bash
   kubectl apply -f service.yaml
   ```

3. **Verify Deployment & Pods status:**
   ```bash
   kubectl get deployments
   kubectl get pods -o wide
   ```

4. **Verify Service access:**
   ```bash
   minikube service frontend-service
   ```
