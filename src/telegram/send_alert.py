# src/telegram/send_alert.py
import os
import requests
import logging
import sys
from src.utils.database import get_db_connection
from src.llm.service import generate_commentary # <-- ADDED THIS IMPORT

# --- Configuration ---
TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
API_URL = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
FUTURES_PREDICTION_COINS = ['BTC', 'ETH', 'SOL'] 
FUTURES_PREDICTION_TIMEFRAMES = ['10m', '30m', '1h', '1d']
FUTURES_PERPETUAL_TIMEFRAMES = ['5m', '15m', '30m']
ALERT_FLAG_PATH = "/workspace/data/alerts_on.flag"

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def _send_telegram_message(text: str):
    if not TOKEN or not CHAT_ID:
        logging.warning("Telegram token or chat ID not set. Skipping alert.")
        return
    payload = {'chat_id': CHAT_ID, 'text': text, 'parse_mode': 'Markdown'}
    try:
        response = requests.post(API_URL, data=payload)
        response.raise_for_status()
        logging.info("Successfully sent alert to Telegram.")
    except requests.exceptions.RequestException as e:
        logging.error(f"Failed to send Telegram message: {e}")

def _format_alert(context: dict, alert_type: str, signal: str) -> str:
    price = context.get("price_at_prediction")
    price_str = f"${float(price):,.4f}" if price is not None else "N/A"
    
    # --- ADDED LLM COMMENTARY ---
    llm_insight = context.get('llm_insight', 'Commentary not available.')
    # --- -------------------- ---

    return (
        f"🚨 *{alert_type.upper()} ALERT* 🚨\n\n"
        f"🪙 *Coin:* `{context.get('symbol')}/USDT`\n"
        f"⏳ *Timeframe:* `{context.get('timeframe')}`\n"
        f"💲 *Price at Alert:* `{price_str}`\n"
        f"📈 *Confidence:* `{float(context.get('confidence', 0)):.2f}%`\n"
        f"🎯 *RECOMMENDATION:* `{signal.upper()}`\n\n"
        f"🤖 *AI Rationale:* {llm_insight}"  # <-- ADDED THIS LINE
    )

def send_test_alert():
    logging.info("Sending a test alert...")
    test_context = {
        'symbol': 'BTC',
        'timeframe': '1h',
        'confidence': 99.99,
        'price_at_prediction': 65432.10
    }
    # For testing, we can generate a sample commentary
    test_context['llm_insight'] = generate_commentary(test_context)
    message = _format_alert(test_context, alert_type="Futures Prediction", signal="UP")
    _send_telegram_message(message)
    logging.info("Test alert sent.")

def process_and_send_alerts():
    if not os.path.exists(ALERT_FLAG_PATH):
        logging.info("Telegram alerts are disabled via the dashboard toggle. Skipping.")
        return

    conn = get_db_connection()
    if conn is None:
        return

    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM predictions WHERE sent_to_telegram = 0")
        unsent_predictions = cursor.fetchall()

        if unsent_predictions:
            logging.info(f"Found {len(unsent_predictions)} new predictions to process.")

        for prediction in unsent_predictions:
            prediction_dict = dict(prediction)
            
            for key, value in prediction_dict.items():
                if isinstance(value, bytes):
                    prediction_dict[key] = value.decode('utf-8', errors='replace')
            
            symbol = prediction_dict.get('symbol')
            timeframe = prediction_dict.get('timeframe')
            original_signal = prediction_dict.get('signal')

            alert_to_send = None
            
            if timeframe in FUTURES_PREDICTION_TIMEFRAMES and symbol in FUTURES_PREDICTION_COINS:
                alert_to_send = {"alert_type": "Futures Prediction", "signal": original_signal}
            elif timeframe in FUTURES_PERPETUAL_TIMEFRAMES:
                alert_to_send = {"alert_type": "Futures Perpetual", "signal": "Long" if original_signal == "UP" else "Short"}
            
            if alert_to_send:
                # --- ADDED LLM INTEGRATION ---
                # Generate commentary only for high-confidence signals to save resources
                if prediction_dict.get('confidence', 0) > 75:
                    prediction_dict['llm_insight'] = generate_commentary(prediction_dict)
                # --- ----------------------- ---

                alert_message = _format_alert(
                    context=prediction_dict,
                    alert_type=alert_to_send['alert_type'],
                    signal=alert_to_send['signal']
                )
                _send_telegram_message(alert_message)
            
            cursor.execute("UPDATE predictions SET sent_to_telegram = 1 WHERE id = %s", (prediction_dict['id'],))
        
        conn.commit()
    except Exception as e:
        logging.error(f"Alert processing job failed: {e}", exc_info=True)
    finally:
        if conn:
            conn.close()

if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'test':
        send_test_alert()
    else:
        process_and_send_alerts()