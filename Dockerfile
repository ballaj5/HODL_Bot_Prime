# Use a specific CUDA base image for reproducibility
FROM nvidia/cuda:12.1.1-runtime-ubuntu22.04

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV DEBIAN_FRONTEND=noninteractive
ENV LLAMA_MODEL_PATH=/models/llama-model.gguf

# Install system dependencies, including the ninja build tool
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    curl \
    wget \
    build-essential \
    python3-dev \
    python3-pip \
    python-is-python3 \
    ninja-build \
    && rm -rf /var/lib/apt/lists/*

# Set up the application directory
WORKDIR /app

# Copy only the requirements file first to leverage Docker layer caching
COPY requirements.txt .

# Install all Python dependencies from the single requirements file
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Make the start script executable
RUN chmod +x ./scripts/start.sh

# Set the start script as the container's final command
CMD ["./scripts/start.sh"]