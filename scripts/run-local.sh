#!/bin/bash
set -e

echo "🟡 Loading environment variables from .env file..."
if [ -f .env ]; then
  export $(grep -v '^#' .env | xargs)
else
  echo "⚠️ .env file not found. Please create one."
  exit 1
fi
echo "✅ Environment loaded."

# Ensure models folder exists & download LLaMA model if missing
mkdir -p models
MODEL_PATH="models/llama-model.gguf"
if [ ! -f "$MODEL_PATH" ]; then
  echo "📥 LLaMA model not found. Downloading..."
  wget -O "$MODEL_PATH" \
    "https://huggingface.co/TheBloke/Llama-3-8B-Instruct-GGUF/resolve/main/llama-3-8b-instruct-q4_K_M.gguf"
else
  echo "✅ Model already exists at: $MODEL_PATH"
fi

# Set trap to gracefully shut down on Ctrl+C
trap "echo '🔴 Shutting down services.'; kill 0" SIGINT

# Launch the dashboard in the background
if [ -f dashboard/app.py ]; then
  echo "🚀 Launching dashboard in the background..."
  python3 dashboard/app.py &
fi

# Run the main pipeline script
# You can add a loop here if you want it to run periodically
# e.g., while true; do ./scripts/run_pipeline.sh; sleep 3600; done
echo "▶️ Starting the main data pipeline..."
./scripts/run_pipeline.sh

echo "✅ Local run finished. The dashboard may still be running in the background."
wait