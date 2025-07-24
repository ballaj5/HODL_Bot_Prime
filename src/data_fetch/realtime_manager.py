# src/data_fetch/realtime_manager.py
import ccxt.pro
import asyncio
import logging
import json
import os
from collections import deque
from datetime import datetime, timezone
from ..shared.constants import SYMBOLS # Using your existing symbols

# --- Configuration ---
REALTIME_FEATURES_PATH = "/workspace/data/realtime_features.json"
# CORRECTED: Changed depth from 25 to 50, which is a valid limit for Bybit's API.
ORDER_BOOK_DEPTH = 50 
TAKER_TRADE_WINDOW_SECONDS = 60 # Analyze taker trades over the last minute

# --- Logging Setup ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(name)s] %(levelname)s: %(message)s')
logger = logging.getLogger("RealtimeManager")

# --- Global State (In-memory) ---
# This will hold the latest calculated features for all symbols
realtime_features = {symbol: {} for symbol in SYMBOLS}

# --- Feature Calculation Logic ---

async def order_book_loop(exchange, symbol):
    """Continuously processes order book data to calculate imbalance."""
    logger.info(f"Starting order book loop for {symbol}...")
    while True:
        try:
            orderbook = await exchange.watch_order_book(symbol + 'USDT', ORDER_BOOK_DEPTH)
            bids = orderbook['bids']
            asks = orderbook['asks']

            if not bids or not asks:
                continue

            # Calculate total volume for bids and asks
            total_bid_volume = sum([price * size for price, size in bids])
            total_ask_volume = sum([price * size for price, size in asks])
            
            # Calculate Order Book Imbalance (OBI)
            # A value > 0 means more buy pressure; < 0 means more sell pressure
            total_volume = total_bid_volume + total_ask_volume
            if total_volume > 0:
                imbalance = (total_bid_volume - total_ask_volume) / total_volume
            else:
                imbalance = 0.0
            
            # Update the global features state
            realtime_features[symbol]['order_book_imbalance'] = round(imbalance, 4)
            realtime_features[symbol]['last_update_utc'] = datetime.now(timezone.utc).isoformat()

        except Exception as e:
            logger.error(f"Error in order book loop for {symbol}: {e}", exc_info=True)
            await asyncio.sleep(5) # Wait before retrying

async def trades_loop(exchange, symbol):
    """Continuously processes public trades to calculate taker volume ratio."""
    logger.info(f"Starting trades loop for {symbol}...")
    # Use a deque to store recent trades efficiently
    recent_trades = deque()

    while True:
        try:
            trades = await exchange.watch_trades(symbol + 'USDT')
            now = datetime.now(timezone.utc)
            
            for trade in trades:
                trade['timestamp_dt'] = now
                recent_trades.append(trade)

            # Remove old trades that are outside our time window
            while recent_trades and (now - recent_trades[0]['timestamp_dt']).total_seconds() > TAKER_TRADE_WINDOW_SECONDS:
                recent_trades.popleft()

            # Calculate taker buy/sell volume
            taker_buy_volume = sum(t['cost'] for t in recent_trades if t['side'] == 'buy')
            taker_sell_volume = sum(t['cost'] for t in recent_trades if t['side'] == 'sell')

            # Calculate Taker Buy/Sell Ratio
            # A value > 1 means more aggressive buying; < 1 means more aggressive selling
            if taker_sell_volume > 0:
                taker_ratio = taker_buy_volume / taker_sell_volume
            else:
                taker_ratio = taker_buy_volume # Avoid division by zero

            # Update the global features state
            realtime_features[symbol]['taker_buy_sell_ratio'] = round(taker_ratio, 4)

        except Exception as e:
            logger.error(f"Error in trades loop for {symbol}: {e}", exc_info=True)
            await asyncio.sleep(5)

async def save_features_loop():
    """Periodically saves the calculated features to a file."""
    logger.info(f"Starting feature save loop. Output file: {REALTIME_FEATURES_PATH}")
    while True:
        await asyncio.sleep(10) # Save every 10 seconds
        try:
            # Ensure the directory exists
            os.makedirs(os.path.dirname(REALTIME_FEATURES_PATH), exist_ok=True)
            with open(REALTIME_FEATURES_PATH, 'w') as f:
                json.dump(realtime_features, f, indent=4)
        except Exception as e:
            logger.error(f"Failed to save features to file: {e}")

async def main():
    """Main function to initialize exchange and start all loops."""
    exchange = ccxt.pro.bybit({'options': {'defaultType': 'swap'}})
    
    tasks = [save_features_loop()]
    for symbol in SYMBOLS:
        tasks.append(order_book_loop(exchange, symbol))
        tasks.append(trades_loop(exchange, symbol))
        
    logger.info(f"Starting real-time feature manager for symbols: {SYMBOLS}")
    await asyncio.gather(*tasks)
    
    # This part is important for proper shutdown
    await exchange.close()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Shutdown signal received. Exiting.")