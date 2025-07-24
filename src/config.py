import os
import sys

# --- Read backend choice first ---
LLM_BACKEND = os.getenv("LLM_BACKEND", "llama").lower()

# --- Define required keys based on backend ---
required_keys = [
    "TELEGRAM_BOT_TOKEN",
    "TELEGRAM_CHAT_ID",
    "BYBIT_API_KEY",
    "BYBIT_API_SECRET",
]

if LLM_BACKEND == "openai":
    required_keys.append("OPENAI_API_KEY")

# --- Validate presence ---
missing = [key for key in required_keys if not os.getenv(key)]

if missing:
    print(f"❌ Missing required env variables for '{LLM_BACKEND}' backend: {', '.join(missing)}")
    sys.exit(1)

print(f"✅ All required environment variables for '{LLM_BACKEND}' backend are present.")

# --- Optional strict type checks ---
try:
    interval = int(os.getenv("RETRAIN_INTERVAL_MINUTES", "30"))
    if interval <= 0:
        raise ValueError("Interval must be positive")
except (ValueError, TypeError):
    print("❌ Invalid value for RETRAIN_INTERVAL_MINUTES. Must be a positive integer.")
    sys.exit(1)

print("✅ All environment variables passed validation.")