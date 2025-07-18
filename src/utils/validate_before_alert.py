import os
import pandas as pd
import pickle
import logging
from utils.indicators import compute_indicators

logging.basicConfig(level=logging.INFO)

DATA_DIR = "data/history"
MODEL_DIR = "models"
REQUIRED_FEATURES = ["open", "high", "low", "close", "volume"]

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
    for file in os.listdir(DATA_DIR):
        if not file.endswith(".csv"):
            continue
        symbol = file.split("_")[0]
        tf = file.split("_")[1].replace(".csv", "")
        fpath = os.path.join(DATA_DIR, file)
        mpath = os.path.join(MODEL_DIR, f"{symbol}_model.pkl")

        valid_data, data_msg = validate_csv(fpath)
        valid_model, model_msg = validate_model(mpath)

        summary.append(f"{symbol}_{tf} → {data_msg} | {model_msg}")
    return summary

if __name__ == "__main__":
    results = run_validation()
    print("\n📋 Validation Summary:")
    for line in results:
        print(line)
