FROM minio/mc:latest AS mc-binary

FROM python:3.11-slim

# Install git and other required packages
RUN apt-get update && apt-get install -y \
    git \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Copy MinIO Client (mc) from official image
COPY --from=mc-binary /usr/bin/mc /usr/local/bin/mc
RUN chmod +x /usr/local/bin/mc && mc --version

# Set working directory
WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy the Python script and entrypoint
COPY minio_manager.py /app/
COPY entrypoint.sh /app/
RUN chmod +x /app/entrypoint.sh

# Use the entrypoint script
ENTRYPOINT ["/app/entrypoint.sh"]
