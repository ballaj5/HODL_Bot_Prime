# data_fetch/data_source.py
import os
import ccxt
import logging
from datetime import datetime
import pandas as pd

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def fetch_ohlcv_data(symbol: str, timeframe: str, since: datetime) -> pd.DataFrame | None:
    """
    Fetches OHLCV data using ccxt, trying a list of exchanges as fallbacks.
    """
    symbol_pair = f"{symbol}/USDT"
    since_ms = int(since.timestamp() * 1000)
    exchanges_to_try = ["bybit", "binance", "okx", "kucoin"]

    for ex_name in exchanges_to_try:
        try:
            exchange_class = getattr(ccxt, ex_name)
            exchange_config = {"enableRateLimit": True}
            
            # Use API keys only for Bybit, as configured
            if ex_name == "bybit":
                exchange_config.update({
                    "apiKey": os.getenv("BYBIT_API_KEY", ""),
                    "secret": os.getenv("BYBIT_API_SECRET", ""),
                })
            
            exchange = exchange_class(exchange_config)

            if not exchange.has.get("fetchOHLCV"):
                logger.debug(f"Exchange {ex_name} does not support fetchOHLCV.")
                continue

            if timeframe not in exchange.timeframes:
                logger.warning(f"{ex_name} does not support timeframe {timeframe}, skipping.")
                continue

            logger.info(f"🔄 Fetching {symbol_pair} @ {timeframe} from {ex_name}...")
            data = exchange.fetch_ohlcv(symbol_pair, timeframe, since_ms, limit=1000)
            
            if not data:
                logger.warning(f"⚠️ {ex_name} returned no data for {symbol_pair}.")
                continue

            df = pd.DataFrame(data, columns=["timestamp", "open", "high", "low", "close", "volume"])
            df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
            
            logger.info(f"✅ Successfully fetched {len(df)} rows from {ex_name}.")
            return df

        except Exception as e:
            logger.warning(f"⚠️ {ex_name} failed for {symbol_pair}: {e}")
            continue

    logger.error(f"❌ All data sources failed for {symbol_pair} on {timeframe}")
    return None