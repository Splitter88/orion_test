#!/bin/bash

NAMESPACE=$1
RETRIES=30
SLEEP_INTERVAL=10

# Function to check if Kafka pods are created
check_pods_created() {
  kubectl get pods -n $NAMESPACE -l app.kubernetes.io/name=kafka -o jsonpath="{.items[0].metadata.name}" 2>/dev/null
}

# Retry loop to wait for Kafka pods to be created
for i in $(seq 1 $RETRIES); do
  POD_NAME=$(check_pods_created)
  if [ -n "$POD_NAME" ]; then
    echo "Kafka pod found: $POD_NAME"
    break
  fi
  echo "Waiting for Kafka pods to be created... ($i/$RETRIES)"
  sleep $SLEEP_INTERVAL
done

if [ -z "$POD_NAME" ]; then
  echo "Kafka pods not found after waiting. Exiting."
  exit 1
fi

# Wait for Kafka pods to be ready
kubectl wait --for=condition=ready pod -l app.kubernetes.io/name=kafka -n $NAMESPACE --timeout=600s

# Create the Kafka topic
kubectl exec -n $NAMESPACE -it $POD_NAME -- kafka-topics --create --topic health_checks_topic --bootstrap-server kafka-headless:9092 --partitions 1 --replication-factor 1