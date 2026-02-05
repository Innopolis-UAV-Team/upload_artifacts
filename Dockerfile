FROM minio/mc:latest AS mc-binary

FROM alpine:latest

# Install required packages
RUN apk add --no-cache \
    bash \
    git \
    ca-certificates

# Copy MinIO client from official image (no download needed!)
COPY --from=mc-binary /usr/bin/mc /usr/local/bin/mc
RUN chmod +x /usr/local/bin/mc && \
    /usr/local/bin/mc --version

# Copy the entrypoint script
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Set the entrypoint
ENTRYPOINT ["/entrypoint.sh"]