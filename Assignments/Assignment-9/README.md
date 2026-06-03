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

## Technical Solution & Implementation Notes

Because the original manifests referenced private or mock remote Docker images (`almond/...:latest`), executing standard deploys resulted in `ImagePullBackOff` errors. We resolved this by implementing and building local mock services:

### 1. Mock Services Architecture
- **Backend Service (`backend/`)**: Built using Flask. Runs on port `5000` and provides a `/predict` endpoint simulating the generation model inference.
- **Frontend Service (`frontend/`)**: Built using Streamlit. Runs on port `8501` and connects to the backend using standard Kubernetes DNS Resolution (`http://ai-service:5000/predict`).

### 2. Local Image Building & Registry Loading
To load the images directly into Minikube without an external registry, build them inside Minikube's context:
```bash
minikube image build -t almond/stylegan-inference:latest ./backend
minikube image build -t almond/streamlit-k8s-demo:latest ./frontend
```

### 3. Manifest Adjustments
- **`imagePullPolicy: IfNotPresent`**: Added to both `deployment_ai.yaml` and `deployment_web.yaml` to instruct Kubernetes to check the local node's Docker daemon for images instead of searching Docker Hub (which avoids pull access denied errors).
- **Resource Limits**: Scaled down CPU and Memory requests in `deployment_ai.yaml` to **200m CPU / 512Mi Memory** per pod so they fit comfortably on a single-node local cluster without triggering scheduling issues (`Insufficient memory`).
