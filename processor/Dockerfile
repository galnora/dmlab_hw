# === Base image ===
FROM python:3.11-slim

# === Workdir ===
WORKDIR /app

# === Copy requirements ===
COPY processor/requirements.txt .

# === Install curl for health check
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

# === Install python deps ===
RUN pip install --no-cache-dir -r requirements.txt

# === Copy app code ===
COPY processor/main.py .
COPY logger_setup.py .

# === Environment defaults ===
ENV MYSQL_HOST=db
ENV MYSQL_USER=collector
ENV MYSQL_PASSWORD=P4ssword
ENV MYSQL_DATABASE=stocks_db

EXPOSE 8001

# === Run FastAPI ===
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8001"]