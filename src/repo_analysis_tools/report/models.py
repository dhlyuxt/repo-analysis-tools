from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class ReportArtifact:
    report_id: str
    document_type: str
    title: str
    markdown: str
    markdown_path: str
    section_titles: list[str]
    evidence_pack_id: str | None = None
    scan_id: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "report_id": self.report_id,
            "document_type": self.document_type,
            "title": self.title,
            "markdown_path": self.markdown_path,
            "section_titles": list(self.section_titles),
            "evidence_pack_id": self.evidence_pack_id,
            "scan_id": self.scan_id,
        }

    @classmethod
    def from_dict(cls, payload: dict[str, Any], *, markdown: str = "") -> "ReportArtifact":
        return cls(
            report_id=str(payload["report_id"]),
            document_type=str(payload["document_type"]),
            title=str(payload["title"]),
            markdown=markdown,
            markdown_path=str(payload["markdown_path"]),
            section_titles=[str(title) for title in payload.get("section_titles", [])],
            evidence_pack_id=(
                None if payload.get("evidence_pack_id") is None else str(payload["evidence_pack_id"])
            ),
            scan_id=None if payload.get("scan_id") is None else str(payload["scan_id"]),
        )
