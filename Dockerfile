FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    HF_HOME=/app/.cache/huggingface

RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 \
    python3-pip \
    python3-dev \
    ffmpeg \
    libsndfile1 \
    git \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install PyTorch with CUDA 12.8 support first (cached layer)
RUN python3 -m pip install --no-cache-dir \
    "torch==2.8.0+cu128" \
    "torchaudio==2.8.0+cu128" \
    --extra-index-url https://download.pytorch.org/whl/cu128

# Copy project files and install remaining dependencies
COPY pyproject.toml README.md ./
COPY omnivoice/ omnivoice/
RUN python3 -m pip install --no-cache-dir -e .

EXPOSE 8001

CMD ["python3", "-m", "omnivoice.api"]
