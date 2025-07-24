#!/bin/bash
set -e

# --- Initial Setup ---
echo "🚀 HODLBot starting up..."

# Load environment variables from .env file if it exists
if [ -f .env ]; then
  echo "🔐 Loading environment variables from .env file..."
  export $(grep -v '^#' .env | xargs)
fi

# Ensure all necessary data directories exist
mkdir -p /workspace/data/history
mkdir -p /workspace/data/finetuning
mkdir -p /workspace/models_data
mkdir -p /workspace/logs

# Initialize the PostgreSQL database (creates the 'predictions' table if not present)
echo "🔍 Initializing database..."
python3 -m src.utils.database init_db

# --- Run the initial data pipeline ONCE ---
# This fetches historical data, trains models, and makes initial predictions
# to populate the database before the live services start.
echo "📊 Running initial data and training pipeline..."
./scripts/run_pipeline.sh

# --- Launch Long-Running Services in the Background ---

# 1. Launch the Streamlit Dashboard
echo "🚀 Launching Streamlit Dashboard on port 8050..."
streamlit run src/dashboard/app.py --server.port 8050 --server.address 0.0.0.0 &

# 2. Launch the Scheduler (for retraining models and sending alerts)
echo "⏰ Launching the APScheduler..."
python3 -m src.scheduler.retrain_scheduler &

# 3. Launch the Real-time Feature Manager
echo "📡 Launching the Real-time Feature Manager..."
python3 -m src.data_fetch.realtime_manager &

echo "✅ All services are running. Tailing logs... (Press Ctrl+C to stop)"
# The 'wait' command keeps the script alive, so the Docker container doesn't exit.
# It will exit if any of the background processes fail.
wait