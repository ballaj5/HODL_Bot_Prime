#!/bin/bash

echo "🚀 Mounting LLaMA model directory..."
mkdir -p /models

MODEL_PATH="/models/llama-model.gguf"
MODEL_URL="https://huggingface.co/TheBloke/Llama-3-8B-Instruct-GGUF/resolve/main/llama-3-8b-instruct-q4_K_M.gguf"

if [ ! -f "$MODEL_PATH" ]; then
    echo "📥 Downloading LLaMA model..."
    wget -O "$MODEL_PATH" "$MODEL_URL"
    
    if [ $? -ne 0 ]; then
        echo "❌ Initial download failed. Retrying..."
        sleep 2
        wget -O "$MODEL_PATH" "$MODEL_URL"
    fi
fi

# Optional: Verify checksum (disabled by default)
# echo "✅ Verifying checksum..."
# echo "<EXPECTED_SHA256>  $MODEL_PATH" | sha256sum -c -

echo "✅ LLaMA model ready at $MODEL_PATH"
