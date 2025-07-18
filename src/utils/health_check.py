import os
import json
from datetime import datetime
import requests

# Load configuration from environment
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
TELEGRAM_HEALTH_ALERTS = os.getenv("TELEGRAM_HEALTH_ALERTS", "false").strip().lower() == "true"

def run_health_check():
    # Prepare health status
    status = {
        "status": "ok",
        "timestamp": datetime.utcnow().isoformat()
    }

    # Ensure logs directory exists
    os.makedirs("logs", exist_ok=True)

    # Write status to logs/health.json
    with open("logs/health.json", "w") as f:
        json.dump(status, f)

    # Optionally send a Telegram message
    if TELEGRAM_HEALTH_ALERTS and TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID:
        try:
            resp = requests.post(
                f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage",
                data={
                    "chat_id": TELEGRAM_CHAT_ID,
                    "text": "✅ Bot health check passed"
                },
                timeout=5
            )
            resp.raise_for_status()
        except Exception as e:
            print(f"❌ Health check alert failed: {e}")

if __name__ == "__main__":
    run_health_check()
