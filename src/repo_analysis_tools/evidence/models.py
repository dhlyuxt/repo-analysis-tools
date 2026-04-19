from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class CitationRecord:
    file_path: str
    anchor_name: str
    kind: str
    line_start: int
    line_end: int

    def to_dict(self) -> dict[str, Any]:
        return {
            "file_path": self.file_path,
            "anchor_name": self.anchor_name,
            "kind": self.kind,
            "line_start": self.line_start,
            "line_end": self.line_end,
        }

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "CitationRecord":
        return cls(
            file_path=str(payload["file_path"]),
            anchor_name=str(payload["anchor_name"]),
            kind=str(payload["kind"]),
            line_start=int(payload["line_start"]),
            line_end=int(payload["line_end"]),
        )


@dataclass(frozen=True)
class EvidencePack:
    evidence_pack_id: str
    slice_id: str
    scan_id: str
    repo_root: str
    summary: str
    citations: list[CitationRecord]

    @property
    def citation_count(self) -> int:
        return len(self.citations)

    def to_dict(self) -> dict[str, Any]:
        return {
            "evidence_pack_id": self.evidence_pack_id,
            "slice_id": self.slice_id,
            "scan_id": self.scan_id,
            "repo_root": self.repo_root,
            "summary": self.summary,
            "citations": [citation.to_dict() for citation in self.citations],
        }

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "EvidencePack":
        return cls(
            evidence_pack_id=str(payload["evidence_pack_id"]),
            slice_id=str(payload["slice_id"]),
            scan_id=str(payload["scan_id"]),
            repo_root=str(payload["repo_root"]),
            summary=str(payload["summary"]),
            citations=[CitationRecord.from_dict(item) for item in payload.get("citations", [])],
        )


@dataclass(frozen=True)
class OpenSpanResult:
    target_repo: str
    evidence_pack_id: str
    path: str
    line_start: int
    line_end: int
    lines: list[str]
