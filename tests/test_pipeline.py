import os
import unittest
from unittest.mock import patch
from src.telegram.send_alert import send_test_alert # CORRECTED: Changed 'telegram_alert' to 'send_alert'
from src.data_fetch.data_source import fetch_and_save_all_futures_data
from src.shared.constants import SYMBOLS

class TestBotPipeline(unittest.TestCase):
    @patch('src.telegram.send_alert.requests.post')
    def test_telegram_alert(self, mock_post):
        """Test sending a Telegram alert."""
        mock_post.return_value.raise_for_status = lambda: None
        send_test_alert()
        self.assertTrue(mock_post.called)
        
    @patch('src.data_fetch.data_source.ccxt.bybit')
    def test_bybit_data_fetch(self, mock_bybit):
        """Test the Bybit data fetching pipeline."""
        # Mocking the exchange and its methods
        mock_exchange = mock_bybit.return_value
        mock_exchange.fetch_ohlcv.return_value = [
            [1672531200000, 60000, 61000, 59000, 60500, 100],
            [1672531260000, 60500, 61500, 60000, 61000, 120]
        ]
        
        # Run the data fetching process
        fetch_and_save_all_futures_data()
        
        # Verify that data files are created for each symbol
        for symbol in SYMBOLS:
            # Check for the 1-minute interval file as a representative sample
            expected_file = f"/workspace/data/history/{symbol}USDT_1m.csv"
            self.assertTrue(os.path.exists(expected_file))
            # Clean up the created file
            if os.path.exists(expected_file):
                os.remove(expected_file)

if __name__ == '__main__':
    unittest.main()