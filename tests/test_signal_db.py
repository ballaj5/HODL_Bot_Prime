# tests/test_signal_db.py
# Import from the src package, as tests are run from the project root
from src.utils.db import db

def test_store_and_load():
    """Tests if a signal can be stored and loaded correctly."""
    symbol = "TEST-BTC"
    signal = "BUY"

    db.init_db()
    db.store_signal(symbol, signal)
    loaded = db.load_last_signal(symbol)

    assert loaded == signal
    print("✅ Signal stored and retrieved successfully")

def test_should_alert():
    """Tests the logic for preventing duplicate alerts."""
    symbol = "TEST-ALERT-BTC"
    db.init_db()
    db.store_signal(symbol, "SELL")
    
    # Alert should trigger for a different signal
    assert db.should_alert(symbol, "BUY") is True
    
    # Alert should NOT trigger for the same signal
    assert db.should_alert(symbol, "SELL") is False
    print("✅ should_alert logic works correctly")

if __name__ == "__main__":
    test_store_and_load()
    test_should_alert()