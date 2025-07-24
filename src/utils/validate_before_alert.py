import os
import pandas as pd
import pickle
import logging
from src.utils.indicators import compute_indicators # Assuming this path is correct when running the script
from src.shared.constants import ALL_TIMEFRAMES, SYMBOLS # Assuming constants are here

logging.basicConfig(level=logging.INFO)

# CORRECTED: Use absolute paths consistent with the rest of your application
DATA_DIR = "/workspace/data/history"
MODEL_DIR = "/workspace/models_data"

def validate_csv(file_path):
    if not os.path.exists(file_path):
        return False, "❌ File missing"

    try:
        df = pd.read_csv(file_path)
        if df.isnull().values.any() or len(df) < 30:
            return False, "❌ Corrupt or insufficient data"
        df = compute_indicators(df)
        missing = [col for col in ["rsi", "ema", "macd"] if col not in df]
        if missing:
            return False, f"❌ Missing indicators: {missing}"
        return True, "✅ Valid data"
    except Exception as e:
        return False, f"❌ Error: {str(e)}"

def validate_model(model_path):
    if not os.path.exists(model_path):
        return False, "❌ Model missing"
    try:
        with open(model_path, "rb") as f:
            model = pickle.load(f)
        if not hasattr(model, "predict"):
            return False, "❌ Model is not a predictor"
        return True, "✅ Model loaded"
    except Exception as e:
        return False, f"❌ Load error: {str(e)}"

def run_validation():
    summary = []
    # CORRECTED: Iterate through symbols and timeframes for clarity
    for symbol in SYMBOLS:
        for tf in ALL_TIMEFRAMES:
            # Construct correct paths based on the app's naming convention
            csv_file = f"{symbol}USDT_{tf}.csv"
            model_file = f"{symbol}USDT_{tf}_model.pkl"
            
            fpath = os.path.join(DATA_DIR, csv_file)
            mpath = os.path.join(MODEL_DIR, model_file)

            valid_data, data_msg = validate_csv(fpath)
            valid_model, model_msg = validate_model(mpath)

            summary.append(f"{symbol}_{tf} → {data_msg} | {model_msg}")
    return summary

if __name__ == "__main__":
    results = run_validation()
    print("\n📋 Validation Summary:")
    for line in results:
        print(line)