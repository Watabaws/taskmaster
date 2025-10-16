TAG = 4

build:
	@echo "--- Building Images with Tag: $(TAG) (No-Cache Build) ---"

	docker build --no-cache -t frontend-api:v$(TAG) frontend/
	docker build --no-cache -t backend-api:v$(TAG) backend/

	@echo "--- Build Complete ---"

deploy:
	kubectl apply -f frontend/frontend-service.yaml
	kubectl apply -f frontend/frontend-deployment.yaml
	kubectl apply -f backend/backend-deployment.yaml
	kubectl apply -f backend/backend-service.yaml

	@echo "--- Deployment Complete. Use 'make access' to get the URL. ---"


access:
	@echo "--- Accessing Frontend Service ---"
	@echo "Open this URL in your browser:"
	minikube service frontend-service --url


clean:
	@echo "Deleting Kubernetes deployments and services..."
	-kubectl delete deployment backend-deployment frontend-deployment
	-kubectl delete service backend-service frontend-service

restart:
	@echo "Restarting deployments to apply new image..."
	kubectl rollout restart deployment backend-deployment
	kubectl rollout restart deployment frontend-deployment
	@echo "Deployment restart initiated. Check rollout status."
