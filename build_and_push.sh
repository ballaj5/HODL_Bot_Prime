#!/bin/bash
set -e

# --- Configuration ---
# IMPORTANT: Replace these with your Docker Hub username and the desired image name.
DOCKER_HUB_USERNAME="ballaj5"
IMAGE_NAME="hodlbot"

# --- Versioning ---
# Generates a unique version tag based on the current timestamp.
VERSION_TAG=$(date +%Y%m%d-%H%M%S)
echo "--------------------------------------------------"
echo "🚀 Starting Docker build and push process..."
echo "--------------------------------------------------"
echo "Image: ${DOCKER_HUB_USERNAME}/${IMAGE_NAME}"
echo "Tags: latest, ${VERSION_TAG}"
echo "--------------------------------------------------"

# --- 1. Docker Login ---
# Prompts for your Docker Hub credentials.
echo "🔐 Please log in to Docker Hub..."
docker login -u "$DOCKER_HUB_USERNAME"

# --- 2. Build the Docker Image ---
# Builds the image from the Dockerfile in the current directory.
echo "🛠️ Building Docker image..."
docker build -t "${DOCKER_HUB_USERNAME}/${IMAGE_NAME}:${VERSION_TAG}" -t "${DOCKER_HUB_USERNAME}/${IMAGE_NAME}:latest" .

# --- 3. Push the Docker Image ---
# Pushes both the 'latest' and the version-specific tag to Docker Hub.
echo "⬆️ Pushing image to Docker Hub..."
docker push "${DOCKER_HUB_USERNAME}/${IMAGE_NAME}:${VERSION_TAG}"
docker push "${DOCKER_HUB_USERNAME}/${IMAGE_NAME}:latest"

echo "--------------------------------------------------"
echo "✅ Success! Image has been built and pushed."
echo "--------------------------------------------------"
