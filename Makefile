# Makefile for todolist_toy app

# Variables
FRONTEND_IMAGE_NAME := frontend-app
BACKEND_IMAGE_NAME := backend-app
FRONTEND_TAG := latest
BACKEND_TAG := latest

# Targets
.PHONY: all build_frontend deploy_frontend build_backend deploy_backend frontend backend clean access deploy_postgres restart

all: frontend backend

# Frontend targets
build_frontend:
	@echo "Building frontend Docker image..."
	docker build -t $(FRONTEND_IMAGE_NAME):$(FRONTEND_TAG) ./frontend

deploy_frontend:
	@echo "Deploying frontend..."
	kubectl apply -f frontend/frontend-deployment.yaml
	kubectl apply -f frontend/frontend-service.yaml

frontend: build_frontend deploy_frontend

# Backend targets
build_backend:
	@echo "Building backend Docker image..."
	docker build -t $(BACKEND_IMAGE_NAME):$(BACKEND_TAG) ./backend

deploy_backend:
	@echo "Deploying backend..."
	kubectl apply -f backend/backend-deployment.yaml
	kubectl apply -f backend/backend-service.yaml

backend: build_backend deploy_backend

deploy_postgres:
	@echo "Deploying postgres..."
	kubectl apply -f backend/postgres-pvc.yaml
	kubectl apply -f backend/postgres-secret.yaml
	kubectl apply -f backend/postgres-deployment.yaml
	kubectl apply -f backend/postgres-service.yaml

# Clean target
clean:
	@echo "Cleaning up Docker images..."
	-docker rmi $(FRONTEND_IMAGE_NAME):$(FRONTEND_TAG)
	-docker rmi $(BACKEND_IMAGE_NAME):$(BACKEND_TAG)

access:
	@echo "Accessing frontend service..."
	minikube service frontend-service

restart:
	@echo "Restarting deployments to apply new image..."
	kubectl rollout restart deployment backend-deployment
	kubectl rollout restart deployment frontend-deployment
	@echo "Deployment restart initiated. Check rollout status."