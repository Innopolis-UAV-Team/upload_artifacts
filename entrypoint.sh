#!/bin/bash
set -e
# Configure git safe directories
git config --global --add safe.directory /github/workspace 2>/dev/null || true
git config --global --add safe.directory "${GITHUB_WORKSPACE}" 2>/dev/null || true

# Change to workspace
cd "${GITHUB_WORKSPACE:-/github/workspace}" 2>/dev/null || true

# Put downloaded files in a temporary directory to avoid permission issues

if [ "${INPUT_MODE}" == "download" ]; then
    TMP_DIR="/tmp/download"
    mkdir -p "${TMP_DIR}"
    TGT_PATH="${TMP_DIR}/${INPUT_TGT_PATH}"
else
    TGT_PATH="${INPUT_TGT_PATH}"
fi

# Run the Python script
python3 /app/minio_manager.py \
    --mode "${INPUT_MODE}" \
    --src_path "${INPUT_SRC_PATH}" \
    --tgt_path "${TGT_PATH}" \
    --bucket "${INPUT_BUCKET}" \
    --use_git "${INPUT_USE_GIT}" \
    --minio_access_key "${INPUT_MINIO_ACCESS_KEY}" \
    --minio_secret_key "${INPUT_MINIO_SECRET_KEY}" \
    --minio_api_uri "${INPUT_MINIO_API_URI}"

# Adjust permissions of the downloaded files and move them to the target path
if [ "${INPUT_MODE}" == "download" ]; then
  mkdir -p "${INPUT_TGT_PATH}"
  chown -R "${INPUT_UID}":"${INPUT_GID}" "${INPUT_TGT_PATH}"
  chown -R "${INPUT_UID}":"${INPUT_GID}" "${TMP_DIR}"
  cp -r "${TMP_DIR}"/* "${INPUT_SRC_PATH}"
fi

exit $?
