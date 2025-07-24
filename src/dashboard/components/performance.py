# utils/performance.py
import os
import json
from datetime import datetime

# Logs directory
os.makedirs("logs", exist_ok=True)

PERF_LOG = "logs/performance_log.jsonl"

def render_performance_tab():
    # implement your tab-rendering logic here
    pass

def log_accuracy(symbol: str, timeframe: str, accuracy: float):
    entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "symbol": symbol,
        "timeframe": timeframe,
        "accuracy": round(accuracy, 4)
    }
    with open(PERF_LOG, "a") as f:
        f.write(json.dumps(entry) + "\n")
