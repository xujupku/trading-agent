#!/usr/bin/env python3
"""Fetch company fundamental data using yfinance.

Usage:
    python get_fundamentals.py <TICKER> [COMMAND] [OPTIONS]

Commands:
    overview    Company fundamentals overview (default)
    balance     Balance sheet data
    cashflow    Cash flow statement
    income      Income statement
    insider     Insider transactions
    all         All of the above

Options:
    --freq annual|quarterly    Financial statement frequency (default: quarterly)
    --date YYYY-MM-DD          Filter data up to this date (prevent look-ahead)

Examples:
    python get_fundamentals.py NVDA
    python get_fundamentals.py AAPL balance --freq quarterly --date 2026-01-15
    python get_fundamentals.py TSLA all --date 2026-01-15
"""

import sys
import os
import logging
from datetime import datetime

import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _shared import yf_retry, get_ticker

logger = logging.getLogger(__name__)


def filter_financials_by_date(data: pd.DataFrame, curr_date: str) -> pd.DataFrame:
    if not curr_date or data.empty:
        return data
    cutoff = pd.Timestamp(curr_date)
    mask = pd.to_datetime(data.columns, errors="coerce") <= cutoff
    return data.loc[:, mask]


def get_overview(ticker: str) -> str:
    try:
        ticker_obj = get_ticker(ticker)
        info = yf_retry(lambda: ticker_obj.info)

        if not info:
            return f"No fundamentals data found for symbol '{ticker}'"

        fields = [
            ("Name", info.get("longName")),
            ("Sector", info.get("sector")),
            ("Industry", info.get("industry")),
            ("Market Cap", info.get("marketCap")),
            ("PE Ratio (TTM)", info.get("trailingPE")),
            ("Forward PE", info.get("forwardPE")),
            ("PEG Ratio", info.get("pegRatio")),
            ("Price to Book", info.get("priceToBook")),
            ("EPS (TTM)", info.get("trailingEps")),
            ("Forward EPS", info.get("forwardEps")),
            ("Dividend Yield", info.get("dividendYield")),
            ("Beta", info.get("beta")),
            ("52 Week High", info.get("fiftyTwoWeekHigh")),
            ("52 Week Low", info.get("fiftyTwoWeekLow")),
            ("50 Day Average", info.get("fiftyDayAverage")),
            ("200 Day Average", info.get("twoHundredDayAverage")),
            ("Revenue (TTM)", info.get("totalRevenue")),
            ("Gross Profit", info.get("grossProfits")),
            ("EBITDA", info.get("ebitda")),
            ("Net Income", info.get("netIncomeToCommon")),
            ("Profit Margin", info.get("profitMargins")),
            ("Operating Margin", info.get("operatingMargins")),
            ("Return on Equity", info.get("returnOnEquity")),
            ("Return on Assets", info.get("returnOnAssets")),
            ("Debt to Equity", info.get("debtToEquity")),
            ("Current Ratio", info.get("currentRatio")),
            ("Book Value", info.get("bookValue")),
            ("Free Cash Flow", info.get("freeCashflow")),
        ]

        lines = []
        for label, value in fields:
            if value is not None:
                lines.append(f"{label}: {value}")

        header = f"# Company Fundamentals for {ticker.upper()}\n"
        header += f"# Data retrieved on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        return header + "\n".join(lines)

    except Exception as e:
        return f"Error retrieving fundamentals for {ticker}: {str(e)}"


def get_balance_sheet(ticker: str, freq: str = "quarterly", curr_date: str = None) -> str:
    try:
        ticker_obj = get_ticker(ticker)
        if freq.lower() == "quarterly":
            data = yf_retry(lambda: ticker_obj.quarterly_balance_sheet)
        else:
            data = yf_retry(lambda: ticker_obj.balance_sheet)

        data = filter_financials_by_date(data, curr_date)

        if data.empty:
            return f"No balance sheet data found for symbol '{ticker}'"

        csv_string = data.to_csv()
        header = f"# Balance Sheet data for {ticker.upper()} ({freq})\n"
        header += f"# Data retrieved on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        return header + csv_string

    except Exception as e:
        return f"Error retrieving balance sheet for {ticker}: {str(e)}"


def get_cashflow(ticker: str, freq: str = "quarterly", curr_date: str = None) -> str:
    try:
        ticker_obj = get_ticker(ticker)
        if freq.lower() == "quarterly":
            data = yf_retry(lambda: ticker_obj.quarterly_cashflow)
        else:
            data = yf_retry(lambda: ticker_obj.cashflow)

        data = filter_financials_by_date(data, curr_date)

        if data.empty:
            return f"No cash flow data found for symbol '{ticker}'"

        csv_string = data.to_csv()
        header = f"# Cash Flow data for {ticker.upper()} ({freq})\n"
        header += f"# Data retrieved on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        return header + csv_string

    except Exception as e:
        return f"Error retrieving cash flow for {ticker}: {str(e)}"


def get_income_statement(ticker: str, freq: str = "quarterly", curr_date: str = None) -> str:
    try:
        ticker_obj = get_ticker(ticker)
        if freq.lower() == "quarterly":
            data = yf_retry(lambda: ticker_obj.quarterly_income_stmt)
        else:
            data = yf_retry(lambda: ticker_obj.income_stmt)

        data = filter_financials_by_date(data, curr_date)

        if data.empty:
            return f"No income statement data found for symbol '{ticker}'"

        csv_string = data.to_csv()
        header = f"# Income Statement data for {ticker.upper()} ({freq})\n"
        header += f"# Data retrieved on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        return header + csv_string

    except Exception as e:
        return f"Error retrieving income statement for {ticker}: {str(e)}"


def get_insider_transactions(ticker: str) -> str:
    try:
        ticker_obj = get_ticker(ticker)
        data = yf_retry(lambda: ticker_obj.insider_transactions)

        if data is None or data.empty:
            return f"No insider transactions data found for symbol '{ticker}'"

        csv_string = data.to_csv()
        header = f"# Insider Transactions data for {ticker.upper()}\n"
        header += f"# Data retrieved on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        return header + csv_string

    except Exception as e:
        return f"Error retrieving insider transactions for {ticker}: {str(e)}"


def parse_args(argv):
    ticker = argv[1] if len(argv) > 1 else None
    command = argv[2] if len(argv) > 2 and not argv[2].startswith("--") else "overview"
    freq = "quarterly"
    date = None

    i = 2 if command != "overview" else 2
    while i < len(argv):
        if argv[i] == "--freq" and i + 1 < len(argv):
            freq = argv[i + 1]
            i += 2
        elif argv[i] == "--date" and i + 1 < len(argv):
            date = argv[i + 1]
            i += 2
        elif not argv[i].startswith("--") and i == 2:
            command = argv[i]
            i += 1
        else:
            i += 1

    return ticker, command, freq, date


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} <TICKER> [COMMAND] [OPTIONS]")
        print(f"Commands: overview, balance, cashflow, income, insider, all")
        print(f"Options: --freq annual|quarterly  --date YYYY-MM-DD")
        print(f"\nExamples:")
        print(f"  {sys.argv[0]} NVDA")
        print(f"  {sys.argv[0]} AAPL balance --freq quarterly --date 2026-01-15")
        print(f"  {sys.argv[0]} TSLA all --date 2026-01-15")
        sys.exit(1)

    ticker_symbol, cmd, frequency, filter_date = parse_args(sys.argv)

    separator = "\n" + "=" * 60 + "\n"

    if cmd == "overview":
        print(get_overview(ticker_symbol))
    elif cmd == "balance":
        print(get_balance_sheet(ticker_symbol, frequency, filter_date))
    elif cmd == "cashflow":
        print(get_cashflow(ticker_symbol, frequency, filter_date))
    elif cmd == "income":
        print(get_income_statement(ticker_symbol, frequency, filter_date))
    elif cmd == "insider":
        print(get_insider_transactions(ticker_symbol))
    elif cmd == "all":
        print(get_overview(ticker_symbol))
        print(separator)
        print(get_balance_sheet(ticker_symbol, frequency, filter_date))
        print(separator)
        print(get_cashflow(ticker_symbol, frequency, filter_date))
        print(separator)
        print(get_income_statement(ticker_symbol, frequency, filter_date))
        print(separator)
        print(get_insider_transactions(ticker_symbol))
    else:
        print(f"Unknown command: {cmd}")
        print(f"Available commands: overview, balance, cashflow, income, insider, all")
        sys.exit(1)
