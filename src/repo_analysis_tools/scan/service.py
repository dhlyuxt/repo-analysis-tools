from __future__ import annotations

from datetime import datetime, timezone
import hashlib
from pathlib import Path

from repo_analysis_tools.core.git import detect_git_provenance
from repo_analysis_tools.core.ids import StableIdKind, make_stable_id
from repo_analysis_tools.core.paths import normalize_repo_relative_path
from repo_analysis_tools.anchors.service import AnchorService
from repo_analysis_tools.scan.models import ScannedFile, ScanSnapshot
from repo_analysis_tools.scan.store import ScanStore
from repo_analysis_tools.scope.service import ScopeService


class ScanService:
    def scan(self, target_repo: Path | str) -> ScanSnapshot:
        repo = Path(target_repo).expanduser().resolve()
        files: list[ScannedFile] = []
        for candidate in sorted(repo.rglob("*")):
            if not candidate.is_file():
                continue
            relative_path = normalize_repo_relative_path(repo, candidate)
            if relative_path.startswith(".git/") or relative_path.startswith(".codewiki/"):
                continue
            files.append(
                ScannedFile(
                    path=relative_path,
                    content_sha256=hashlib.sha256(candidate.read_bytes()).hexdigest(),
                    size_bytes=candidate.stat().st_size,
                    line_count=len(
                        candidate.read_text(encoding="utf-8", errors="ignore").splitlines()
                    ),
                )
            )
        git_head, workspace_dirty = detect_git_provenance(repo)
        snapshot = ScanSnapshot(
            scan_id=make_stable_id(StableIdKind.SCAN),
            repo_root=str(repo),
            file_count=len(files),
            completed_at=datetime.now(timezone.utc).isoformat(),
            git_head=git_head,
            workspace_dirty=workspace_dirty,
            files=files,
        )
        ScanStore.for_repo(repo).save(snapshot)
        AnchorService().build_snapshot(repo, snapshot.scan_id)
        ScopeService().build_snapshot(repo, snapshot.scan_id)
        return snapshot
