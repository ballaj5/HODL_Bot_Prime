#!/bin/bash

# Name(s) of containers you want to KEEP (space-separated if more than one)
KEEP_CONTAINERS=("crypto-predictor-bot")

echo "🧹 Cleaning up Docker containers..."

# Get all container IDs and names
docker ps -a --format "{{.ID}} {{.Names}}" | while read -r line; do
  ID=$(echo "$line" | awk '{print $1}')
  NAME=$(echo "$line" | awk '{print $2}')

  # Check if the container name is in KEEP_CONTAINERS
  if [[ ! " ${KEEP_CONTAINERS[@]} " =~ " ${NAME} " ]]; then
    echo "❌ Removing container: $NAME ($ID)"
    docker stop "$ID" > /dev/null 2>&1
    docker rm "$ID" > /dev/null 2>&1
  else
    echo "✅ Keeping container: $NAME"
  fi
done

echo "✅ Cleanup complete."
