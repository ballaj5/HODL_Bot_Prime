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
  # This function now takes a module path like "src.data_fetch.fetch_futures_data"
  local module_path="$1"
  local name="$2"
  for i in $(seq 1 3); do
    echo "$(timestamp) 🔁 Attempt $i for $name..."
    # Use python -m to run the module, which fixes the import errors
    python3 -m "$module_path" && report_health "$name" "Success" && return 0
    sleep 2
  done
  report_health "$name" "Fail"
  return 1
}

# Run pipeline steps using their module paths
run_with_retry "src.data_fetch.fetch_futures_data" "Fetch Data"
run_with_retry "src.models.train_predictor"      "Train Model"
run_with_retry "src.models.predict"              "Run Predictions"
run_with_retry "src.telegram.send_alert"         "Telegram Alerts"

# Run the dashboard as a module as well
if [ -f "src/dashboard/app.py" ]; then
    echo "$(timestamp) 🚀 Launching Dash dashboard..."
    python3 -m src.dashboard.app &
    report_health "Dashboard" "Started"
fi

echo "$(timestamp) ✅ All services launched. Container will remain active."
tail -f /dev/null