# shared/constants.py
"""
Central location for shared constants like symbols and timeframes
to avoid duplication across different scripts.
"""

SYMBOLS = ["BTC", "ETH", "SOL", "DOGE", "XRP", "ADA", "WIF", "1000PEPE"]

# Timeframes to fetch directly from the exchange
NATIVE_TIMEFRAMES = ["1m", "5m", "15m", "30m", "1h", "1d"]

# All timeframes to be used in the model, including simulated ones
ALL_TIMEFRAMES = ["1m", "5m", "10m", "15m", "30m", "1h", "1d"]