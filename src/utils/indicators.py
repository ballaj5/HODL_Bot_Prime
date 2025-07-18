# utils/indicators.py
import pandas as pd
import logging

def compute_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """
    Computes technical indicators (RSI, EMA, MACD) and appends them
    as columns to the input DataFrame.

    Args:
        df: DataFrame with 'close' prices.

    Returns:
        The original DataFrame with added indicator columns.
    """
    if df.empty:
        logging.warning("Input DataFrame is empty, cannot compute indicators.")
        return df

    close = df["close"]

    # RSI (Relative Strength Index)
    delta = close.diff()
    gain = delta.where(delta > 0, 0).ewm(alpha=1/14, adjust=False).mean()
    loss = -delta.where(delta < 0, 0).ewm(alpha=1/14, adjust=False).mean()
    
    # Avoid division by zero
    rs = gain / loss.replace(0, 1e-9) # Add small epsilon to avoid zero division
    df['rsi'] = 100 - (100 / (1 + rs))

    # EMA (Exponential Moving Average)
    df['ema'] = close.ewm(span=14, adjust=False).mean()

    # MACD (Moving Average Convergence Divergence)
    ema12 = close.ewm(span=12, adjust=False).mean()
    ema26 = close.ewm(span=26, adjust=False).mean()
    df['macd'] = ema12 - ema26
    
    # Fill any initial NaN values that result from rolling calculations
    df.fillna(method='bfill', inplace=True)

    return df