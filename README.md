# Artifact Uploader to MinIO Storage

The repository provides a GitHub Action (Docker-based) for uploading artifacts to a MinIO storage system. The action automatically detects if it's running in a git repository and organizes files accordingly.

## Features

- **Smart Path Detection**: Automatically detects if running in a git repository
  - **In a Git Repo** (e.g., after using `actions/checkout`): Uploads to `./artifacts/repo_name/branch_name/commit_sha/<file>`
  - **Outside a Git Repo**: Uploads to `./artifacts/<file>`
- **Docker-based**: Runs in a containerized environment for consistency
- **MinIO Integration**: Seamless integration with MinIO storage

## Usage
1) (Optional) If you want structured paths, ensure you checkout the repository first:
    ```yaml
    steps:
      - uses: actions/checkout@v3
    ```
2) Add the uploading step to your workflow (usually at the end):
    ```yaml
    steps:
      - name: Upload artifacts
        uses: Innopolis-UAV-Team/upload_artifacts@v1
        with:
          path: <path_to_your_file_or_directory>
          MINIO_ACCESS_KEY: ${{ secrets.MINIO_ACCESS_KEY }}
          MINIO_SECRET_KEY: ${{ secrets.MINIO_SECRET_KEY }}
          MINIO_URL: <URL_of_your_MinIO_instance>
    ```
3) Replace `<path_to_your_file_or_directory>` with the path to your file or directory in the repository.
    > E.g., `./build/` or `./dist/app.zip`
4) Add the MinIO URL or use the default: `http://api.minio.uavlab.site/`
5) Get secrets for your repository from the team administrators. Add them to the secrets of your repository.

    Guide on how to add secrets: https://docs.github.com/en/actions/security-for-github-actions/security-guides/using-secrets-in-github-actions#creating-secrets-for-a-repository

    Secrets you need to add:
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
When not in a git repository, artifacts are stored with a timestamp:
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
