from logger import logger
import pandas as pd

class SignalParser:
    """
    Parses market data and uses a model to generate a trading signal.
    """
    def __init__(self, model):
        self.model = model
        if self.model is None:
            logger.error("SignalParser initialized without a valid model.")
            raise ValueError("Model cannot be None.")

    def generate_signal(self, market_data: pd.DataFrame):
        """
        Analyzes market data and returns a signal ('buy', 'sell', or 'hold').
        This is a placeholder for your actual signal generation logic.
        """
        logger.debug("Generating trading signal...")
        if market_data.empty:
            logger.warning("Market data is empty, cannot generate signal.")
            return 'hold'

        # Example: Simple RSI logic. Replace with your model prediction.
        # last_rsi = market_data['rsi'].iloc[-1]
        # if last_rsi > 70:
        #     return 'sell'
        # elif last_rsi < 30:
        #     return 'buy'
        # else:
        #     return 'hold'

        # Example: Using the loaded model
        try:
            # Assume model expects the last row of features
            features = market_data.drop(columns=['close_time']).iloc[-1:]
            prediction = self.model.predict(features)[0]

            if prediction == 1:
                logger.info("Signal: BUY")
                return 'buy'
            elif prediction == -1:
                logger.info("Signal: SELL")
                return 'sell'
            else:
                logger.info("Signal: HOLD")
                return 'hold'
        except Exception as e:
            logger.error(f"Error during model prediction: {e}")
            return 'hold' # Default to holding if prediction fails