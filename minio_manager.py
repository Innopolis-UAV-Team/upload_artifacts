import argparse
import os
import subprocess
import sys
from pathlib import Path
from urllib.parse import urlparse

from git import Repo, InvalidGitRepositoryError


def get_repo_name(repo: Repo) -> str:
    """Extract repository name from GitHub environment or git remote."""
    # First, try GitHub Actions environment variable (most reliable in CI/CD)
    github_repo = os.environ.get('GITHUB_REPOSITORY')
    if github_repo:
        # Format is "owner/repo-name", extract just the repo name
        return github_repo.split('/')[-1].lower()

    # Second, try to get from git remote
    try:
        if repo.remotes and len(repo.remotes) > 0:
            # Get the first remote (usually 'origin')
            remote = repo.remotes[0]
            for remote_url in remote.urls:
                # Parse different URL formats
                # SSH: git@github.com:user/repo.git
                # HTTPS: https://github.com/user/repo.git

                if remote_url.startswith('git@') or ':' in remote_url and not remote_url.startswith('http'):
                    # SSH format: git@github.com:user/repo.git
                    path_part = remote_url.split(':')[-1]
                else:
                    # HTTPS format: use urlparse
                    parsed = urlparse(remote_url)
                    path_part = parsed.path

                # Extract repo name from path
                repo_name = path_part.rstrip('/').split('/')[-1]

                # Remove .git suffix if present
                if repo_name.endswith('.git'):
                    repo_name = repo_name[:-4]
                if repo_name:
                    return repo_name.lower()

    except Exception as e:
        print(f"Warning: Could not extract repo name from git remote: {e}")

    # Final fallback to directory name
    return Path(repo.working_tree_dir).name.lower()


def generate_git_path(use_git: bool, target_path: Path) -> Path:
    """Generate path with git info if enabled."""
    if use_git:
        if 'GITHUB_WORKSPACE' in os.environ:
            os.chdir(os.environ['GITHUB_WORKSPACE'])
        try:
            repo = Repo(Path('./'))
            repo_name = get_repo_name(repo)
            branch_name = repo.active_branch.name
            commit_sha = repo.head.commit.hexsha[:7]

            print(f"Git repository detected: {repo_name}")
            print(f"  Branch: {branch_name}")
            print(f"  Commit: {commit_sha}")

            tgt_path_trunk = (
                    Path(repo_name) /
                    Path(branch_name) /
                    Path(f"SHA-{commit_sha}") /
                    target_path
            )
        except InvalidGitRepositoryError:
            print("No git repository found. Proceeding without git info.")
            tgt_path_trunk = target_path
    else:
        print("Git info usage disabled. Proceeding without git info.")
        tgt_path_trunk = target_path

    return tgt_path_trunk


def run_mc_command(cmd: list[str], check: bool = True) -> subprocess.CompletedProcess:
    """Run mc command and return result."""
    print(f"Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True, check=False)

    if result.stdout:
        print(result.stdout)
    if result.stderr:
        print(result.stderr, file=sys.stderr)

    if check and result.returncode != 0:
        print(f"Command failed with exit code {result.returncode}")
        sys.exit(result.returncode)

    return result


def setup_mc_alias(alias: str, endpoint: str, access_key: str, secret_key: str) -> None:
    """Configure mc alias."""
    print(f"Configuring MinIO client alias '{alias}'...")
    cmd = [
        'mc', 'alias', 'set', alias,
        endpoint, access_key, secret_key
    ]

    result = subprocess.run(cmd, capture_output=True, text=True, check=False)
    if result.returncode != 0:
        print(f"Command failed with exit code {result.returncode}")
        sys.exit(result.returncode)


def upload_to_minio(args: argparse.Namespace) -> None:
    """Handle upload operation using mc cp."""
    print("\nStarting upload operation...")

    # Setup mc alias
    alias = 'myminio'
    setup_mc_alias(alias, args.minio_api_uri, args.minio_access_key, args.minio_secret_key)
    tgt_path_trunk = Path(args.bucket) / generate_git_path(args.use_git, args.tgt_path)
    path_alias = Path(alias)

    run_mc_command(["mc", "mb", "-p", f"{(path_alias / tgt_path_trunk).as_posix()}"])

    run_mc_command(["mc", "cp", "-r", f"{args.src_path}", f"{(path_alias / tgt_path_trunk).as_posix()}"])

    print(f"\nUpload completed successfully to: {tgt_path_trunk.as_posix()}")


def download_from_minio(args: argparse.Namespace) -> None:
    """Handle download operation using mc cp."""
    print("\n⬇Starting download operation...")

    alias = 'myminio'
    setup_mc_alias(alias, args.minio_api_uri, args.minio_access_key, args.minio_secret_key)
    src_path_trunk = Path(args.bucket) / generate_git_path(args.use_git, args.src_path)
    args.tgt_path.mkdir(parents=True, exist_ok=True)
    path_alias = Path(alias)

    run_mc_command(["mc", "cp", "-r", f"{(path_alias / src_path_trunk).as_posix()}", f"{args.tgt_path}"])
    print(f"\nDownload completed successfully to: {args.tgt_path.as_posix()}")


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

    def str2bool(v):
        if isinstance(v, bool):
            return v
        if v.lower() in ('yes', 'true', 't', 'y', '1'):
            return True
        elif v.lower() in ('no', 'false', 'f', 'n', '0'):
            return False
        else:
            raise argparse.ArgumentTypeError('Boolean value expected.')

    parser = argparse.ArgumentParser(description="MinIO file transfer utility")
    parser.add_argument(
        "--minio_secret_key", type=str, required=True,
        help="MinIO secret key for authentication")
    parser.add_argument(
        "--minio_access_key", type=str, required=True,
        help="MinIO access key for authentication")
    parser.add_argument(
        "--minio_api_uri", type=str, required=True,
        help="MinIO API URI")
    parser.add_argument(
        "--src_path", type=Path, required=True,
        help="Source file or directory path")
    parser.add_argument(
        "--tgt_path", type=Path, required=False, default=Path('./'),
        help="Target file or directory path")
    parser.add_argument(
        "--bucket", type=str, required=False, default="artifacts",
        help="Bucket name for MinIO operations")
    parser.add_argument(
        "--mode", type=str, choices=["upload", "download"], required=True,
        help="Operation mode: upload or download")
    parser.add_argument(
        "--use_git", type=str2bool, required=False, default=True,
        help="If git repo info is used for path generation")

    main(parser.parse_args())

