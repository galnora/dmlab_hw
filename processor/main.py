from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
import mysql.connector
import pandas as pd
import numpy as np
import os
from logger_setup import setup_logger

logger = setup_logger("processor")

app = FastAPI(title="Stock Processor Service")

# --- DB config ---
DB_CONFIG = {
    "host": os.getenv("MYSQL_HOST", "db"),
    "user": os.getenv("MYSQL_USER", "collector"),
    "password": os.getenv("MYSQL_PASSWORD", "P4ssword"),
    "database": os.getenv("MYSQL_DATABASE", "stocks_db"),
}


# ============================================
#               DATA MODELS
# ============================================

class StockRecord(BaseModel):
    date: str
    open: float
    high: float
    low: float
    close: float
    volume: int


# ============================================
#         DATABASE INITIALIZATION
# ============================================

def create_table():
    """Create DB table if not exists."""
    logger.info("[startup] Creating table if not exists...")
    with mysql.connector.connect(**DB_CONFIG) as conn:
        cur = conn.cursor()
        cur.execute("""
        CREATE TABLE IF NOT EXISTS stock_prices (
            id INT AUTO_INCREMENT PRIMARY KEY,
            symbol VARCHAR(10) NOT NULL,
            date DATE NOT NULL,
            open FLOAT,
            high FLOAT,
            low FLOAT,
            close FLOAT,
            volume BIGINT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE KEY unique_symbol_date (symbol, date)
        )
        """)
        conn.commit()
        cur.close()
    logger.info("[startup] Table ready.")


@app.on_event("startup")
def startup():
    create_table()


# ============================================
#         DB OPERATIONS
# ============================================

def insert_stock_data(symbol: str, records: List[StockRecord]):
    """Insert stock data into DB."""
    with mysql.connector.connect(**DB_CONFIG) as conn:
        cur = conn.cursor()

        sql = """
        INSERT INTO stock_prices (symbol, date, open, high, low, close, volume)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE
            open=VALUES(open),
            high=VALUES(high),
            low=VALUES(low),
            close=VALUES(close),
            volume=VALUES(volume)
        """

        rows = [
            (symbol, r.date, r.open, r.high, r.low, r.close, r.volume)
            for r in records
        ]
        cur.executemany(sql, rows)
        conn.commit()
        cur.close()


def get_dataframe(symbol: str) -> pd.DataFrame:
    """Load stock data for a symbol."""
    with mysql.connector.connect(**DB_CONFIG) as conn:
        query = """
            SELECT date, close, volume
            FROM stock_prices
            WHERE symbol = %s
            ORDER BY date;
        """
        df = pd.read_sql(query, conn, params=(symbol,))
        if not df.empty:
            df["date"] = pd.to_datetime(df["date"])
        return df


# ============================================
#             INGEST ENDPOINT
# ============================================

@app.post("/api/v1/ingest/{symbol}")
def ingest(symbol: str, data: List[StockRecord]):
    logger.info(f"[ingest] Received {len(data)} records for {symbol}")

    try:
        insert_stock_data(symbol, data)
    except Exception as e:
        logger.exception(f"[ingest] Insert failed for {symbol}")
        raise HTTPException(status_code=500, detail="DB insert failed")

    return {"symbol": symbol, "inserted": len(data)}


# ============================================
#             METRICS ENDPOINT
# ============================================

@app.get("/api/v1/metrics/{symbol}")
def get_metrics(symbol: str):
    logger.info(f"[metrics] Request for {symbol}")

    df = get_dataframe(symbol)
    if df.empty:
        return {"symbol": symbol, "error": "No data"}

    # time windows
    pre_start = pd.Timestamp("2017-01-01")
    pre_end = pd.Timestamp("2020-01-01")
    covid_start = pd.Timestamp("2020-01-01")
    covid_end = pd.Timestamp("2023-05-01")
    post_start = pd.Timestamp("2023-05-02")

    pre_covid = df[(df["date"] >= pre_start) & (df["date"] < pre_end)]
    covid = df[(df["date"] >= covid_start) & (df["date"] <= covid_end)]
    post_covid = df[df["date"] > post_start]

    def growth_period(dfp):
        if dfp.empty:
            return None
        start_val = dfp.iloc[0]["close"]
        end_val = dfp.iloc[-1]["close"]
        return round(((end_val - start_val) / start_val) * 100, 2)

    result = {
        "symbol": symbol,
        "growth_pre_covid": growth_period(pre_covid),
        "growth_covid": growth_period(covid),
        "growth_post_covid": growth_period(post_covid),
    }

    return result


# ============================================
#       ANALYTICS ENDPOINT
# ============================================

@app.get("/api/v1/analytics/{symbol}")
def analytics(symbol: str):
    logger.info(f"[analytics] Request for {symbol}")

    df = get_dataframe(symbol)
    if df.empty:
        return {"symbol": symbol, "error": "No data"}

    # --- 1) Volatility ---
    df["log_return"] = np.log(df["close"] / df["close"].shift(1))
    volatility = float(df["log_return"].std() * np.sqrt(252)) if df["log_return"].notna().sum() > 1 else None

    # --- 2) Month-over-month percent change ---
    df_month = df.resample("M", on="date").last()
    mom = df_month["close"].pct_change().iloc[-1] if len(df_month) > 1 else None
    mom = round(float(mom * 100), 2) if mom is not None and not np.isnan(mom) else None

    # --- 3) Average volume ---
    avg_volume = float(df["volume"].mean()) if df["volume"].notna().sum() else None

    return {
        "symbol": symbol,
        "volatility": round(volatility, 4) if volatility else None,
        "mom_change": mom,
        "avg_volume": round(avg_volume, 2) if avg_volume else None,
    }


# ============================================
#               TREND ENDPOINT
# ============================================

@app.get("/api/v1/trend/{symbol}")
def get_trend(symbol: str):
    logger.info(f"[trend] Request for {symbol}")

    df = get_dataframe(symbol)
    if df.empty:
        return []

    df = df[df["date"] >= "2017-01-01"]
    df["date"] = df["date"].astype(str)

    return df.to_dict(orient="records")


# ============================================
#               HEALTH ENDPOINT
# ============================================

@app.get("/health")
def health():
    return {"status": "ok"}