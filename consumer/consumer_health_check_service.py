from flask import Flask, jsonify
from kafka import KafkaConsumer
import json
import threading
import logging

app = Flask(__name__)
consumer = KafkaConsumer('health_checks_topic', bootstrap_servers='kafka-headless.dev.svc.cluster.local:9092', value_deserializer=lambda m: json.loads(m.decode('utf-8')))
latest_health_check = None
logging.basicConfig(level=logging.INFO)

def consume_health_checks():
    global latest_health_check
    for message in consumer:
        latest_health_check = message.value
        logging.info(f"Consumed: {latest_health_check}")

@app.route('/get_latest_health_check', methods=['GET'])
def get_latest_health_check():
    if latest_health_check:
        return jsonify(latest_health_check), 200
    else:
        return jsonify({"message": "No health check available"}), 404

if __name__ == '__main__':
    threading.Thread(target=consume_health_checks).start()
    app.run(host='0.0.0.0', port=5000)
