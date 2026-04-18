from pathlib import Path

from repo_analysis_tools.storage.contracts import STORAGE_BOUNDARIES


RUNTIME_DIRNAME = ".codewiki"


def _repo_root(target_repo: Path | str) -> Path:
    return Path(target_repo).expanduser().resolve()


def runtime_root(target_repo: Path | str) -> Path:
    return _repo_root(target_repo) / RUNTIME_DIRNAME


def normalize_repo_relative_path(target_repo: Path | str, candidate: Path | str) -> str:
    repo_root = _repo_root(target_repo)
    raw_path = Path(candidate)
    absolute_path = raw_path.resolve() if raw_path.is_absolute() else (repo_root / raw_path).resolve()
    try:
        relative_path = absolute_path.relative_to(repo_root)
    except ValueError as exc:
        raise ValueError(f"{candidate!s} escapes repository root {repo_root}") from exc
    return relative_path.as_posix()


def domain_storage_root(target_repo: Path | str, domain_name: str) -> Path:
    boundary = STORAGE_BOUNDARIES.get(domain_name)
    if boundary is None:
        raise ValueError(f"undeclared storage domain: {domain_name}")
    return runtime_root(target_repo) / boundary.directory_name
