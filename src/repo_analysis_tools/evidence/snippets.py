from __future__ import annotations

from pathlib import Path

from repo_analysis_tools.core.paths import normalize_repo_relative_path


def _decode_source(raw_bytes: bytes) -> str:
    for encoding in ("utf-8", "gb18030"):
        try:
            return raw_bytes.decode(encoding)
        except UnicodeDecodeError:
            continue
    return raw_bytes.decode("utf-8", errors="replace")


def read_snippet(target_repo: Path | str, relative_path: str, line_start: int, line_end: int) -> str:
    if line_start < 1 or line_end < line_start:
        raise ValueError("line range must satisfy 1 <= line_start <= line_end")

    repo = Path(target_repo).expanduser().resolve()
    normalized_path = normalize_repo_relative_path(repo, relative_path)
    source_path = repo / normalized_path
    source_text = _decode_source(source_path.read_bytes())
    lines = source_text.splitlines()

    if line_end > len(lines):
        raise ValueError(f"requested line range exceeds file length for {normalized_path}")
    return "\n".join(lines[line_start - 1 : line_end])
