from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class ScannedFile:
    path: str
    content_sha256: str
    size_bytes: int
    line_count: int

    def to_dict(self) -> dict[str, Any]:
        return {
            "path": self.path,
            "content_sha256": self.content_sha256,
            "size_bytes": self.size_bytes,
            "line_count": self.line_count,
        }

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "ScannedFile":
        return cls(
            path=str(payload["path"]),
            content_sha256=str(payload["content_sha256"]),
            size_bytes=int(payload["size_bytes"]),
            line_count=int(payload["line_count"]),
        )


@dataclass(frozen=True)
class ScanSnapshot:
    scan_id: str
    repo_root: str
    file_count: int
    completed_at: str
    git_head: str | None
    workspace_dirty: bool | None
    files: list[ScannedFile]

    def to_dict(self) -> dict[str, Any]:
        return {
            "scan_id": self.scan_id,
            "repo_root": self.repo_root,
            "file_count": self.file_count,
            "completed_at": self.completed_at,
            "git_head": self.git_head,
            "workspace_dirty": self.workspace_dirty,
            "files": [scanned_file.to_dict() for scanned_file in self.files],
        }

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "ScanSnapshot":
        return cls(
            scan_id=str(payload["scan_id"]),
            repo_root=str(payload["repo_root"]),
            file_count=int(payload["file_count"]),
            completed_at=str(payload["completed_at"]),
            git_head=payload.get("git_head"),
            workspace_dirty=payload.get("workspace_dirty"),
            files=[
                ScannedFile.from_dict(item)
                for item in payload.get("files", [])
            ],
        )
