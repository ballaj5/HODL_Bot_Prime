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
    """Fetches data for a single symbol and timeframe and saves it to a CSV."""
    now = datetime.utcnow()
    start_date = now - timedelta(days=30) 
    df = fetch_ohlcv_data(symbol, timeframe, start_date)
    if df is not None and not df.empty:
        output_path = f"data/history/{symbol}USDT_{timeframe}.csv"
        df.to_csv(output_path, index=False)
    else:
        logging.error(f"❌ No data fetched for {symbol} on {timeframe}.")

def simulate_10m(symbol: str):
    """Simulates a 10-minute timeframe by resampling the 1-minute data."""
    try:
        path_1m = f"data/history/{symbol}USDT_1m.csv"
        if not os.path.exists(path_1m):
            logging.warning(f"⚠️ Cannot simulate 10m for {symbol}, 1m data is missing.")
            return
        df_1m = pd.read_csv(path_1m, parse_dates=['timestamp'])
        df_1m = df_1m.set_index('timestamp')
        resampled_df = df_1m.resample('10T').agg({
            'open': 'first', 'high': 'max', 'low': 'min', 'close': 'last', 'volume': 'sum'
        }).dropna().reset_index()
        output_path = f"data/history/{symbol}USDT_10m.csv"
        resampled_df.to_csv(output_path, index=False)
        logging.info(f"🧪 {symbol} 10m timeframe simulated successfully.")
    except Exception as e:
        logging.error(f"❌ Failed to simulate 10m for {symbol}: {e}")

def main():
    """Main function to orchestrate data fetching and processing."""
    for symbol in SYMBOLS:
        for tf in NATIVE_TIMEFRAMES:
            fetch_and_store(symbol, tf)
        simulate_10m(symbol)

if __name__ == "__main__":
    main()