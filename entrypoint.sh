#!/bin/bash

path=$1
MINIO_ACCESS_KEY=$2
MINIO_SECRET_KEY=$3

# Ensure the script is executable
repo_name=$(basename $(git remote get-url origin) .git | tr '[:upper:]' '[:lower:]')
branch_name=$(git rev-parse --abbrev-ref HEAD | tr '[:upper:]' '[:lower:]')
commit_sha=$(git rev-parse --short HEAD | tr '[:upper:]' '[:lower:]')

current_time=$(git show -s --date=format:"%Y.%m.%d-%H:%M" --format=%cd)
commit_backet_name="${current_time}...SHA-${commit_sha}"

# Using lftp to upload files
~/mc alias set myminio http://localhost:9000 $MINIO_ACCESS_KEY $MINIO_SECRET_KEY
~/mc mb myminio/artifacts/$repo_name/$branch_name/$commit_backet_name
~/mc cp $path myminio/artifacts/$repo_name/$branch_name/$commit_backet_name/

echo ""
echo ""
echo "Artifact has been uploaded successfuly. You can find your file at:"
echo "----------FILE LOCATION----------"
echo "VPN (Netherlands):     http://10.8.0.19:9001/browser/artifacts/${repo_name}%2F${branch_name}%2F${commit_backet_name}%2F"
echo "WIFI (might change):   http://10.95.0.140:9001/browser/artifacts/${repo_name}%2F${branch_name}%2F${commit_backet_name}%2F"
echo "---------------------------------"
echo "If you have any problems with getting your artifacts, please contact @jpeg_not_ded or @AsiiaBara (if someone is still working here)."