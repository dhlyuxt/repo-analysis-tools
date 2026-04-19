from __future__ import annotations

import hashlib
from pathlib import Path

from repo_analysis_tools.core.paths import normalize_repo_relative_path
from repo_analysis_tools.scan.store import ScanStore


def evaluate_selected_file_freshness(
    target_repo: Path | str,
    scan_id: str,
    selected_files: list[str],
) -> list[str]:
    repo = Path(target_repo).expanduser().resolve()
    scan_snapshot = ScanStore.for_repo(repo).load(scan_id)
    expected_digests = {
        scanned_file.path: scanned_file.content_sha256
        for scanned_file in scan_snapshot.files
    }

    drifted: list[str] = []
    for selected_file in sorted({normalize_repo_relative_path(repo, path) for path in selected_files}):
        expected_digest = expected_digests.get(selected_file)
        source_path = repo / selected_file
        if expected_digest is None or not source_path.is_file():
            drifted.append(selected_file)
            continue
        actual_digest = hashlib.sha256(source_path.read_bytes()).hexdigest()
        if actual_digest != expected_digest:
            drifted.append(selected_file)
    return drifted
