from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class AnchorRecord:
    anchor_id: str
    scope_node_id: str
    kind: str
    name: str
    path: str
    start_line: int
    end_line: int

    def to_dict(self) -> dict[str, Any]:
        return {
            "anchor_id": self.anchor_id,
            "scope_node_id": self.scope_node_id,
            "kind": self.kind,
            "name": self.name,
            "path": self.path,
            "start_line": self.start_line,
            "end_line": self.end_line,
        }

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "AnchorRecord":
        return cls(
            anchor_id=str(payload["anchor_id"]),
            scope_node_id=str(payload["scope_node_id"]),
            kind=str(payload["kind"]),
            name=str(payload["name"]),
            path=str(payload["path"]),
            start_line=int(payload["start_line"]),
            end_line=int(payload["end_line"]),
        )


@dataclass(frozen=True)
class AnchorRelation:
    kind: str
    source_anchor_id: str
    source_name: str
    target_name: str
    target_anchor_id: str | None = None
    target_path: str | None = None
    line: int | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "kind": self.kind,
            "source_anchor_id": self.source_anchor_id,
            "source_name": self.source_name,
            "target_name": self.target_name,
            "target_anchor_id": self.target_anchor_id,
            "target_path": self.target_path,
            "line": self.line,
        }

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "AnchorRelation":
        return cls(
            kind=str(payload["kind"]),
            source_anchor_id=str(payload["source_anchor_id"]),
            source_name=str(payload["source_name"]),
            target_name=str(payload["target_name"]),
            target_anchor_id=payload.get("target_anchor_id"),
            target_path=payload.get("target_path"),
            line=payload.get("line"),
        )


@dataclass(frozen=True)
class AnchorSnapshot:
    scan_id: str
    repo_root: str
    extraction_backend: str
    anchors: list[AnchorRecord]
    relations: list[AnchorRelation]

    def to_dict(self) -> dict[str, Any]:
        return {
            "scan_id": self.scan_id,
            "repo_root": self.repo_root,
            "extraction_backend": self.extraction_backend,
            "anchors": [anchor.to_dict() for anchor in self.anchors],
            "relations": [relation.to_dict() for relation in self.relations],
        }

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "AnchorSnapshot":
        return cls(
            scan_id=str(payload["scan_id"]),
            repo_root=str(payload["repo_root"]),
            extraction_backend=str(payload.get("extraction_backend", "unknown")),
            anchors=[AnchorRecord.from_dict(item) for item in payload.get("anchors", [])],
            relations=[AnchorRelation.from_dict(item) for item in payload.get("relations", [])],
        )


@dataclass(frozen=True)
class AnchorDescription:
    anchor: AnchorRecord
    description: str
    relations: list[AnchorRelation]
