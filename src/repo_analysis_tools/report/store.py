from __future__ import annotations

from pathlib import Path
import re

from repo_analysis_tools.report.models import ReportArtifact
from repo_analysis_tools.storage.json_assets import JsonAssetStore


_REPORT_ID_PATTERN = re.compile(r"^report_[0-9a-f]{12}$")


def _validated_report_id(report_id: str) -> str:
    if not _REPORT_ID_PATTERN.fullmatch(report_id):
        raise ValueError(f"invalid report_id: {report_id}")
    return report_id


class ReportStore:
    def __init__(self, target_repo: Path | str) -> None:
        self.assets = JsonAssetStore(target_repo, "report")

    @classmethod
    def for_repo(cls, target_repo: Path | str) -> "ReportStore":
        return cls(target_repo)

    def save(self, artifact: ReportArtifact) -> ReportArtifact:
        report_id = _validated_report_id(artifact.report_id)
        markdown_path = self.assets.root / "rendered" / f"{report_id}.md"
        markdown_path.parent.mkdir(parents=True, exist_ok=True)
        markdown_path.write_text(artifact.markdown, encoding="utf-8")
        persisted = ReportArtifact(
            report_id=artifact.report_id,
            document_type=artifact.document_type,
            title=artifact.title,
            markdown=artifact.markdown,
            markdown_path=markdown_path.as_posix(),
            section_titles=list(artifact.section_titles),
            evidence_pack_id=artifact.evidence_pack_id,
            scan_id=artifact.scan_id,
        )
        self.assets.write_json(f"results/{report_id}.json", persisted.to_dict())
        self.assets.write_json("latest.json", {"report_id": report_id})
        return persisted

    def load_latest(self) -> ReportArtifact:
        return self.load()

    def load(self, report_id: str | None = None) -> ReportArtifact:
        if report_id is None:
            resolved_report_id = _validated_report_id(str(self.assets.read_json("latest.json")["report_id"]))
        else:
            resolved_report_id = _validated_report_id(report_id)
        payload = self.assets.read_json(f"results/{resolved_report_id}.json")
        markdown_path = Path(str(payload["markdown_path"]))
        return ReportArtifact.from_dict(payload, markdown=markdown_path.read_text(encoding="utf-8"))
