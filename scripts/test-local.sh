#!/bin/bash
set -e

echo "🚀 Starting local test (GPU)..."

# Step 1: Prepare host models folder
mkdir -p models

# Step 2: Download LLaMA model if missing
MODEL_PATH="models/llama-model.gguf"
if [ ! -f "$MODEL_PATH" ]; then
  echo "📥 Downloading LLaMA model..."
  wget -O "$MODEL_PATH" \
    https://huggingface.co/TheBloke/Llama-3-8B-Instruct-GGUF/resolve/main/llama-3-8b-instruct-q4_K_M.gguf
else
  echo "✅ Model already exists: $MODEL_PATH"
fi

# Step 3: Build Docker image
echo "🐳 Building Docker image..."
docker build -t llama-crypto-bot .

# Step 4: Run container with GPU and models mounted
echo "▶️ Running container..."
docker run --rm \
  --gpus all \
  -v "$(pwd)/models:/models" \
  --env-file .env \
  llama-crypto-bot
