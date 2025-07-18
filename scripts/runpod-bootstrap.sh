#!/bin/bash
set -e

cd /app

# Export environment variables from .env file
if [ -f .env ]; then
  echo "🔐 Loading environment variables from .env file..."
  export $(grep -v '^#' .env | xargs)
fi

# Create a unified logs folder for health checks and pipeline output
mkdir -p logs
echo '{"status":"starting","timestamp":"'$(date -u +"%Y-%m-%dT%H:%M:%SZ")'"}' > logs/health.json

# Download the LLaMA model required for the bot
# This assumes you have a script to handle the download logic
if [ -f runpod/download_llama_model.sh ] && [ -x runpod/download_llama_model.sh ]; then
  echo "📥 Downloading LLaMA model..."
  bash runpod/download_llama_model.sh
else
  echo "⚠️ Warning: Model download script 'runpod/download_llama_model.sh' not found or not executable."
fi

# Install Python dependencies from the primary requirements file
if [ -f requirements.txt ]; then
  echo "🐍 Installing Python dependencies from requirements.txt..."
  pip install --no-cache-dir -r requirements.txt
else
  echo "❌ Error: requirements.txt not found. Cannot install dependencies."
  exit 1
fi

echo "✅ Setup complete. Launching application..."
# Launch the main application using the start script
bash start.sh