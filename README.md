# ToDo Microservice Deployment on Kubernetes (Minikube)

This repository demonstrates the deployment of a simple two-tier ToDo application orchestrated by **Kubernetes**. It highlights key concepts in containerization, internal service discovery, and external traffic handling via a **Reverse Proxy** pattern.

---

## Technical Stack

> * **Orchestration:** Kubernetes (Minikube) - Container management and cluster environment.
> * **Container Engine:** Docker - Packaging the application and web server images.
> * **Backend:** Python / Flask / Gunicorn - Simple REST API for task data (in-memory).
> * **Frontend:** HTML / JavaScript / Nginx - Static web client served by Nginx.
> * **Networking:** Kubernetes Services - Internal (ClusterIP) and external (NodePort) routing.

---

## Deployment Architecture

The application is split into two independent services that communicate exclusively through Kubernetes' internal DNS system:

1.  **Backend Service (`backend-api`)**
    * **Deployment:** Runs the Flask application on port `5000`.
    * **Service Type:** `ClusterIP`. Exposed internally using the DNS name **`backend-api`**.

2.  **Frontend Service (`frontend-service`)**
    * **Deployment:** Runs an Nginx web server on port `80`.
    * **Service Type:** `NodePort`. Exposed externally to the host machine.
    * **Reverse Proxy:** The Nginx configuration forwards all browser requests to the `/api/` path internally to **`http://backend-api:5000`**.

---

## Getting Started

These instructions assume you have **Docker**, **Minikube**, and **kubectl** installed and configured.

### 1. Configure Environment

Ensure your local Docker environment is correctly pointed at the Minikube daemon:

```bash
eval $(minikube docker-env)
