
import os
import sys

required_keys = [
    "TELEGRAM_BOT_TOKEN",
    "TELEGRAM_CHAT_ID",
    "OPENAI_API_KEY",
    "BYBIT_API_KEY",
    "BYBIT_API_SECRET",
]

missing = [key for key in required_keys if not os.getenv(key)]

if missing:
    print(f"❌ Missing required env variables: {', '.join(missing)}")
    sys.exit(1)

print("✅ All required environment variables are present.")

# Optional strict checks
boolean_keys = ["LLM_COMMENTARY", "TELEGRAM_HEALTH_ALERTS"]
for key in boolean_keys:
    val = os.getenv(key, "false").lower()
    if val not in ["true", "false"]:
        print(f"❌ Invalid boolean value for {key}: {val}")
        sys.exit(1)

try:
    interval = int(os.getenv("RETRAIN_INTERVAL_MINUTES", 30))
    if interval <= 0:
        raise ValueError
except ValueError:
    print("❌ RETRAIN_INTERVAL_MINUTES must be a positive integer.")
    sys.exit(1)
