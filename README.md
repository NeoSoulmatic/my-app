# my-sre-app

A minimal Flask API built to practice SRE fundamentals end to end:
CI/CD, containerization, Kubernetes, and observability.

---

## Stack

| Layer | Tool |
|---|---|
| App | Python / Flask |
| Tests | pytest |
| Container | Docker |
| CI/CD | GitHub Actions + GitHub Container Registry |
| Orchestration | Kubernetes (Minikube) |
| Package Management | Helm |
| Metrics | Prometheus + prometheus-flask-exporter |
| Dashboards | Grafana |

---

## Project Structure

```
my-app/
├── app/
│   └── main.py              # Flask application
├── tests/
│   └── test_main.py         # pytest unit tests
├── k8s/
│   ├── deployment.yaml      # K8s Deployment (2 replicas, probes, resource limits)
│   ├── service.yaml         # K8s Service (ClusterIP)
│   ├── ingress.yaml         # K8s Ingress (nginx)
│   └── prometheus-values.yaml  # Helm values for kube-prometheus-stack
├── .github/
│   └── workflows/
│       └── ci.yaml          # GitHub Actions pipeline
├── Dockerfile
└── requirements.txt
```

---

## Phase 1: Run Locally

```bash
# Install dependencies
pip install -r requirements.txt

# Run the app
python -m app.main

# Test endpoints
curl http://localhost:5000/
curl http://localhost:5000/health
curl http://localhost:5000/ready
curl http://localhost:5000/info
curl http://localhost:5000/metrics  # Prometheus metrics
```

---

## Phase 2: Run Tests

```bash
pytest tests/ -v
```

All four tests should pass before you touch Docker or Kubernetes.

---

## Phase 3: Build and Run with Docker

```bash
# Build the image
docker build -t my-sre-app:local .

# Run the container
docker run -p 5000:5000 my-sre-app:local

# Verify it works inside Docker
curl http://localhost:5000/health
```

---

## Phase 4: Push to GitHub

```bash
git init
git add .
git commit -m "initial commit"
git remote add origin https://github.com/YOUR_USERNAME/my-app.git
git push -u origin main
```

GitHub Actions will automatically:
1. Run your tests
2. Build the Docker image
3. Push it to GitHub Container Registry (ghcr.io)

Check the Actions tab in your GitHub repo to watch it run.

Before pushing, update the image name in k8s/deployment.yaml:
```yaml
image: ghcr.io/YOUR_GITHUB_USERNAME/my-app:latest
```

---

## Phase 5: Deploy to Kubernetes

```bash
# Start Minikube
minikube start

# Enable the nginx ingress controller
minikube addons enable ingress

# Apply all manifests
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml
kubectl apply -f k8s/ingress.yaml

# Watch pods come up
kubectl get pods -w

# Verify deployment
kubectl get deployments
kubectl get services
kubectl get ingress

# Check logs
kubectl logs -l app=my-sre-app

# Add to /etc/hosts so the ingress hostname resolves
echo "$(minikube ip) my-sre-app.local" | sudo tee -a /etc/hosts

# Hit the app through the ingress
curl http://my-sre-app.local/
curl http://my-sre-app.local/health
```

### Useful kubectl commands to practice

```bash
# Describe a pod (useful for debugging)
kubectl describe pod -l app=my-sre-app

# Execute a command inside a running pod
kubectl exec -it $(kubectl get pod -l app=my-sre-app -o name | head -1) -- /bin/sh

# Scale the deployment
kubectl scale deployment my-sre-app --replicas=3

# Trigger a rolling update (change image tag, then apply)
kubectl rollout status deployment/my-sre-app
kubectl rollout history deployment/my-sre-app
kubectl rollout undo deployment/my-sre-app  # Rollback

# View resource usage
kubectl top pods
```

---

## Phase 6: Observability with Prometheus and Grafana

```bash
# Add the Prometheus community Helm chart repo
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update

# Install kube-prometheus-stack (includes Prometheus + Grafana)
helm install monitoring prometheus-community/kube-prometheus-stack \
  --namespace monitoring \
  --create-namespace \
  --values k8s/prometheus-values.yaml

# Watch the monitoring pods come up
kubectl get pods -n monitoring -w

# Access Grafana (get the NodePort)
kubectl get svc -n monitoring monitoring-grafana

# Port-forward Grafana to your local machine
kubectl port-forward -n monitoring svc/monitoring-grafana 3000:80

# Open http://localhost:3000
# Username: admin  Password: admin
```

### PromQL queries to try in Grafana

```promql
# Request rate per second over last 5 minutes
rate(flask_http_request_total[5m])

# Error rate (4xx and 5xx responses)
rate(flask_http_request_total{status=~"4..|5.."}[5m])

# Request latency 95th percentile
histogram_quantile(0.95, rate(flask_http_request_duration_seconds_bucket[5m]))

# Total requests by endpoint
sum by (path) (flask_http_request_total)
```

---

## SRE Concepts Demonstrated

| Concept | Where |
|---|---|
| Liveness probe | deployment.yaml — restarts unhealthy containers |
| Readiness probe | deployment.yaml — removes unready pods from load balancer |
| Resource requests/limits | deployment.yaml — prevents noisy neighbor problems |
| Rolling deployments | Kubernetes default — zero downtime updates |
| Metrics endpoint | /metrics — scraped by Prometheus |
| SLI example | HTTP success rate (non-5xx / total requests) |
| SLO example | 99.9% of requests return non-5xx over a 30 day window |
| Error budget | 0.1% of requests allowed to fail = ~43 min/month |

---

## Next Steps (when you're ready to go further)

- Add a `HorizontalPodAutoscaler` that scales based on CPU
- Add a `ConfigMap` for app configuration instead of hardcoding values
- Add a `Secret` for any sensitive config
- Write an alert rule in Prometheus that fires when error rate exceeds 1%
- Add a second service and practice network policies between them
- Deploy to a real cloud cluster (EKS, GKE, or AKS)
