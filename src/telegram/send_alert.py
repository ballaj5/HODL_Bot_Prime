# src/telegram/send_alert.py
import os
import json
import requests
import logging
from datetime import datetime
# Use relative import to find the sibling llm module
from ..llm.service import generate_commentary

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
ALERT_LOG = os.getenv("ALERT_LOG", "logs/alerts_log.jsonl")
SKIPPED_LOG = os.getenv("SKIPPED_LOG", "logs/skipped_llm_alerts.jsonl")

logging.basicConfig(level=logging.INFO)

def _send_telegram_message(text: str):
    """Sends a message to the configured Telegram chat."""
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        logging.error("❌ Telegram token or chat ID is not set.")
        return
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": text, "parse_mode": "Markdown"}
    try:
        response = requests.post(url, data=payload, timeout=10)
        response.raise_for_status()
        logging.info("✅ Telegram alert sent successfully.")
    except requests.RequestException as e:
        logging.error(f"❌ Failed to send Telegram message: {e}")

def _log_jsonl(filepath: str, data: dict):
    """Appends a JSON object to a JSONL file."""
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, "a") as f:
        f.write(json.dumps(data) + "\n")

def process_and_send_alert(context: dict):
    """Processes a signal, gets LLM commentary, and sends a Telegram alert."""
    confidence = context.get("confidence", 0)
    if confidence < 70:
        logging.info(f"Skipping alert for {context.get('symbol')}, confidence {confidence:.2f}% < 70%.")
        _log_jsonl(SKIPPED_LOG, context)
        return
    commentary = generate_commentary(context)
    alert_text = (
        f"📡 *LLM Signal Alert*\n\n"
        f"🪙 *Coin:* `{context.get('symbol')}`\n"
        f"🕒 *Timeframe:* `{context.get('timeframe')}`\n"
        f"📈 *Signal:* `{context.get('signal')}`\n"
        f"📊 *Confidence:* `{confidence:.2f}%`\n\n"
        f"*🧠 LLM Insight:*\n{commentary}"
    )
    _send_telegram_message(alert_text)
    context.update({"llm_commentary": commentary, "timestamp": datetime.utcnow().isoformat()})
    _log_jsonl(ALERT_LOG, context)

if __name__ == '__main__':
    sample_context = {
        "symbol": "BTC", "timeframe": "1h", "signal": "LONG", "confidence": 85.5,
        "volatility": 1.5, "ema": "above price", "macd": "bullish crossover", "rsi": 68.0
    }
    process_and_send_alert(sample_context)