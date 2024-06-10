# DevOps Exam - Interview Task

This project sets up a local Kubernetes environment using Minikube, deploys Kafka, Prometheus, and Grafana using Helm, and builds and deploys Docker images for health check services.

## Prerequisites

- [Minikube](https://minikube.sigs.k8s.io/docs/start/)
- [Docker](https://docs.docker.com/get-docker/)
- [Pulumi](https://www.pulumi.com/docs/get-started/install/)
- [Python 3.8+](https://www.python.org/downloads/)
- [kubectl](https://kubernetes.io/docs/tasks/tools/install-kubectl/)
- [Helm](https://helm.sh/docs/intro/install/)
- [pip3](https://pip.pypa.io/en/stable/installation/)

## Running the Project

1. **Install the prerequisites**
2. **Configure Pulumi**:
3. **Edit following line in deploy.sh to reflect your environment**
    *pulumi config set interview-test:kubeconfig $HOME/.kube/config --plaintext*
4. **Run deploy.sh**:
    *This will start minikube, configure kubeconfig path for Pulumi and run the Pulumi program to deploy the environment.*
        **Alternatively, setup.sh can be used as a backup, but it is not fully supported.**
