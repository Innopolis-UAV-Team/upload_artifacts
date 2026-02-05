#!/bin/bash

set -e

path=$1
MINIO_ACCESS_KEY=$2
MINIO_SECRET_KEY=$3
MINIO_URL=$4

# Change to GitHub workspace if it exists (for Docker actions)
if [ -n "$GITHUB_WORKSPACE" ] && [ -d "$GITHUB_WORKSPACE" ]; then
    echo "Detected GitHub Actions environment"
    cd "$GITHUB_WORKSPACE"
    echo "Working directory: $(pwd)"
    echo "Contents: $(ls -la | head -10)"
fi

echo "Debug info:"
echo "  GITHUB_REPOSITORY: ${GITHUB_REPOSITORY:-<not set>}"
echo "  GITHUB_SHA: ${GITHUB_SHA:-<not set>}"
echo "  GITHUB_REF_NAME: ${GITHUB_REF_NAME:-<not set>}"
echo "  GITHUB_REF: ${GITHUB_REF:-<not set>}"
echo "  .git exists: $([ -d .git ] && echo 'yes' || echo 'no')"
echo ""

# Check if we're in a git repository OR if GitHub Actions context is available
if git rev-parse --is-inside-work-tree > /dev/null 2>&1 || [ -n "$GITHUB_REPOSITORY" ]; then
    echo "Git repository detected. Uploading to structured path..."

    # Get commit SHA (8 character short version)
    if [ -n "$GITHUB_SHA" ]; then
        # Use GitHub Actions context if available (always present in GHA)
        commit_sha=$(echo "$GITHUB_SHA" | cut -c1-8)
    else
        # Use git command as fallback
        commit_sha=$(git rev-parse --short=8 HEAD 2>/dev/null || echo "unknown")
    fi

    # Get branch name with fallback for detached HEAD
    if [ -n "$GITHUB_HEAD_REF" ]; then
        # For pull requests, use the source branch
        branch_name=$(echo "$GITHUB_HEAD_REF" | tr '[:upper:]' '[:lower:]' | tr '/' '-')
    elif [ -n "$GITHUB_REF_NAME" ]; then
        # GitHub Actions provides this as a cleaner alternative (e.g., "main" instead of "refs/heads/main")
        branch_name=$(echo "$GITHUB_REF_NAME" | tr '[:upper:]' '[:lower:]' | tr '/' '-')
    elif branch_name=$(git symbolic-ref --short HEAD 2>/dev/null); then
        # We're on a branch (local git)
        branch_name=$(echo "$branch_name" | tr '[:upper:]' '[:lower:]' | tr '/' '-')
    elif [ -n "$GITHUB_REF" ]; then
        # Fallback: Extract branch from refs/heads/branch-name or refs/pull/123/merge
        branch_name=$(echo "$GITHUB_REF" | sed 's|refs/heads/||; s|refs/pull/||; s|/merge||' | tr '[:upper:]' '[:lower:]' | tr '/' '-')
    else
        # Final fallback to commit SHA
        branch_name="detached-${commit_sha}"
    fi

    # Get repository name with multiple fallback strategies
    if [ -n "$GITHUB_REPOSITORY" ]; then
        # Use GitHub Actions context (format: owner/repo) - most reliable in CI
        repo_name=$(basename "$GITHUB_REPOSITORY" | tr '[:upper:]' '[:lower:]')
    elif remote_url=$(git config --get remote.origin.url 2>/dev/null); then
        # Extract repo name from URL (works with HTTPS and SSH)
        # Remove .git suffix and extract basename
        repo_name=$(echo "$remote_url" | sed 's/\.git$//' | awk -F'/' '{print $NF}' | tr '[:upper:]' '[:lower:]')
    else
        # Fallback to directory name
        repo_name=$(basename "$(git rev-parse --show-toplevel 2>/dev/null || pwd)" | tr '[:upper:]' '[:lower:]')
    fi

    # Create bucket path with git information
    commit_bucket_name="SHA-${commit_sha}"

    # Set upload path
    upload_path="artifacts/${repo_name}/${branch_name}/${commit_bucket_name}"

    echo "Repository: ${repo_name}"
    echo "Branch: ${branch_name}"
    echo "Commit: ${commit_sha}"
else
    echo "Not a git repository. Uploading to simple path..."

    upload_path="artifacts/uploads"
fi

echo "Upload path: ${upload_path}"
echo ""

# Resolve the file path (handle relative paths in GitHub workspace)
if [ -n "$GITHUB_WORKSPACE" ] && [ ! -f "$path" ] && [ ! -d "$path" ]; then
    # Try relative to workspace
    resolved_path="${GITHUB_WORKSPACE}/${path}"
    if [ -e "$resolved_path" ]; then
        path="$resolved_path"
        echo "Resolved path to: ${path}"
    fi
fi

# Configure MinIO client
mc alias set myminio $MINIO_URL $MINIO_ACCESS_KEY $MINIO_SECRET_KEY

# Create bucket if it doesn't exist
mc mb -p myminio/${upload_path} 2>/dev/null || true

# Upload the file(s)
echo "Uploading ${path}..."
if [ ! -e "$path" ]; then
    echo "❌ Error: Path does not exist: ${path}"
    exit 1
fi
mc cp -r $path myminio/${upload_path}/

echo ""
echo "✅ Artifact has been uploaded successfully!"
echo "=========================================="
echo "📁 File location:"
echo "   <your minio (not api) uri>/browser/${upload_path}/"
echo "=========================================="
echo ""
echo "ℹ️  If you have any problems accessing your artifacts, please contact the team."
