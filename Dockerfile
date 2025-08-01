FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
# Don't copy code - it will be mounted as volume in development
# COPY . .
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "main:app", "--capture-output", "--log-level", "debug", "--access-logfile", "-", "--error-logfile", "-", "--reload"]
