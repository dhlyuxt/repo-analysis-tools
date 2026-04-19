from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from repo_analysis_tools.anchors.models import AnchorRecord


@dataclass(frozen=True)
class QueryClassification:
    query_kind: str
    symbol_name: str | None = None
    subject: str | None = None


@dataclass(frozen=True)
class SymbolResolution:
    exact_matches: list[AnchorRecord]
    close_matches: list[str]


@dataclass(frozen=True)
class SliceMember:
    path: str
    anchor_names: list[str]
    reason: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "path": self.path,
            "anchor_names": list(self.anchor_names),
            "reason": self.reason,
        }

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "SliceMember":
        return cls(
            path=str(payload["path"]),
            anchor_names=[str(item) for item in payload.get("anchor_names", [])],
            reason=str(payload["reason"]),
        )


@dataclass(frozen=True)
class SliceManifest:
    slice_id: str
    scan_id: str
    repo_root: str
    question: str
    query_kind: str
    status: str
    selected_files: list[str]
    selected_anchor_names: list[str]
    members: list[SliceMember]
    notes: list[str]

    def to_dict(self) -> dict[str, Any]:
        return {
            "slice_id": self.slice_id,
            "scan_id": self.scan_id,
            "repo_root": self.repo_root,
            "question": self.question,
            "query_kind": self.query_kind,
            "status": self.status,
            "selected_files": list(self.selected_files),
            "selected_anchor_names": list(self.selected_anchor_names),
            "members": [member.to_dict() for member in self.members],
            "notes": list(self.notes),
        }

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "SliceManifest":
        return cls(
            slice_id=str(payload["slice_id"]),
            scan_id=str(payload["scan_id"]),
            repo_root=str(payload["repo_root"]),
            question=str(payload["question"]),
            query_kind=str(payload["query_kind"]),
            status=str(payload["status"]),
            selected_files=[str(item) for item in payload.get("selected_files", [])],
            selected_anchor_names=[str(item) for item in payload.get("selected_anchor_names", [])],
            members=[SliceMember.from_dict(item) for item in payload.get("members", [])],
            notes=[str(item) for item in payload.get("notes", [])],
        )


@dataclass(frozen=True)
class SliceInspection:
    target_repo: str
    slice_id: str
    members: list[str]


@dataclass(frozen=True)
class SliceExpansion:
    target_repo: str
    slice_id: str
    expanded: bool
