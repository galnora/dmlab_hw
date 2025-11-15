import requests
import datetime
import os
from logger_setup import setup_logger


class AlphaVantageClient:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.logger = setup_logger("alpha_vantage")

    def fetch(self, symbol: str, full: bool = False):
        """Fetch stock data (full history or today's only)."""

        url = (
            f"https://www.alphavantage.co/query?"
            f"function=TIME_SERIES_DAILY&symbol={symbol}"
            f"&apikey={self.api_key}"
        )

        if full:
            url += "&outputsize=full"

        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()
        except Exception as e:
            self.logger.error(f"[API] Error for {symbol}: {e}")
            return None

        if "Time Series (Daily)" not in data:
            self.logger.error(f"[API] Bad response for {symbol}: {data}")
            return None

        ts = data["Time Series (Daily)"]

        return ts


class ProcessorClient:
    def __init__(self, processor_url: str):
        self.url = processor_url.rstrip("/")
        self.logger = setup_logger("processor_client")

    def send(self, symbol: str, records: list):
        endpoint = f"{self.url}/api/v1/ingest/{symbol}"
        try:
            res = requests.post(endpoint, json=records, timeout=10)
            res.raise_for_status()
            self.logger.info(
                f"[send] Sent {len(records)} records for {symbol}"
            )
            return True
        except Exception as e:
            self.logger.error(f"[send] Failed sending {symbol}: {e}")
            return False