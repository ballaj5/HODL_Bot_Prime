# llm/llm_test.py
import os
from llm.service import generate_commentary

# Sample context for testing
sample_context = {
    "symbol": "BTC",
    "timeframe": "15m",
    "signal": "LONG",
    "confidence": 78.2,
    "volatility": 2.3,
    "ema": "above price",
    "macd": "bullish crossover",
    "rsi": 63.4
}

# Ensure the backend is set for the test if not already in the environment
backend = os.getenv("LLM_BACKEND", "llama")
print(f"🧪 Testing LLM backend: {backend.upper()}")

# Generate commentary using the unified service
commentary = generate_commentary(sample_context)

print("\n--- Generated Commentary ---")
print(commentary)
print("--------------------------")