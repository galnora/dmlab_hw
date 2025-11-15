# === Base image ===
FROM python:3.11-slim

# === Workdir ===
WORKDIR /app

# === Copy dependencies ===
COPY dashboard/requirements.txt .

# === Install dependencies ===
RUN pip install --no-cache-dir -r requirements.txt

# === Copy app files ===
COPY dashboard/main.py .
COPY dashboard/templates ./templates
COPY dashboard/static ./static
COPY logger_setup.py .

# === Environment variables ===
ENV PROCESSOR_URL=http://processor:8001
ENV PORT=8000

# === Expose port ===
EXPOSE 8000

# === Run FastAPI ===
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
