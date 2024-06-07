from flask import Flask, jsonify
import json
import logging
from kafka import KafkaConsumer
from kafka.errors import KafkaError
from pythonjsonlogger import jsonlogger

app = Flask(__name__)
consumer = KafkaConsumer('health_checks_topic', bootstrap_servers='kafka.headless:9092', value_deserializer=lambda m: json.loads(m.decode('utf-8')))
latest_message = {}

logHandler = logging.StreamHandler()
formatter = jsonlogger.JsonFormatter()
logHandler.setFormatter(formatter)
app.logger.addHandler(logHandler)
app.logger.setLevel(logging.INFO)

@app.route('/get_latest_health_check', methods=['GET'])
def get_latest_health_check():
    global latest_message
    try:
        for message in consumer:
            latest_message = message.value
        return jsonify(latest_message)
    except KafkaError as e:
        app.logger.error(f"Failed to consume health check data: {e}")
        return jsonify({'error': 'Failed to consume health check data'}), 500
    except Exception as e:
        app.logger.error(f"Unexpected error: {e}")
        return jsonify({'error': 'Unexpected error occurred'}), 500

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
