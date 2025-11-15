# === Base image ===
FROM python:3.11-slim

# === Workdir ===
WORKDIR /app

# === Install cron
RUN apt-get update && apt-get install -y cron && rm -rf /var/lib/apt/lists/*

# === Install dependencies
COPY collector/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# == Copy app files ===
COPY collector/collector_daily.py .
COPY collector/stocks_client.py .
COPY logger_setup.py .

# === Copy cron files ===
COPY scheduler/daily_cronjob /etc/cron.d/daily_cronjob
RUN chmod 0644 /etc/cron.d/daily_cronjob && crontab /etc/cron.d/daily_cronjob

# === Copy entrypoint.sh ===
COPY scheduler/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# === Run entrypoint.sh ===
CMD ["/entrypoint.sh"]