import pulumi
import subprocess
from pulumi import ResourceOptions, export, Config
from pulumi_kubernetes import Provider, yaml as k8s_yaml
from pulumi_kubernetes.helm.v3 import Chart, ChartOpts, FetchOpts
from pulumi_docker import Image, DockerBuildArgs

def get_minikube_ip():
    result = subprocess.run(["minikube", "ip"], stdout=subprocess.PIPE, text=True)
    return result.stdout.strip()

def get_registry_service_ip():
    result = subprocess.run(
        ["kubectl", "get", "svc", "-n", "kube-system", "registry", "-o", "jsonpath={.spec.clusterIP}"],
        stdout=subprocess.PIPE, text=True
    )
    return result.stdout.strip()

# Get the Minikube IP and the internal registry service IP dynamically
minikube_ip = get_minikube_ip()
registry_service_ip = get_registry_service_ip()
registry_port = 80
external_registry = f'localhost:32770'
internal_registry = f'{registry_service_ip}:{registry_port}'

# Function to replace placeholders in YAML
def replace_placeholders(file_path, registry_url):
    with open(file_path, 'r') as file:
        content = file.read()
    content = content.replace('{{REGISTRY_URL}}', registry_service_ip)
    temp_file_path = f'/tmp/updated-{file_path}'
    with open(temp_file_path, 'w') as file:
        file.write(content)
    return temp_file_path

# Configure Kubernetes provider
config = Config()
kubeconfig_path = config.require('kubeconfig')
k8s_provider = Provider('k8s-provider', kubeconfig=kubeconfig_path)

# Namespace
namespace = 'dev'

# Deploy Kafka using Helm
kafka = Chart(
    'kafka',
    ChartOpts(
        chart='kafka',
        fetch_opts=FetchOpts(
            repo='https://ricardo-aires.github.io/helm-charts'
        ),
        namespace=namespace
    ),
    opts=ResourceOptions(provider=k8s_provider)
)

# Deploy Prometheus using Helm
prometheus = Chart(
    'prometheus',
    ChartOpts(
        chart='prometheus',
        fetch_opts=FetchOpts(
            repo='https://charts.bitnami.com/bitnami'
        ),
        namespace=namespace
    ),
    opts=ResourceOptions(provider=k8s_provider)
)

# Deploy Grafana using Helm
grafana = Chart(
    'grafana',
    ChartOpts(
        chart='grafana',
        fetch_opts=FetchOpts(
            repo='https://charts.bitnami.com/bitnami'
        ),
        namespace=namespace
    ),
    opts=ResourceOptions(provider=k8s_provider)
)

# Replace placeholders in YAML files and apply
updated_healthcheckservice_deployment_yaml = replace_placeholders('healthcheckservice-deployment.yaml', registry_service_ip)
updated_consumerhealthcheckservice_deployment_yaml = replace_placeholders('consumerhealthcheckservice-deployment.yaml', registry_service_ip)

# Apply Kubernetes YAML manifests directly
kafka_configmap_yaml = k8s_yaml.ConfigFile('kafka-configmap', file='kafka-configmap.yaml', opts=ResourceOptions(provider=k8s_provider))
healthcheckservice_deployment_yaml = k8s_yaml.ConfigFile('healthcheckservice-deployment', file='healthcheckservice-deployment.yaml', opts=ResourceOptions(provider=k8s_provider))
consumerhealthcheckservice_deployment_yaml = k8s_yaml.ConfigFile('consumerhealthcheckservice-deployment', file='consumerhealthcheckservice-deployment.yaml', opts=ResourceOptions(provider=k8s_provider))
healthcheckservice_hpa_yaml = k8s_yaml.ConfigFile('healthcheckservice-hpa', file='healthcheckservice-hpa.yaml', opts=ResourceOptions(provider=k8s_provider))
consumerhealthcheckservice_hpa_yaml = k8s_yaml.ConfigFile('consumerhealthcheckservice-hpa', file='consumerhealthcheckservice-hpa.yaml', opts=ResourceOptions(provider=k8s_provider))

# Docker images
# Build and push the health-check service Docker image
health_check_image = Image(
    'health-check-service',
    build=DockerBuildArgs(
        context='./health-check'
    ),
    image_name=f'{external_registry}/healthcheckservice:latest',
    skip_push=False
)

# Build and push the consumer health-check service Docker image
consumer_health_check_image = Image(
    'consumer-health-check-service',
    build=DockerBuildArgs(
        context='./consumer'
    ),
    image_name=f'{external_registry}/consumerhealthcheckservice:latest',
    skip_push=False
)

# Export the kubeconfig path
export('kubeconfig', kubeconfig_path)