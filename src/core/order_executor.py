import ccxt.async_support as ccxt
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from logger import logger

# Define what exceptions should trigger a retry
RETRYABLE_EXCEPTIONS = (
    ccxt.NetworkError,
    ccxt.ExchangeError,
    ccxt.RequestTimeout,
)

class OrderExecutor:
    """
    Handles all exchange interactions, such as placing orders and fetching data.
    Includes robust retry logic for network-related issues.
    """
    def __init__(self, api_key, api_secret):
        self.exchange = ccxt.binance({
            'apiKey': api_key,
            'secret': api_secret,
            'options': {
                'defaultType': 'spot',
            },
        })

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        retry=retry_if_exception_type(RETRYABLE_EXCEPTIONS),
        before_sleep=lambda retry_state: logger.warning(f"Retrying API call due to {retry_state.outcome.exception()}. Attempt #{retry_state.attempt_number}")
    )
    async def fetch_balance(self, currency='USDT'):
        """Fetches the balance for a given currency with retry logic."""
        logger.info(f"Fetching balance for {currency}...")
        balance = await self.exchange.fetch_balance()
        return balance[currency]['free']

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        retry=retry_if_exception_type(RETRYABLE_EXCEPTIONS)
    )
    async def create_order(self, symbol, order_type, side, amount):
        """Creates an order with retry logic."""
        logger.info(f"Creating {side} {order_type} order for {amount} {symbol}...")
        try:
            order = await self.exchange.create_order(symbol, order_type, side, amount)
            logger.info(f"Successfully placed order: {order['id']}")
            return order
        except Exception as e:
            logger.error(f"Failed to create order: {e}")
            raise # Re-raise the exception to allow tenacity to handle retries

    async def close_connection(self):
        """Closes the exchange connection."""
        await self.exchange.close()
        logger.info("Exchange connection closed.")