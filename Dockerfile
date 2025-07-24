# --- Stage 1: Builder ---
FROM nvidia/cuda:12.1.1-runtime-ubuntu22.04 AS builder

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV DEBIAN_FRONTEND=noninteractive

# Install build-time system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    build-essential \
    python3-dev \
    python3-pip \
    python3.10-venv \
    ninja-build \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Create and activate a virtual environment
RUN python3 -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Install Python dependencies
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt


# --- Stage 2: Final Image ---
FROM nvidia/cuda:12.1.1-runtime-ubuntu22.04

# Set environment variables for the final image
ENV LLAMA_MODEL_PATH=/workspace/models/llama-model.gguf
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PATH="/opt/venv/bin:$PATH"
ENV DEBIAN_FRONTEND=noninteractive

# Install only necessary runtime system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    wget \
    libgomp1 \
    python-is-python3 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy the virtual environment and application code
COPY --from=builder /opt/venv /opt/venv
## FIX: Corrected the redundant 'COPY . .' to a single, correct command.
COPY . .

# Make the start script executable
RUN chmod +x ./scripts/start.sh

# Expose any necessary ports (e.g., Streamlit and JupyterLab)
EXPOSE 8888
EXPOSE 8050

# Set the default command to run the application using the start script
CMD ["./scripts/start.sh"]