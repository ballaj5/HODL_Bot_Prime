#!/bin/bash

timestamp() {
  date '+%Y-%m-%d %H:%M:%S'
}

echo "$(timestamp) 🔁 Starting Crypto Bot..."
mkdir -p /app/logs

report_health() {
  local service="$1"
  local status="$2"
  echo "$(timestamp) [$status] $service" >> /app/logs/health_log.txt
}

run_with_retry() {
  local module_path="$1"
  local name="$2"
  for i in $(seq 1 3); do
    echo "$(timestamp) 🔁 Attempt $i for $name..."
    # Use python -m to run the module, which fixes all import errors
    python3 -m "$module_path" && report_health "$name" "Success" && return 0
    sleep 2
  done
  report_health "$name" "Fail"
  return 1
}

# Run pipeline steps using their full module paths
run_with_retry "src.data_fetch.fetch_futures_data" "Fetch Data"
run_with_retry "src.models.train_predictor"      "Train Model"
run_with_retry "src.models.predict"              "Run Predictions"

# The alert script now reads from the DB, so we run it once without retry
echo "$(timestamp) 📣 Generating and sending alerts..."
python3 -m src.telegram.send_alert

# Run the dashboard as a module in the background
if [ -f "src/dashboard/app.py" ]; then
    echo "$(timestamp) 🚀 Launching Dash dashboard..."
    python3 -m src.dashboard.app &
    report_health "Dashboard" "Started"
fi

echo "$(timestamp) ✅ All services launched. Container will remain active."
tail -f /dev/null