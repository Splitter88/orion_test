#!/bin/bash

# Start Minikube
echo "Starting Minikube..."
minikube start --driver=docker --insecure-registry "10.0.0.0/24" --addons=ingress,registry

# Configure Docker to use Minikube's Docker daemon
echo "Configuring Docker to use Minikube's Docker daemon..."
eval $(minikube -p minikube docker-env)
kubectl create ns dev

# Set kubeconfig path for Pulumi
echo "Setting kubeconfig path for Pulumi..."
pulumi config set interview-test:kubeconfig $HOME/.kube/config --plaintext

# Run Pulumi
echo "Running Pulumi..."
pulumi up

