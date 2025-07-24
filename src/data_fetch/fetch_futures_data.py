# src/data_fetch/fetch_futures_data.py
import os
import logging
import pandas as pd
from datetime import datetime, timedelta
from .data_source import fetch_ohlcv_data
from ..shared.constants import SYMBOLS, NATIVE_TIMEFRAMES

# Define a persistent base path for data, aligning with the single volume strategy
DATA_BASE_PATH = "/workspace/data/history"

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
os.makedirs(DATA_BASE_PATH, exist_ok=True)

def get_csv_path(symbol: str, timeframe: str) -> str:
    """Helper function to get the full, consistent path for CSV files."""
    return f"{DATA_BASE_PATH}/{symbol}USDT_{timeframe}.csv"

def fetch_and_store(symbol: str, timeframe: str):
    now = datetime.utcnow()
    start_date = now - timedelta(days=30) 
    df = fetch_ohlcv_data(symbol, timeframe, start_date)
    
    if df is not None and not df.empty:
        df.to_csv(get_csv_path(symbol, timeframe), index=False)
    else:
        logging.error(f"❌ No data for {symbol} on {timeframe}.")

def simulate_10m(symbol: str):
    try:
        path_1m = get_csv_path(symbol, '1m')
        if not os.path.exists(path_1m):
            logging.warning(f"⚠️ Cannot simulate 10m for {symbol}, 1m data missing at {path_1m}.")
            return
            
        df_1m = pd.read_csv(path_1m, parse_dates=['timestamp'])
        df_1m = df_1m.set_index('timestamp')
        
        resampled_df = df_1m.resample('10T').agg({
            'open': 'first', 'high': 'max', 'low': 'min', 'close': 'last', 'volume': 'sum'
        }).dropna().reset_index()
        
        resampled_df.to_csv(get_csv_path(symbol, '10m'), index=False)
        logging.info(f"🧪 {symbol} 10m timeframe simulated and saved.")
    except Exception as e:
        logging.error(f"❌ Failed to simulate 10m for {symbol}: {e}")

def main():
    logging.info("--- Fetching All Futures Data ---")
    for symbol in SYMBOLS:
        for tf in NATIVE_TIMEFRAMES:
            fetch_and_store(symbol, tf)
        simulate_10m(symbol)
    logging.info("--- Data Fetching Complete ---")

if __name__ == "__main__":
    main()
