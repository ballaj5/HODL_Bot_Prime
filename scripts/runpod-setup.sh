#!/bin/bash
set -e

# --- Install Dependencies ---
echo "--- Installing Python dependencies ---"
pip install -r /app/requirements.txt

# --- Create models directory before downloading ---
echo "--- Creating models directory ---"
mkdir -p /workspace/models

# --- Download LLM Model ---
echo "--- Downloading LLM model ---"
bash /app/scripts/download_llama_model.sh

echo "--- Setup complete ---"