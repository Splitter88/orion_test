from flask import Flask, jsonify, request
from kafka import KafkaProducer
import json
import time
import threading
import logging

app = Flask(__name__)
producer = KafkaProducer(bootstrap_servers='kafka.dev.svc.cluster.local:9092', value_serializer=lambda v: json.dumps(v).encode('utf-8'))
logging.basicConfig(level=logging.INFO)

def perform_health_check():
    while True:
        health_check = {
            "service_name": "MyService",
            "status": "OK",
            "timestamp": time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
        }
        producer.send('health_checks_topic', health_check)
        logging.info(f"Produced: {health_check}")
        time.sleep(30)

@app.route('/check_health', methods=['GET'])
def check_health():
    return jsonify({"message": "Health checks are being performed"}), 200

if __name__ == '__main__':
    threading.Thread(target=perform_health_check).start()
    app.run(host='0.0.0.0', port=5000)
