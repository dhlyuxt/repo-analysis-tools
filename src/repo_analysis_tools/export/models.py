from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class FreshnessReport:
    state: str
    summary: str
    drifted_paths: list[str]

    def to_dict(self) -> dict[str, Any]:
        return {
            "state": self.state,
            "summary": self.summary,
            "drifted_paths": list(self.drifted_paths),
        }

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "FreshnessReport":
        return cls(
            state=str(payload["state"]),
            summary=str(payload["summary"]),
            drifted_paths=[str(path) for path in payload.get("drifted_paths", [])],
        )


@dataclass(frozen=True)
class ExportArtifact:
    export_id: str
    export_kind: str
    source_kind: str
    source_id: str
    owner_tool: str
    manifest_path: str
    payload_path: str
    copied_paths: list[str]
    freshness: FreshnessReport
    copied_markdown_path: str | None = None
    scan_id: str | None = None
    evidence_pack_id: str | None = None
    report_id: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "export_id": self.export_id,
            "export_kind": self.export_kind,
            "source_kind": self.source_kind,
            "source_id": self.source_id,
            "owner_tool": self.owner_tool,
            "manifest_path": self.manifest_path,
            "payload_path": self.payload_path,
            "copied_paths": list(self.copied_paths),
            "copied_markdown_path": self.copied_markdown_path,
            "freshness": self.freshness.to_dict(),
            "scan_id": self.scan_id,
            "evidence_pack_id": self.evidence_pack_id,
            "report_id": self.report_id,
        }

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "ExportArtifact":
        return cls(
            export_id=str(payload["export_id"]),
            export_kind=str(payload["export_kind"]),
            source_kind=str(payload["source_kind"]),
            source_id=str(payload["source_id"]),
            owner_tool=str(payload["owner_tool"]),
            manifest_path=str(payload["manifest_path"]),
            payload_path=str(payload["payload_path"]),
            copied_paths=[str(path) for path in payload.get("copied_paths", [])],
            copied_markdown_path=(
                None if payload.get("copied_markdown_path") is None else str(payload["copied_markdown_path"])
            ),
            freshness=FreshnessReport.from_dict(payload["freshness"]),
            scan_id=None if payload.get("scan_id") is None else str(payload["scan_id"]),
            evidence_pack_id=(
                None if payload.get("evidence_pack_id") is None else str(payload["evidence_pack_id"])
            ),
            report_id=None if payload.get("report_id") is None else str(payload["report_id"]),
        )
