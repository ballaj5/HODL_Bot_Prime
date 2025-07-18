#!/bin/bash
set -e

echo "📦 [RUNPOD SETUP] Starting Crypto Bot Environment Setup..."

# Change into the app directory
cd /app || {
  echo "❌ /app directory not found!"
  exit 1
}

# Generate .env from template if missing
if [ ! -f .env ]; then
  echo "🔐 Creating default .env file from template..."
  cat <<EOF > .env
TELEGRAM_BOT_TOKEN=\${TELEGRAM_BOT_TOKEN}
TELEGRAM_CHAT_ID=\${TELEGRAM_CHAT_ID}
LLM_COMMENTARY=true
TELEGRAM_HEALTH_ALERTS=true
ENV=production
EOF
else
  echo "✅ Found existing .env file"
fi

# Cleanup old container
echo "🧼 Removing old 'predictor' container if it exists..."
docker rm -f predictor 2>/dev/null || true

# Build the Docker image
echo "🐳 Building Docker image (this may take a few mins)..."
docker build -t crypto-predictor-bot .

# Ensure logs & models mounts exist on host
mkdir -p "$(pwd)/data" "$(pwd)/models" "$(pwd)/logs"

# Run container (CPU-only mode)
echo "🚀 Running Docker container in CPU mode..."
docker run -d --name predictor \
  --env-file .env \
  -p 8050:8050 \
  -v "$(pwd)/data:/app/data" \
  -v "$(pwd)/models:/models" \
  -v "$(pwd)/logs:/app/logs" \
  crypto-predictor-bot

# GPU variant hint
echo ""
echo "👉 To run with GPU, stop the above and run:"
echo "docker run -d --name predictor --gpus all --env-file .env -p 8050:8050 -v \"$(pwd)/data:/app/data\" -v \"$(pwd)/models:/models\" -v \"$(pwd)/logs:/app/logs\" crypto-predictor-bot"

echo "✅ Crypto Bot is running! Dashboard: http://localhost:8050"
