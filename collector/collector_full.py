# collector_full.py
import time
import os
from stocks_client import AlphaVantageClient, ProcessorClient
from logger_setup import setup_logger

logger = setup_logger("full_collector")

API_KEY = os.getenv("ALPHAVANTAGE_API_KEY")
PROCESSOR_URL = os.getenv("PROCESSOR_URL", "http://processor:8001")
STOCKS = ["JNJ", "ROG", "MRK", "PFE", "ABBV"]


if __name__ == "__main__":
    logger.info("=== Full collector started ===")

    av = AlphaVantageClient(API_KEY)
    processor = ProcessorClient(PROCESSOR_URL)

    for symbol in STOCKS:
        ts = av.fetch(symbol, full=True)
        if not ts:
            continue

        records = []
        for date_str, v in ts.items():
            records.append({
                "date": date_str,
                "open": float(v["1. open"]),
                "high": float(v["2. high"]),
                "low": float(v["3. low"]),
                "close": float(v["4. close"]),
                "volume": int(v["5. volume"])
            })

        processor.send(symbol, records)
        time.sleep(15)  # API limit

    logger.info("=== Full collector finished ===")