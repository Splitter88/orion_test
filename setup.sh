#!/bin/bash

echo "Starting Minikube..."
minikube start --driver=docker --addons=ingress

echo "Configuring Docker to use Minikube's Docker daemon..."
eval $(minikube -p minikube docker-env)

echo "Setting Kubernetes context to Minikube..."
kubectl config use-context minikube

echo "Adding and updating Helm repositories..."
helm repo add rhcharts https://ricardo-aires.github.io/helm-charts/
helm repo add bitnami https://charts.bitnami.com/bitnami
helm repo update

echo "Uninstalling existing Helm releases..."
helm uninstall kafka || true
helm uninstall prometheus || true
helm uninstall grafana || true

echo "Deploying local Docker registry..."
kubectl apply -f registry.yaml

echo "Installing Kafka with Helm..."
helm upgrade --install kafka rhcharts/kafka

echo "Waiting for Kafka pods to be ready..."
kubectl wait --for=condition=ready pod -l app.kubernetes.io/name=kafka --timeout=600s

echo "Creating Kafka topic..."
kubectl exec -it $(kubectl get pods -l app.kubernetes.io/name=kafka -o jsonpath="{.items[0].metadata.name}") -- kafka-topics --create --topic health_checks_topic --bootstrap-server kafka-headless:9092 --partitions 1 --replication-factor 1

echo "Installing Prometheus and Grafana with Helm..."
helm install prometheus bitnami/prometheus
helm install grafana bitnami/grafana

echo "Applying Kubernetes manifests..."
kubectl apply -f kafka-configmap.yaml
kubectl apply -f healthcheckservice-deployment.yaml
kubectl apply -f consumerhealthcheckservice-deployment.yaml
kubectl apply -f healthcheckservice-hpa.yaml
kubectl apply -f consumerhealthcheckservice-hpa.yaml


echo "Waiting for the local Docker registry to be ready..."
kubectl wait --for=condition=ready pod -l app=registry --timeout=300s

REGISTRY_IP=$(minikube ip):5000

echo "Building Docker images..."
docker build -t healthcheckservice:latest -f health-check/Dockerfile health-check/

docker build -t consumerhealthcheckservice:latest -f consumer/Dockerfile consumer/

INTERNAL_REGISTRY_IP=$(kubectl get svc registry -n default -o=jsonpath='{.spec.clusterIP}'):5000

docker tag healthcheckservice:latest $INTERNAL_REGISTRY_IP/healthcheckservice:latest
docker tag consumerhealthcheckservice:latest $INTERNAL_REGISTRY_IP/consumerhealthcheckservice:latest

docker push $INTERNAL_REGISTRY_IP/healthcheckservice:latest
docker push $INTERNAL_REGISTRY_IP/consumerhealthcheckservice:latest

echo "Updating Kubernetes deployments to use images from the local registry..."
kubectl set image deployment/healthcheckservice healthcheckservice=$INTERNAL_REGISTRY_IP/healthcheckservice:latest
kubectl set image deployment/consumerhealthcheckservice consumerhealthcheckservice=$INTERNAL_REGISTRY_IP/consumerhealthcheckservice:latest

echo "Setup complete!"
