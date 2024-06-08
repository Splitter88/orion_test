FROM python:3.9-slim
COPY consumer_health_check_service.py /app/consumer_health_check_service.py
WORKDIR /app
RUN pip install flask kafka-python
RUN pip install python-json-logger
CMD ["python", "consumer_health_check_service.py"]
