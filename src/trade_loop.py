import asyncio
from logger import logger
from config import config
from db_manager import DBManager
from model_validator import load_model
from order_executor import OrderExecutor
from signal_parser import SignalParser

class TradeLoop:
    def __init__(self):
        self.is_running = False
        # Load model with fallback
        self.model = load_model(config.MODEL_PATH, config.BACKUP_MODEL_PATH)
        # Initialize components
        self.db_manager = DBManager(config.DB_PATH)
        self.db_manager.create_trades_table()
        self.order_executor = OrderExecutor(config.API_KEY, config.API_SECRET)
        self.signal_parser = SignalParser(self.model)
        # State
        self.in_position = False

    async def run(self):
        """The main trading loop."""
        self.is_running = True
        logger.info("Trading bot started. Press Ctrl+C to stop.")

        while self.is_running:
            try:
                # 1. Fetch data (this part needs to be implemented)
                # For example, using the exchange object from the order executor
                logger.info(f"Fetching market data for {config.SYMBOL}...")
                ohlcv = await self.order_executor.exchange.fetch_ohlcv(config.SYMBOL, config.TIMEFRAME)
                # Create a pandas DataFrame
                import pandas as pd
                market_data = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])

                # 2. Generate signal
                signal = self.signal_parser.generate_signal(market_data)

                # 3. Execute trade based on signal
                if signal == 'buy' and not self.in_position:
                    logger.info("Buy signal received. Executing trade.")
                    order = await self.order_executor.create_order(
                        config.SYMBOL, 'market', 'buy', config.AMOUNT
                    )
                    self.db_manager.log_trade(config.SYMBOL, 'buy', order['price'], config.AMOUNT, 'filled')
                    self.in_position = True

                elif signal == 'sell' and self.in_position:
                    logger.info("Sell signal received. Executing trade.")
                    order = await self.order_executor.create_order(
                        config.SYMBOL, 'market', 'sell', config.AMOUNT
                    )
                    self.db_manager.log_trade(config.SYMBOL, 'sell', order['price'], config.AMOUNT, 'filled')
                    self.in_position = False

                else: # hold
                    logger.info("Hold signal received. No action taken.")

                # Wait for the next candle
                await asyncio.sleep(3600) # Wait for 1 hour for the next 1h candle

            except asyncio.CancelledError:
                logger.info("Trade loop cancelled.")
                self.is_running = False
            except Exception as e:
                logger.error(f"An error occurred in the trade loop: {e}", exc_info=True)
                # Decide on a cool-down period before retrying
                await asyncio.sleep(60)

    async def stop(self):
        """Stops the trading loop gracefully."""
        logger.info("Stopping trade loop...")
        self.is_running = False
        # Close connections
        await self.order_executor.close_connection()
        self.db_manager.close()
        logger.info("Bot has been shut down gracefully.")


async def main():
    """Main function to run the bot."""
    loop = TradeLoop()
    try:
        await loop.run()
    except KeyboardInterrupt:
        await loop.stop()

if __name__ == "__main__":
    asyncio.run(main())