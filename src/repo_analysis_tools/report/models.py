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

    def to_dict(self) -> dict[str, Any]:
        return {
            "report_id": self.report_id,
            "document_type": self.document_type,
            "title": self.title,
            "markdown_path": self.markdown_path,
            "section_titles": list(self.section_titles),
        }
