# collector_daily.py
import datetime
import os
from stocks_client import AlphaVantageClient, ProcessorClient
from logger_setup import setup_logger

logger = setup_logger("daily_collector")

API_KEY = os.getenv("ALPHAVANTAGE_API_KEY")
PROCESSOR_URL = os.getenv("PROCESSOR_URL", "http://processor:8001")
STOCKS = ["JNJ", "ROG", "MRK", "PFE", "ABBV"]


def today_str():
    return datetime.date.today().strftime("%Y-%m-%d")


if __name__ == "__main__":
    logger.info("=== Daily collector started ===")

    av = AlphaVantageClient(API_KEY)
    processor = ProcessorClient(PROCESSOR_URL)

    for symbol in STOCKS:
        ts = av.fetch(symbol, full=False)
        if not ts:
            continue

        t = today_str()
        if t not in ts:
            logger.info(f"[daily] No data for today: {t}")
            continue

        v = ts[t]
        record = [{
            "date": t,
            "open": float(v["1. open"]),
            "high": float(v["2. high"]),
            "low": float(v["3. low"]),
            "close": float(v["4. close"]),
            "volume": int(v["5. volume"])
        }]

        processor.send(symbol, record)

    logger.info("=== Daily collector finished ===")