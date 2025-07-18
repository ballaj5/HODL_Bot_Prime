# src/data_fetch/fetch_futures_data.py
import os
import logging
import pandas as pd
from datetime import datetime, timedelta
# Use relative imports to find sibling modules
from .data_source import fetch_ohlcv_data
from ..shared.constants import SYMBOLS, NATIVE_TIMEFRAMES

logging.basicConfig(level=logging.INFO)
os.makedirs("data/history", exist_ok=True)

def fetch_and_store(symbol: str, timeframe: str):
    now = datetime.utcnow()
    start_date = now - timedelta(days=30) 
    df = fetch_ohlcv_data(symbol, timeframe, start_date)
    if df is not None and not df.empty:
        df.to_csv(f"data/history/{symbol}USDT_{timeframe}.csv", index=False)
    else:
        logging.error(f"❌ No data for {symbol} on {timeframe}.")

def simulate_10m(symbol: str):
    try:
        path_1m = f"data/history/{symbol}USDT_1m.csv"
        if not os.path.exists(path_1m):
            logging.warning(f"⚠️ Cannot simulate 10m for {symbol}, 1m data missing.")
            return
        df_1m = pd.read_csv(path_1m, parse_dates=['timestamp'])
        df_1m = df_1m.set_index('timestamp')
        # FIX: Use '10min' instead of deprecated '10T'
        resampled_df = df_1m.resample('10min').agg({
            'open': 'first', 'high': 'max', 'low': 'min', 'close': 'last', 'volume': 'sum'
        }).dropna().reset_index()
        resampled_df.to_csv(f"data/history/{symbol}USDT_10m.csv", index=False)
        logging.info(f"🧪 {symbol} 10m timeframe simulated.")
    except Exception as e:
        logging.error(f"❌ Failed to simulate 10m for {symbol}: {e}")

def main():
    for symbol in SYMBOLS:
        for tf in NATIVE_TIMEFRAMES:
            fetch_and_store(symbol, tf)
        simulate_10m(symbol)

if __name__ == "__main__":
    main()