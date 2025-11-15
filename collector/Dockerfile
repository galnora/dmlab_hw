# === Base image ===
FROM python:3.11-slim

# === Workdir ===
WORKDIR /app

# === Copy requirements ===
COPY collector/requirements.txt .

# === Install dependencies ===
RUN pip install --no-cache-dir -r requirements.txt

# === Copy app files ===
COPY collector/collector_full.py .
COPY collector/stocks_client.py .
COPY logger_setup.py .

# === Environment defaults ===
ENV PROCESSOR_URL=http://processor:8001

# === Run collector script ===
CMD ["python", "collector_full.py"]