FROM python:3.13-slim

WORKDIR /app

# We only copy the source code since we don't have external dependencies
COPY src/ ./src/

# Set the Python path so the 'app' module can be found
ENV PYTHONPATH=/app/src

# Default command (will be overridden by docker-compose)
CMD ["python", "src/app/run_http_server.py", "8080"]
