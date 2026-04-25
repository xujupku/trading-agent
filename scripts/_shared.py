#!/usr/bin/env python3
import os
import time
import random
import logging
import threading

import pandas as pd
import yfinance as yf
from yfinance.exceptions import YFRateLimitError

logger = logging.getLogger(__name__)

CACHE_DIR = os.path.join(os.path.expanduser("~"), ".tradingagents", "cache")

_ticker_cache: dict[str, yf.Ticker] = {}

_request_lock = threading.Lock()
_last_request_time = 0.0
_MIN_REQUEST_INTERVAL = 0.5


def _throttle():
    global _last_request_time
    with _request_lock:
        now = time.monotonic()
        elapsed = now - _last_request_time
        if elapsed < _MIN_REQUEST_INTERVAL:
            time.sleep(_MIN_REQUEST_INTERVAL - elapsed)
        _last_request_time = time.monotonic()


def yf_retry(func, max_retries=5, base_delay=2.0):
    for attempt in range(max_retries + 1):
        _throttle()
        try:
            return func()
        except YFRateLimitError:
            if attempt < max_retries:
                jitter = random.uniform(0, 1)
                delay = base_delay * (2 ** attempt) + jitter
                logger.warning(f"Rate limited, retrying in {delay:.1f}s (attempt {attempt + 1}/{max_retries})")
                time.sleep(delay)
            else:
                raise


def get_ticker(symbol: str) -> yf.Ticker:
    key = symbol.upper()
    if key not in _ticker_cache:
        _ticker_cache[key] = yf.Ticker(key)
    return _ticker_cache[key]


def _clean_dataframe(data: pd.DataFrame) -> pd.DataFrame:
    data["Date"] = pd.to_datetime(data["Date"], errors="coerce")
    data = data.dropna(subset=["Date"])
    price_cols = [c for c in ["Open", "High", "Low", "Close", "Volume"] if c in data.columns]
    data[price_cols] = data[price_cols].apply(pd.to_numeric, errors="coerce")
    data = data.dropna(subset=["Close"])
    data[price_cols] = data[price_cols].ffill().bfill()
    return data


def load_ohlcv(symbol: str, end_date: str | None = None) -> pd.DataFrame:
    symbol = symbol.upper()
    today_date = pd.Timestamp.today()
    start_date = today_date - pd.DateOffset(years=5)
    start_str = start_date.strftime("%Y-%m-%d")
    end_str = today_date.strftime("%Y-%m-%d")

    data_file = None
    try:
        os.makedirs(CACHE_DIR, exist_ok=True)
        data_file = os.path.join(CACHE_DIR, f"{symbol}-YFin-data-{start_str}-{end_str}.csv")
    except OSError:
        pass

    if data_file and os.path.exists(data_file):
        data = pd.read_csv(data_file, on_bad_lines="skip")
    else:
        data = yf_retry(lambda: yf.download(
            symbol,
            start=start_str,
            end=end_str,
            multi_level_index=False,
            progress=False,
            auto_adjust=True,
        ))
        data = data.reset_index()
        if data_file:
            try:
                data.to_csv(data_file, index=False)
            except OSError:
                pass

    data = _clean_dataframe(data)
    if end_date:
        data = data[data["Date"] <= pd.to_datetime(end_date)]
    return data
