import argparse
import os
import sys
from pathlib import Path
from urllib.parse import urlparse

from git import Repo, InvalidGitRepositoryError
from minio import Minio
from minio.error import S3Error


def generate_git_path(use_git: bool, target_path: Path) -> Path:
    if use_git:
        if 'GITHUB_WORKSPACE' in os.environ:
            os.chdir(os.environ['GITHUB_WORKSPACE'])
        try:
            repo = Repo(Path('./'))
            print(f"Git repository detected: "
                  f"{repo.active_branch.name} ({repo.head.commit.hexsha[:7]}")
            tgt_path_trunk = (
                    Path(repo.working_tree_dir).stem /
                    Path(repo.active_branch.name) /
                    Path(f"SHA-{repo.head.commit.hexsha[:7]}") /
                    target_path
            )
        except InvalidGitRepositoryError:
            print("No git repository found. Proceeding without git info.")
            tgt_path_trunk = target_path
    else:
        print("Git info usage disabled. Proceeding without git info.")
        tgt_path_trunk = target_path

    return tgt_path_trunk


def strip_scheme(url: str) -> str:
    schemaless = urlparse(url)._replace(scheme='').geturl()
    return schemaless[2:] if schemaless.startswith("//") else schemaless

def upload_to_minio(args: argparse.Namespace) -> None:
    """Handle upload operation."""
    print("\n🚀 Starting upload operation...")

    client = Minio(
        strip_scheme(args.minio_api_uri),
        access_key=args.minio_access_key,
        secret_key=args.minio_secret_key,
        secure=args.minio_api_uri.startswith("https://")
    )

    if not args.src_path.exists():
        print(f"Source path does not exist: {args.src_path}")
        sys.exit(1)

    found = client.bucket_exists(bucket_name=args.bucket)
    if not found:
        client.make_bucket(bucket_name=args.bucket)
        print(f"Created new bucket: {args.bucket}")
    else:
        print(f"Using existing bucket: {args.bucket}")

    tgt_path_trunk = generate_git_path(args.use_git, args.tgt_path)
    src_path = args.src_path

    if not src_path.exists():
        print(f"Source path does not exist: {src_path}")
        sys.exit(1)

    if src_path.is_file():
        # Upload single file
        client.fput_object(args.bucket, src_path.name, str(src_path))
        print(f"Uploaded: {src_path} -> {src_path.name}")
    else:
        # Upload directory recursively
        files_uploaded = 0
        for file_path in src_path.rglob('*'):
            if not file_path.is_file():
                continue
            # Preserve directory structure relative to src_path
            dest = tgt_path_trunk / src_path / file_path.relative_to(src_path)
            try:
                client.fput_object(args.bucket, dest.as_posix(), str(file_path))
                print(f"Uploaded: {file_path} -> {dest}")
                files_uploaded += 1
            except S3Error as e:
                print(f"Failed to upload {file_path}: {e}")

        print(f"Total files uploaded: {files_uploaded}")
        print("Upload operation completed!")

def download_from_minio(args: argparse.Namespace) -> None:
    """Handle download operation."""
    print("\n⬇️  Starting download operation...")

    client = Minio(
        strip_scheme(args.minio_api_uri),
        access_key=args.minio_access_key,
        secret_key=args.minio_secret_key,
        secure=args.minio_api_uri.startswith("https://")
    )

    # Check if bucket exists
    found = client.bucket_exists(bucket_name=args.bucket)
    if not found:
        print(f"Bucket does not exist: {args.bucket}")
        sys.exit(1)
    else:
        print(f"Using bucket: {args.bucket}")

    # Generate source path in MinIO (with git info if enabled)
    # We need to separate the git trunk from the actual source path
    git_trunk_without_src = generate_git_path(args.use_git, Path('.'))

    # Ensure target directory exists
    tgt_path = args.tgt_path
    tgt_path.mkdir(parents=True, exist_ok=True)

    try:
        # List objects with the given prefix
        objects = client.list_objects(
            args.bucket,
            prefix=git_trunk_without_src.as_posix(),
            recursive=True
        )

        files_downloaded = 0
        for obj in objects:
            # Get the object name
            object_name = obj.object_name
            # Strip only the git trunk (repo/branch/SHA), keep the source path
            relative_path = Path(object_name).relative_to(git_trunk_without_src)

            # Determine local file path
            local_file_path = tgt_path / relative_path
            local_file_path.parent.mkdir(parents=True, exist_ok=True)

            # Download the file
            try:
                client.fget_object(args.bucket, object_name, str(local_file_path))
                print(f"Downloaded: {object_name} -> {local_file_path}")
                files_downloaded += 1
            except S3Error as e:
                print(f"Failed to download {object_name}: {e}")

        if files_downloaded == 0:
            print(f"No files found at: {git_trunk_without_src}")
        else:
            print(f"Total files downloaded: {files_downloaded}")
            print("Download operation completed!")

    except (S3Error, ValueError) as e:
        print(f"Error during download: {e}")
        sys.exit(1)


def main(args: argparse.Namespace) -> None:
    """Main entry point for the MinIO manager."""
    print("=" * 50)
    print("MinIO Artifact Manager")
    print("=" * 50)

    if args.mode == "upload":
        upload_to_minio(args)
    elif args.mode == "download":
        download_from_minio(args)
    else:
        print(f"Unknown mode: {args.mode}")
        sys.exit(1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="MinIO file transfer utility" )
    parser.add_argument(
        "--minio_secret_key", type=str, required=True,
        help="MinIO secret key for authentication" )
    parser.add_argument(
        "--minio_access_key", type=str, required=True,
        help="MinIO access key for authentication" )
    parser.add_argument(
        "--minio_api_uri", type=str, required=True,
        help="MinIO API uri")
    parser.add_argument(
        "--src_path", type=Path, required=True,
        help="Source file or directory path" )
    parser.add_argument(
        "--tgt_path", type=Path, required=False, default=Path('./'),
        help="Target file or directory path" )
    parser.add_argument(
        "--bucket", type=str, required=False, default="artifacts",
        help="Bucket name for MinIO operations" )
    parser.add_argument(
        "--mode", type=str, choices=["upload", "download"], required=True,
        help="Operation mode: upload or download" )
    parser.add_argument(
        "--use_git", type=bool, required=False, default=True,
        help="If git repo info is used for path generation" )

    main(parser.parse_args())