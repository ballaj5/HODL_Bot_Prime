# src/telegram/send_alert.py
import os
import json
import requests
import logging
from datetime import datetime
# Use absolute imports from the src package
from src.llm.service import generate_commentary
from src.utils.db import load_all_signals

# --- Configuration ---
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
ALERT_LOG_PATH = "logs/alerts_log.jsonl"
SKIPPED_LOG_PATH = "logs/skipped_llm_alerts.jsonl"
CONFIDENCE_THRESHOLD = 70.0
PERPETUAL_TIMEFRAMES = ["10m", "30m", "1h", "1d"]

# --- Setup Logging ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# --- Helper Functions ---
def _send_telegram_message(text: str):
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        logging.error("❌ Telegram token or chat ID is not set.")
        return
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": text, "parse_mode": "Markdown"}
    try:
        response = requests.post(url, data=payload, timeout=10)
        response.raise_for_status()
        logging.info("✅ Telegram message sent.")
    except requests.RequestException as e:
        logging.error(f"❌ Failed to send Telegram message: {e}")

def _log_jsonl(filepath: str, data: dict):
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, "a") as f:
        f.write(json.dumps(data) + "\n")

def _calculate_leverage(volatility: float) -> str:
    if volatility > 5.0: return "5x (High Volatility)"
    elif volatility > 2.5: return "10x (Moderate Volatility)"
    else: return "20x (Low Volatility)"

def _get_hold_time(timeframe: str) -> str:
    if timeframe == "10m": return "30-60 minutes"
    elif timeframe == "30m": return "1-3 hours"
    elif timeframe == "1h": return "2-6 hours"
    elif timeframe == "1d": return "1-3 days"
    return "N/A"

# --- Alert Formatting ---
def _format_alert(context: dict) -> str:
    timeframe = context.get("timeframe", "")
    signal = context.get("signal", "UNKNOWN")
    volatility = context.get("volatility", 0.0)
    
    commentary = generate_commentary(context)
    context["llm_commentary"] = commentary
    _log_jsonl(ALERT_LOG_PATH, context)

    base_text = (
        f"🪙 *Coin:* `{context.get('symbol')}/USDT`\n"
        f"🕒 *Timeframe:* `{timeframe}`\n"
        f"📊 *Confidence:* `{context.get('confidence', 0):.2f}%`\n"
    )

    if timeframe in PERPETUAL_TIMEFRAMES:
        alert_title = "📈 *Futures Perpetual Alert*"
        signal_term = "Long" if signal == "UP" else "Short"
        leverage_rec = _calculate_leverage(volatility)
        hold_time_rec = _get_hold_time(timeframe)
        specific_text = (
            f"🧭 *Signal:* `{signal_term}`\n"
            f"🌪️ *Volatility:* `{volatility:.2f}%`\n\n"
            f"*🧠 LLM Insight:*\n{commentary}\n\n"
            f"⏳ *Hold Time:* Monitor for the next {hold_time_rec}.\n"
            f"⚖️ *Max Leverage:* `{leverage_rec}`"
        )
    else:
        alert_title = "🔮 *Futures Prediction Alert*"
        signal_term = "Up" if signal == "UP" else "Down"
        specific_text = (
            f"🧭 *Signal:* `{signal_term}`\n\n"
            f"*🧠 LLM Insight:*\n{commentary}"
        )
    return f"{alert_title}\n\n{base_text}{specific_text}"

# --- Main Logic ---
def process_signal(signal_context: dict):
    if signal_context.get('confidence', 0) >= CONFIDENCE_THRESHOLD:
        alert_text = _format_alert(signal_context)
        _send_telegram_message(alert_text)
    else:
        _log_jsonl(SKIPPED_LOG_PATH, signal_context)

def main():
    """Main entry point to fetch all signals and process them for alerting."""
    logging.info("--- Running Alert Generation ---")
    all_signals = load_all_signals()
    if not all_signals:
        logging.info("No signals found in the database to process.")
        return
    for signal_context in all_signals:
        process_signal(signal_context)
    logging.info("--- Alert Generation Complete ---")

if __name__ == '__main__':
    main()