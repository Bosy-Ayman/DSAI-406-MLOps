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

---

## Architecture & Design

```mermaid
graph LR
    User([Browser / External User]) -->|NodePort: 30085| Service[frontend-service <br> NodePort]
    Service -->|Routing port: 8501| Pod1[streamlit-pod-1]
    Service -->|Routing port: 8501| Pod2[streamlit-pod-2]
    Service -->|Routing port: 8501| Pod3[streamlit-pod-3]
    
    style User fill:#ffe0b2,stroke:#e65100,stroke-width:2px
    style Service fill:#bbdefb,stroke:#0d47a1,stroke-width:2px
    style Pod1 fill:#e8f5e9,stroke:#1b5e20,stroke-width:2px
    style Pod2 fill:#e8f5e9,stroke:#1b5e20,stroke-width:2px
    style Pod3 fill:#e8f5e9,stroke:#1b5e20,stroke-width:2px
```

### 1. Kubernetes Workload Routing
This setup represents a **Single-Service Kubernetes Architecture**:
- **Workload Deployment**: [deployment.yaml](file:///c:/Users/pouss/Documents/CSAI/4th%20Year/Spring/DSAI-406-MLOps/Assignments/Assignment-8/deployment.yaml) defines the Streamlit frontend. It is scaled to **3 replicas** for high availability. 
- **Resource Constraints**: Each Streamlit pod requests `250m` CPU & `256Mi` memory, limited to `500m` CPU & `512Mi` memory. Exceeding the memory limit will result in Kubernetes killing the pod via OOM (Out Of Memory), while exceeding CPU limits will only result in throttling (slowing down).
- **Service Gateway**: [service.yaml](file:///c:/Users/pouss/Documents/CSAI/4th%20Year/Spring/DSAI-406-MLOps/Assignments/Assignment-8/service.yaml) defines a `NodePort` service. It provides a static entry point that listens on port `80` internally and binds to port `30085` on each minikube cluster node. 
- **Traffic Forwarding**: When a user accesses `http://<Node-IP>:30085`, the NodePort intercepts the request, routes it internally through the Service on port `80`, and load balances the traffic to port `8501` on one of the running pods matching the selector label `app: streamlit-web`.
- **Local Settings (`imagePullPolicy`)**: The deployment has `imagePullPolicy: IfNotPresent` specified to use the image built locally in minikube's Docker registry instead of requesting authentication for a private/remote registry on Docker Hub.
