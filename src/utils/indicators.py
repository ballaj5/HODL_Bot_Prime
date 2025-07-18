# src/utils/indicators.py
import pandas as pd
import logging

def compute_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """Computes technical indicators and appends them as columns."""
    if df.empty:
        logging.warning("Input DataFrame is empty, cannot compute indicators.")
        return df

    close = df["close"]
    
    delta = close.diff()
    gain = delta.where(delta > 0, 0).ewm(alpha=1/14, adjust=False).mean()
    loss = -delta.where(delta < 0, 0).ewm(alpha=1/14, adjust=False).mean()
    rs = gain / loss.replace(0, 1e-9)
    df['rsi'] = 100 - (100 / (1 + rs))

    df['ema'] = close.ewm(span=14, adjust=False).mean()

    ema12 = close.ewm(span=12, adjust=False).mean()
    ema26 = close.ewm(span=26, adjust=False).mean()
    df['macd'] = ema12 - ema26
    
    # FIX: Use the modern `bfill()` method instead of the deprecated one
    df.bfill(inplace=True)

    return df