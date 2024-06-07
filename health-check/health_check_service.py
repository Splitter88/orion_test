from flask import Flask, request, jsonify
import json
import logging
from kafka import KafkaProducer
from kafka.errors import KafkaError
from datetime import datetime
from pythonjsonlogger import jsonlogger

app = Flask(__name__)
producer = KafkaProducer(bootstrap_servers='kafka-headless:9092', value_serializer=lambda v: json.dumps(v).encode('utf-8'))

logHandler = logging.StreamHandler()
formatter = jsonlogger.JsonFormatter()
logHandler.setFormatter(formatter)
app.logger.addHandler(logHandler)
app.logger.setLevel(logging.INFO)

@app.route('/check_health', methods=['POST'])
def check_health():
    try:
        health_data = request.json
        health_data['timestamp'] = datetime.utcnow().isoformat()
        producer.send('health_checks_topic', value=health_data).get(timeout=10)
        app.logger.info(f"Health check data sent: {health_data}")
        return jsonify({'message': 'Health check data sent'}), 200
    except KafkaError as e:
        app.logger.error(f"Failed to send health check data: {e}")
        return jsonify({'error': 'Failed to send health check data'}), 500
    except Exception as e:
        app.logger.error(f"Unexpected error: {e}")
        return jsonify({'error': 'Unexpected error occurred'}), 500

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)