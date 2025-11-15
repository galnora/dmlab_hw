from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import requests
import os
from logger_setup import setup_logger

logger = setup_logger("dashboard")

app = FastAPI(title="Pharma Stocks Dashboard")

# --- configuration ---
PROCESSOR_URL = os.getenv("PROCESSOR_URL", "http://processor:8001")

templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

STOCKS = {
    "JNJ": "Johnson & Johnson",
    "ROG": "Roche",
    "MRK": "Merck & Co.",
    "PFE": "Pfizer",
    "ABBV": "AbbVie"
}


@app.get("/")
def home(request: Request):
    logger.info("Rendering dashboard home")
    metrics = []
    analytics = {}

    for symbol, name in STOCKS.items():
        # --- Metrics ---
        try:
            res = requests.get(f"{PROCESSOR_URL}/api/v1/metrics/{symbol}")
            if res.status_code == 200:
                data = res.json()
                data["name"] = name
                metrics.append(data)
        except Exception:
            logger.exception(f"Failed loading metrics for {symbol}")

        # --- Analytics ---
        try:
            res = requests.get(f"{PROCESSOR_URL}/api/v1/analytics/{symbol}")
            analytics[symbol] = res.json() if res.status_code == 200 else {}
        except Exception:
            analytics[symbol] = {}

    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "metrics": metrics,
        "analytics": analytics,
        "stocks": STOCKS
    })


@app.get("/api/trend/{symbol}")
def get_trend(symbol: str):
    try:
        res = requests.get(f"{PROCESSOR_URL}/api/v1/trend/{symbol}")
        if res.status_code == 200:
            return res.json()
    except Exception:
        logger.exception(f"Trend load failed for {symbol}")
    return []