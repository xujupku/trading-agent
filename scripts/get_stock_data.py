#!/usr/bin/env python3
"""Fetch OHLCV stock price data using yfinance.

Usage:
    python get_stock_data.py <TICKER> <START_DATE> <END_DATE>

Example:
    python get_stock_data.py NVDA 2025-07-01 2026-01-15
"""

import sys
import os
import logging
from datetime import datetime

import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _shared import load_ohlcv

logger = logging.getLogger(__name__)


def get_stock_data(symbol: str, start_date: str, end_date: str) -> str:
    start_dt = pd.to_datetime(start_date)
    end_dt = pd.to_datetime(end_date)

    data = load_ohlcv(symbol, end_date)
    data = data[data["Date"] >= start_dt]

    if data.empty:
        return f"No data found for symbol '{symbol}' between {start_date} and {end_date}"

    numeric_columns = ["Open", "High", "Low", "Close"]
    for col in numeric_columns:
        if col in data.columns:
            data[col] = data[col].round(2)

    csv_string = data.to_csv(index=False)

    header = f"# Stock data for {symbol.upper()} from {start_date} to {end_date}\n"
    header += f"# Total records: {len(data)}\n"
    header += f"# Data retrieved on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"

    return header + csv_string


if __name__ == "__main__":
    if len(sys.argv) != 4:
        print(f"Usage: {sys.argv[0]} <TICKER> <START_DATE> <END_DATE>")
        print(f"Example: {sys.argv[0]} NVDA 2025-07-01 2026-01-15")
        sys.exit(1)

    ticker_symbol = sys.argv[1]
    start = sys.argv[2]
    end = sys.argv[3]

    result = get_stock_data(ticker_symbol, start, end)
    print(result)
