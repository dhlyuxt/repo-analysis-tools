from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class ScopedFile:
    path: str
    role: str
    node_id: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "path": self.path,
            "role": self.role,
            "node_id": self.node_id,
        }

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "ScopedFile":
        return cls(
            path=str(payload["path"]),
            role=str(payload["role"]),
            node_id=str(payload["node_id"]),
        )


@dataclass(frozen=True)
class ScopeNode:
    node_id: str
    label: str
    role: str
    file_count: int
    related_files: list[str]

    def to_dict(self) -> dict[str, Any]:
        return {
            "node_id": self.node_id,
            "label": self.label,
            "role": self.role,
            "file_count": self.file_count,
            "related_files": list(self.related_files),
        }

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "ScopeNode":
        return cls(
            node_id=str(payload["node_id"]),
            label=str(payload["label"]),
            role=str(payload["role"]),
            file_count=int(payload["file_count"]),
            related_files=[str(path) for path in payload.get("related_files", [])],
        )


@dataclass(frozen=True)
class ScopeSnapshot:
    scan_id: str
    repo_root: str
    scope_summary: str
    role_counts: dict[str, int]
    nodes: list[ScopeNode]
    files: list[ScopedFile]

    def to_dict(self) -> dict[str, Any]:
        return {
            "scan_id": self.scan_id,
            "repo_root": self.repo_root,
            "scope_summary": self.scope_summary,
            "role_counts": dict(self.role_counts),
            "nodes": [node.to_dict() for node in self.nodes],
            "files": [scoped_file.to_dict() for scoped_file in self.files],
        }

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "ScopeSnapshot":
        return cls(
            scan_id=str(payload["scan_id"]),
            repo_root=str(payload["repo_root"]),
            scope_summary=str(payload["scope_summary"]),
            role_counts={
                str(role): int(count)
                for role, count in payload.get("role_counts", {}).items()
            },
            nodes=[ScopeNode.from_dict(item) for item in payload.get("nodes", [])],
            files=[ScopedFile.from_dict(item) for item in payload.get("files", [])],
        )
