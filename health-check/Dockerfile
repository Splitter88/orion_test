FROM python:3.9-slim
COPY health_check_service.py /app/health_check_service.py
WORKDIR /app
RUN pip install flask kafka-python
RUN pip install python-json-logger
CMD ["python", "health_check_service.py"]