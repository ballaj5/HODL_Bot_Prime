# tests/core/test_db_manager.py
import pytest
import sqlite3
from unittest.mock import patch
from src.core.db_manager import DBManager

@pytest.fixture
def memory_db_manager():
    """
    Fixture to create a DBManager instance with an in-memory SQLite database.
    This ensures tests are isolated and don't interact with the real database.
    """
    # ':memory:' tells SQLite to use RAM instead of a file
    manager = DBManager(db_path=":memory:")
    yield manager
    # Teardown: close the connection after the test is done
    manager.close()

def test_db_connection(memory_db_manager):
    """Tests that the database connection is successfully established."""
    assert memory_db_manager.conn is not None
    assert isinstance(memory_db_manager.conn, sqlite3.Connection)

def test_create_trades_table(memory_db_manager):
    """Tests the creation of the 'trades' table."""
    # Check that the table does not exist initially
    assert not memory_db_manager.check_for_existing_table("trades")
    
    # Run the creation method
    memory_db_manager.create_trades_table()
    
    # Check that the table now exists
    assert memory_db_manager.check_for_existing_table("trades")

def test_log_trade(memory_db_manager):
    """Tests that a trade is correctly logged into the database."""
    # First, ensure the table exists
    memory_db_manager.create_trades_table()
    
    # Log a sample trade
    symbol = "BTC/USDT"
    trade_type = "buy"
    price = 50000.0
    amount = 0.01
    status = "filled"
    memory_db_manager.log_trade(symbol, trade_type, price, amount, status)
    
    # Verify the trade was inserted by querying the database directly
    cursor = memory_db_manager.conn.cursor()
    cursor.execute("SELECT * FROM trades WHERE symbol=?", (symbol,))
    trade = cursor.fetchone()
    
    assert trade is not None
    assert trade["symbol"] == symbol
    assert trade["type"] == trade_type
    assert trade["price"] == price
    assert trade["amount"] == amount
    assert trade["status"] == status

@patch('src.core.db_manager.sqlite3.connect')
def test_connection_failure_raises_exception(mock_connect):
    """Tests that a connection error during initialization raises an exception."""
    # Arrange: Make the connect call raise an error
    mock_connect.side_effect = sqlite3.Error("Test connection error")
    
    # Act & Assert: Check that DBManager raises a RuntimeError
    with pytest.raises(sqlite3.Error):
        DBManager(db_path="dummy_path.db")