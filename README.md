# Artifact Uploader to MinIO Storage

The repository provides a GitHub Action (Docker-based) for uploading artifacts to a MinIO storage system. The action automatically detects if it's running in a git repository and organizes files accordingly.

## Features

- **Smart Path Detection**: Automatically detects if running in a git repository
  - **In a Git Repo** (e.g., after using `actions/checkout`): Uploads to `./<bucket>/repo_name/branch_name/commit_sha/<file>`
  - **Outside a Git Repo**: Uploads to `./<bucket>/<file>`
- **Docker-based**: Runs in a containerized environment for consistency
- **MinIO Integration**: Seamless integration with MinIO storage

## Usage

### Basic Upload

```yaml
steps:
  - uses: actions/checkout@v3
  
  - name: Upload artifacts
    uses: Innopolis-UAV-Team/upload_artifacts@v1
    with:
      path: ./build/
      minio_access_key: ${{ secrets.MINIO_ACCESS_KEY }}
      minio_secret_key: ${{ secrets.MINIO_SECRET_KEY }}
      minio_api_uri: http://api.minio.uavlab.site/
```

### Advanced Configuration

All available options:

```yaml
steps:
  - uses: actions/checkout@v3
  
  - name: Upload artifacts with custom settings
    uses: Innopolis-UAV-Team/upload_artifacts@v1
    with:
      path: ./build/                    # Required: Path to upload/download
      target_path: ./my-artifacts/      # Optional: Target path (default: './')
      bucket: my-bucket                 # Optional: Bucket name (default: 'artifacts')
      mode: upload                      # Optional: 'upload' or 'download' (default: 'upload')
      use_git: true                     # Optional: Use git info for paths (default: 'true')
      minio_access_key: ${{ secrets.MINIO_ACCESS_KEY }}
      minio_secret_key: ${{ secrets.MINIO_SECRET_KEY }}
      minio_api_uri: http://api.minio.uavlab.site/
```

### Download Artifacts

```yaml
steps:
  - name: Download artifacts
    uses: Innopolis-UAV-Team/upload_artifacts@v1
    with:
      path: ./my-artifacts/             # Source path in MinIO
      target_path: ./downloads/         # Where to save locally
      mode: download                    # Switch to download mode
      bucket: artifacts
      use_git: true
      minio_access_key: ${{ secrets.MINIO_ACCESS_KEY }}
      minio_secret_key: ${{ secrets.MINIO_SECRET_KEY }}
      minio_api_uri: http://api.minio.uavlab.site/
```

## Configuration Options

| Input | Description | Required | Default |
|-------|-------------|----------|---------|
| `path` | Path to file/directory to upload or download | ✅ Yes | - |
| `target_path` | Target path in MinIO (upload) or local (download) | No | `./` |
| `bucket` | MinIO bucket name | No | `artifacts` |
| `mode` | Operation mode: `upload` or `download` | No | `upload` |
| `use_git` | Use git repository info for path generation | No | `true` |
| `MINIO_ACCESS_KEY` | MinIO access key | ✅ Yes | - |
| `MINIO_SECRET_KEY` | MinIO secret key | ✅ Yes | - |
| `MINIO_URL` | MinIO server URL | ✅ Yes | `http://api.minio.uavlab.site/` |

### Setup Secrets

Get secrets from your team administrators and add them to your repository:

Required secrets:
1) `MINIO_ACCESS_KEY`
2) `MINIO_SECRET_KEY`

## Path Structure

### With Git Repository (after checkout)
When running in a git repository, artifacts are organized hierarchically:
```
artifacts/
└── repository-name/
    └── branch-name/
        └── SHA-abcd123/
            └── your-files
```

### Without Git Repository
When not in a git repository, artifacts are stored like that:
```
artifacts/
└── uploads/
    └── your-files
```

## Where to find artifacts

1) Go to the desired action.  
    You can do it right from the commit page or your repository's `Actions` tab.

2) Open the job that ran the upload step.
3) Find the `Upload artifacts` step in the logs.
4) You will find the links to your artifacts there.

    Example output:
    ```
    ✅ Artifact has been uploaded successfully!
    ==========================================
    📁 File location:
       http://minio.uavlab.site/browser/artifacts/my-repo/main/SHA-abc1234/
    ==========================================
    ```
5) Login with the appropriate account credentials when accessing the MinIO browser.
