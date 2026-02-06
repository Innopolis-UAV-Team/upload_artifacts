FROM python:3.11-slim

# Install git and other required packages
RUN apt-get update && apt-get install -y \
    git \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy the Python script
COPY minio_manager.py /app/

# Change to workspace and call minio_manager directly with environment variables
ENTRYPOINT ["sh", "-c", "\
    git config --global --add safe.directory /github/workspace 2>/dev/null || true; \
    git config --global --add safe.directory ${GITHUB_WORKSPACE} 2>/dev/null || true; \
    cd ${GITHUB_WORKSPACE:-/github/workspace} 2>/dev/null || true; \
    python3 /app/minio_manager.py \
        --mode ${INPUT_MODE:-upload} \
        --src_path \"${INPUT_SRC_PATH}\" \
        --tgt_path \"${INPUT_TGT_PATH:-.}\" \
        --bucket ${INPUT_BUCKET:-artifacts} \
        --use_git ${INPUT_USE_GIT:-True} \
        --minio_access_key ${INPUT_MINIO_ACCESS_KEY} \
        --minio_secret_key ${INPUT_MINIO_SECRET_KEY} \
        --minio_api_uri ${INPUT_MINIO_API_URI:-}"]
