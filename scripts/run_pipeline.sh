#!/bin/bash
set -e

# Load env from the root directory
if [ -f .env ]; then
  export $(grep -v '^#' .env | xargs)
fi

# Ensure logs folder exists at the root
mkdir -p logs

echo "🔄 Starting prediction pipeline: $(date)" | tee -a logs/pipeline.log

# Run python modules using python -m for correct pathing
python3 -m src.data_fetch.fetch_futures_data 2>&1 | tee -a logs/pipeline.log
python3 -m src.models.train_predictor      2>&1 | tee -a logs/pipeline.log
python3 -m src.models.predict              2>&1 | tee -a logs/pipeline.log

if [ "$LLM_COMMENTARY" = "true" ]; then
    # Assuming generate_summary is now part of the telegram alert step
    echo "LLM commentary will be generated during the alert phase."
fi

echo "✅ Pipeline complete: $(date)" | tee -a logs/pipeline.log