# src/models/train_predictor.py
import os
import json
import logging
import pandas as pd
from src.utils.model import train_model
from src.utils.indicators import compute_indicators
from src.shared.constants import SYMBOLS, ALL_TIMEFRAMES

# --- Configuration ---
HISTORY_DATA_PATH = "/workspace/data/history"

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def train_all():
    logging.info("🚀 Starting model training cycle...")

    for symbol in SYMBOLS:
        for tf in ALL_TIMEFRAMES:
            path = f"{HISTORY_DATA_PATH}/{symbol}USDT_{tf}.csv"
            if not os.path.exists(path):
                logging.warning(f"⛔ Data file not found: {path}")
                continue
            
            try:
                df = pd.read_csv(path)
                if len(df) < 50:
                    logging.warning(f"⚠️ Insufficient data for {symbol}-{tf}")
                    continue
                
                # --- Feature Engineering ---
                ## FIX: Removed the incorrect logic that merged a single snapshot of real-time
                ## features into the entire historical dataset. The model should be trained
                ## only on historical data and its indicators. Real-time features are for
                ## making live predictions, not for historical training.
                df_with_indicators = compute_indicators(df)
                                
                # --- Model Training ---
                train_model(symbol, tf, df_with_indicators)
                logging.info(f"✅ Trained model for {symbol}-{tf}.")

            except Exception as e:
                logging.error(f"❌ Failed training for {symbol}-{tf}: {e}", exc_info=True)

if __name__ == "__main__":
    train_all()