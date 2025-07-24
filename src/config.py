import os
from dotenv import load_dotenv

# Load environment variables from .env file for local development
load_dotenv()

class Config:
    """
    Configuration class for the application.
    Uses os.environ to get environment variables.
    This will raise a KeyError if a variable is not set,
    which is good for "failing fast".
    """
    try:
        TELEGRAM_TOKEN = os.environ["TELEGRAM_TOKEN"]
        TELEGRAM_CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]
        API_KEY = os.environ["API_KEY"]
        API_SECRET = os.environ["API_SECRET"]
    except KeyError as e:
        raise RuntimeError(f"Error: Missing critical environment variable: {e}") from e

    # Trading parameters
    SYMBOL = 'BTC/USDT'
    TIMEFRAME = '1h'
    RSI_PERIOD = 14
    RSI_OVERBOUGHT = 70
    RSI_OVERSOLD = 30
    AMOUNT = 0.001

    # Database
    DB_PATH = "trading_bot.db"

    # Model
    MODEL_PATH = "model.pkl"
    BACKUP_MODEL_PATH = "backup_model.pkl" # Path to a backup model

    # Logging
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# Instantiate config
config = Config()