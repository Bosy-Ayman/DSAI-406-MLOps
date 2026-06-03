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

---

## Architecture & Design

```mermaid
graph TD
    User([Browser / External User]) -->|NodePort: 30085| ServiceWeb[streamlit-service <br> NodePort]
    ServiceWeb -->|Routing port: 8501| WebPod1[streamlit-pod-1]
    ServiceWeb -->|Routing port: 8501| WebPod2[streamlit-pod-2]
    ServiceWeb -->|Routing port: 8501| WebPod3[streamlit-pod-3]
    
    WebPod1 -->|K8s DNS: http://ai-service:5000| ServiceAI[ai-service <br> ClusterIP]
    WebPod2 -->|K8s DNS: http://ai-service:5000| ServiceAI
    WebPod3 -->|K8s DNS: http://ai-service:5000| ServiceAI
    
    ServiceAI -->|Routing port: 5000| AIPod1[generator-pod-1]
    ServiceAI -->|Routing port: 5000| AIPod2[generator-pod-2]

    style User fill:#ffe0b2,stroke:#e65100,stroke-width:2px
    style ServiceWeb fill:#bbdefb,stroke:#0d47a1,stroke-width:2px
    style ServiceAI fill:#f8bbd0,stroke:#880e4f,stroke-width:2px
    style WebPod1 fill:#e8f5e9,stroke:#1b5e20,stroke-width:2px
    style WebPod2 fill:#e8f5e9,stroke:#1b5e20,stroke-width:2px
    style WebPod3 fill:#e8f5e9,stroke:#1b5e20,stroke-width:2px
    style AIPod1 fill:#e0f7fa,stroke:#006064,stroke-width:2px
    style AIPod2 fill:#e0f7fa,stroke:#006064,stroke-width:2px
```

### 1. Multi-Service Microservices Architecture
This setup represents a **Multi-Service Microservices Kubernetes Architecture** isolating the UI layer from the AI inference engine:
- **Frontend Layer**: 
  - Deployments: [deployment_web.yaml](file:///c:/Users/pouss/Documents/CSAI/4th%20Year/Spring/DSAI-406-MLOps/Assignments/Assignment-9/deployment_web.yaml) keeps **3 replicas** of the Streamlit application running.
  - Service: [service_web.yaml](file:///c:/Users/pouss/Documents/CSAI/4th%20Year/Spring/DSAI-406-MLOps/Assignments/Assignment-9/service_web.yaml) exposes the frontend externally using `NodePort` on port `30085`.
- **AI Inference Layer**:
  - Deployments: [deployment_ai.yaml](file:///c:/Users/pouss/Documents/CSAI/4th%20Year/Spring/DSAI-406-MLOps/Assignments/Assignment-9/deployment_ai.yaml) maintains **2 replicas** of the StyleGAN generator inference application.
  - Service: [service_ai.yaml](file:///c:/Users/pouss/Documents/CSAI/4th%20Year/Spring/DSAI-406-MLOps/Assignments/Assignment-9/service_ai.yaml) exposes the backend internally using `ClusterIP` on port `5000`. This isolates the AI pods from external internet traffic for security and cost efficiency.

### 2. Service Discovery & Core DNS
The frontend container talks to the backend via standard **Kubernetes DNS Resolution**. 
- K8s cluster includes an internal CoreDNS resolver mapping the service name `ai-service` to its stable internal Virtual IP `10.96.93.30`. 
- The Streamlit Python code issues requests to `http://ai-service:5000/predict` which resolves internally and load balances to one of the active backend pods.

### 3. Local Image Building & Registry loading
Because the original manifests referenced private or mock remote Docker images (`almond/...:latest`), standard deploys resulted in `ImagePullBackOff`. We resolved this by building local mock services directly inside Minikube:
- **Local build command**:
  ```bash
  minikube image build -t almond/stylegan-inference:latest ./backend
  minikube image build -t almond/streamlit-k8s-demo:latest ./frontend
  ```
- **Manifest adjustments**:
  - `imagePullPolicy: IfNotPresent` was added to both deployment manifests to prevent K8s from trying to pull from Docker Hub.
  - Resource requests for the AI backend were scaled down to **200m CPU / 512Mi Memory** to prevent OOM / scheduling blocks on a single-node local cluster.
