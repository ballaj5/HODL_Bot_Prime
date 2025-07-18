# tests/test_data_source.py
import pytest
import pandas as pd
from unittest.mock import patch, MagicMock
from data_fetch.data_source import fetch_ohlcv_data
from datetime import datetime

@patch('data_fetch.data_source.ccxt.bybit')
def test_fetch_ohlcv_data_success(mock_bybit):
    """
    Tests successful data fetching by mocking the ccxt exchange object.
    """
    # Arrange: Create a mock DataFrame to be returned by the API call
    mock_data = [
        [1672531200000, 16500, 16600, 16400, 16550, 100],
        [1672534800000, 16550, 16700, 16500, 16650, 120],
    ]
    mock_exchange_instance = MagicMock()
    mock_exchange_instance.fetch_ohlcv.return_value = mock_data
    mock_exchange_instance.timeframes = ['1h']
    mock_bybit.return_value = mock_exchange_instance

    # Act: Call the function we are testing
    df = fetch_ohlcv_data(symbol="BTC", timeframe="1h", since=datetime.utcnow())

    # Assert: Check that the DataFrame is correct
    assert isinstance(df, pd.DataFrame)
    assert len(df) == 2
    assert 'close' in df.columns
    # Check that the exchange's fetch_ohlcv method was called
    mock_exchange_instance.fetch_ohlcv.assert_called_once()
    print("\n✅ test_fetch_ohlcv_data_success passed")

# To run this test, install pytest (`pip install pytest`)
# and run `pytest` from your project's root directory.