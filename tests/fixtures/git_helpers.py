import subprocess
from pathlib import Path


def init_git_fixture(
    repo: Path,
    *,
    email: str = "fixtures@example.com",
    name: str = "Fixture Tests",
) -> str:
    subprocess.run(["git", "init"], cwd=repo, capture_output=True, text=True, check=True)
    subprocess.run(["git", "config", "user.email", email], cwd=repo, capture_output=True, text=True, check=True)
    subprocess.run(["git", "config", "user.name", name], cwd=repo, capture_output=True, text=True, check=True)
    subprocess.run(["git", "add", "."], cwd=repo, capture_output=True, text=True, check=True)
    subprocess.run(["git", "commit", "-m", "initial fixture"], cwd=repo, capture_output=True, text=True, check=True)
    return subprocess.run(["git", "rev-parse", "HEAD"], cwd=repo, capture_output=True, text=True, check=True).stdout.strip()
