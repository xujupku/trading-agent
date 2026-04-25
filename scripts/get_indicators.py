#!/usr/bin/env python3
"""Calculate technical indicators for a stock using stockstats + yfinance.

Usage:
    python get_indicators.py <TICKER> <INDICATOR> <CURR_DATE> [LOOK_BACK_DAYS]

Example:
    python get_indicators.py NVDA rsi 2026-01-15 30
    python get_indicators.py AAPL macd 2026-01-15
    python get_indicators.py TSLA close_50_sma,rsi,macd 2026-01-15 60

Supported indicators:
    Moving Averages: close_50_sma, close_200_sma, close_10_ema
    MACD:           macd, macds, macdh
    Momentum:       rsi, mfi
    Volatility:     boll, boll_ub, boll_lb, atr
    Volume:         vwma

Multiple indicators can be comma-separated (e.g. "rsi,macd,atr").
"""

import sys
import os
import logging
from datetime import datetime

import pandas as pd
from stockstats import wrap
from dateutil.relativedelta import relativedelta

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _shared import load_ohlcv

logger = logging.getLogger(__name__)

INDICATOR_DESCRIPTIONS = {
    "close_50_sma": (
        "50 SMA: A medium-term trend indicator. "
        "Usage: Identify trend direction and serve as dynamic support/resistance. "
        "Tips: It lags price; combine with faster indicators for timely signals."
    ),
    "close_200_sma": (
        "200 SMA: A long-term trend benchmark. "
        "Usage: Confirm overall market trend and identify golden/death cross setups. "
        "Tips: It reacts slowly; best for strategic trend confirmation rather than frequent trading entries."
    ),
    "close_10_ema": (
        "10 EMA: A responsive short-term average. "
        "Usage: Capture quick shifts in momentum and potential entry points. "
        "Tips: Prone to noise in choppy markets; use alongside longer averages for filtering false signals."
    ),
    "macd": (
        "MACD: Computes momentum via differences of EMAs. "
        "Usage: Look for crossovers and divergence as signals of trend changes. "
        "Tips: Confirm with other indicators in low-volatility or sideways markets."
    ),
    "macds": (
        "MACD Signal: An EMA smoothing of the MACD line. "
        "Usage: Use crossovers with the MACD line to trigger trades. "
        "Tips: Should be part of a broader strategy to avoid false positives."
    ),
    "macdh": (
        "MACD Histogram: Shows the gap between the MACD line and its signal. "
        "Usage: Visualize momentum strength and spot divergence early. "
        "Tips: Can be volatile; complement with additional filters in fast-moving markets."
    ),
    "rsi": (
        "RSI: Measures momentum to flag overbought/oversold conditions. "
        "Usage: Apply 70/30 thresholds and watch for divergence to signal reversals. "
        "Tips: In strong trends, RSI may remain extreme; always cross-check with trend analysis."
    ),
    "boll": (
        "Bollinger Middle: A 20 SMA serving as the basis for Bollinger Bands. "
        "Usage: Acts as a dynamic benchmark for price movement. "
        "Tips: Combine with the upper and lower bands to effectively spot breakouts or reversals."
    ),
    "boll_ub": (
        "Bollinger Upper Band: Typically 2 standard deviations above the middle line. "
        "Usage: Signals potential overbought conditions and breakout zones. "
        "Tips: Confirm signals with other tools; prices may ride the band in strong trends."
    ),
    "boll_lb": (
        "Bollinger Lower Band: Typically 2 standard deviations below the middle line. "
        "Usage: Indicates potential oversold conditions. "
        "Tips: Use additional analysis to avoid false reversal signals."
    ),
    "atr": (
        "ATR: Averages true range to measure volatility. "
        "Usage: Set stop-loss levels and adjust position sizes based on current market volatility. "
        "Tips: It's a reactive measure, so use it as part of a broader risk management strategy."
    ),
    "vwma": (
        "VWMA: A moving average weighted by volume. "
        "Usage: Confirm trends by integrating price action with volume data. "
        "Tips: Watch for skewed results from volume spikes; use in combination with other volume analyses."
    ),
    "mfi": (
        "MFI: The Money Flow Index uses both price and volume to measure buying and selling pressure. "
        "Usage: Identify overbought (>80) or oversold (<20) conditions and confirm the strength of trends or reversals. "
        "Tips: Use alongside RSI or MACD to confirm signals; divergence between price and MFI can indicate potential reversals."
    ),
}

def get_indicator(symbol: str, indicator: str, curr_date: str, look_back_days: int = 30) -> str:
    if indicator not in INDICATOR_DESCRIPTIONS:
        return (
            f"Error: Indicator '{indicator}' is not supported.\n"
            f"Supported indicators: {', '.join(sorted(INDICATOR_DESCRIPTIONS.keys()))}"
        )

    curr_date_dt = datetime.strptime(curr_date, "%Y-%m-%d")
    before = curr_date_dt - relativedelta(days=look_back_days)

    try:
        data = load_ohlcv(symbol, curr_date)
        df = wrap(data)
        df["Date"] = df["Date"].dt.strftime("%Y-%m-%d")
        df[indicator]

        result_dict = {}
        for _, row in df.iterrows():
            date_str = row["Date"]
            val = row[indicator]
            result_dict[date_str] = "N/A" if pd.isna(val) else str(val)

        current_dt = curr_date_dt
        date_values = []
        while current_dt >= before:
            date_str = current_dt.strftime("%Y-%m-%d")
            value = result_dict.get(date_str, "N/A: Not a trading day (weekend or holiday)")
            date_values.append((date_str, value))
            current_dt = current_dt - relativedelta(days=1)

        ind_string = ""
        for date_str, value in date_values:
            ind_string += f"{date_str}: {value}\n"

    except Exception as e:
        return f"Error calculating indicator '{indicator}' for {symbol}: {str(e)}"

    result_str = (
        f"## {indicator} values from {before.strftime('%Y-%m-%d')} to {curr_date}:\n\n"
        + ind_string
        + "\n\n"
        + INDICATOR_DESCRIPTIONS.get(indicator, "No description available.")
    )
    return result_str


if __name__ == "__main__":
    if len(sys.argv) < 4:
        print(f"Usage: {sys.argv[0]} <TICKER> <INDICATOR(s)> <CURR_DATE> [LOOK_BACK_DAYS]")
        print(f"Example: {sys.argv[0]} NVDA rsi 2026-01-15 30")
        print(f"         {sys.argv[0]} AAPL close_50_sma,macd,rsi 2026-01-15 60")
        print(f"\nSupported indicators: {', '.join(sorted(INDICATOR_DESCRIPTIONS.keys()))}")
        sys.exit(1)

    ticker_symbol = sys.argv[1]
    indicators_arg = sys.argv[2]
    curr_date = sys.argv[3]
    look_back = int(sys.argv[4]) if len(sys.argv) > 4 else 30

    indicators = [ind.strip() for ind in indicators_arg.split(",")]

    for ind in indicators:
        result = get_indicator(ticker_symbol, ind, curr_date, look_back)
        print(result)
        if len(indicators) > 1:
            print("\n" + "=" * 60 + "\n")
