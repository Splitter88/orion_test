#!/bin/bash

kubectl exec -n dev -it $(kubectl get pods -n dev -l app.kubernetes.io/name=kafka -o jsonpath="{.items[0].metadata.name}") -- kafka-topics --create --topic health_checks_topic --bootstrap-server kafka-headless:9092 --partitions 1 --replication-factor 1