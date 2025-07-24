import pytest
from unittest.mock import patch
# Use the refactored function name
from telegram.send_alert import process_and_send_alert

# Mock the downstream dependencies of the function under test
@patch('telegram.send_alert.generate_commentary')
@patch('telegram.send_alert._send_telegram_message')
@patch('telegram.send_alert._log_jsonl')
def test_alert_sent_when_confidence_is_high(mock_log, mock_telegram, mock_llm):
    """
    Tests that a Telegram message is sent for a high-confidence signal.
    """
    # Arrange
    mock_llm.return_value = "This is a test commentary."
    sample_context = {
        "symbol": "BTC",
        "confidence": 85.0,
        "signal": "LONG"
    }

    # Act
    process_and_send_alert(sample_context)

    # Assert
    # Check that the Telegram function was called once
    mock_telegram.assert_called_once()
    # Check that the message contains the key info
    sent_text = mock_telegram.call_args[0][0]
    assert "BTC" in sent_text
    assert "LONG" in sent_text
    assert "85.00%" in sent_text
    assert "test commentary" in sent_text
    # Ensure the alert was logged
    assert mock_log.call_count == 1

@patch('telegram.send_alert.generate_commentary')
@patch('telegram.send_alert._send_telegram_message')
@patch('telegram.send_alert._log_jsonl')
def test_alert_skipped_when_confidence_is_low(mock_log, mock_telegram, mock_llm):
    """
    Tests that no message is sent for a low-confidence signal.
    """
    # Arrange
    sample_context = {
        "symbol": "ETH",
        "confidence": 65.0,
        "signal": "SHORT"
    }

    # Act
    process_and_send_alert(sample_context)

    # Assert
    # Ensure the Telegram and LLM functions were NEVER called
    mock_telegram.assert_not_called()
    mock_llm.assert_not_called()
    # Check that the "skipped" log was written to
    assert mock_log.call_count == 1
    log_path = mock_log.call_args[0][0]
    assert "skipped" in log_path