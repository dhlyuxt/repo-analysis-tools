from __future__ import annotations

from dataclasses import replace
from pathlib import Path
import re
from typing import Any

from repo_analysis_tools.export.models import ExportArtifact
from repo_analysis_tools.storage.json_assets import JsonAssetStore


_EXPORT_ID_PATTERN = re.compile(r"^export_[0-9a-f]{12}$")


def _validated_export_id(export_id: str) -> str:
    if not _EXPORT_ID_PATTERN.fullmatch(export_id):
        raise ValueError(f"invalid export_id: {export_id}")
    return export_id


class ExportStore:
    def __init__(self, target_repo: Path | str) -> None:
        self.assets = JsonAssetStore(target_repo, "export")

    @classmethod
    def for_repo(cls, target_repo: Path | str) -> "ExportStore":
        return cls(target_repo)

    def save(
        self,
        artifact: ExportArtifact,
        *,
        manifest: dict[str, Any],
        payload: dict[str, Any],
        markdown: str | None = None,
    ) -> ExportArtifact:
        export_id = _validated_export_id(artifact.export_id)
        manifest_path = self.assets.root / "bundles" / export_id / "manifest.json"
        payload_path = self.assets.root / "bundles" / export_id / "payload.json"
        copied_markdown_path = (
            None if markdown is None
            else (self.assets.root / "bundles" / export_id / "report.md").as_posix()
        )
        copied_paths = [payload_path.as_posix()]
        if copied_markdown_path is not None:
            copied_paths.append(copied_markdown_path)

        persisted = replace(
            artifact,
            manifest_path=manifest_path.as_posix(),
            payload_path=payload_path.as_posix(),
            copied_paths=copied_paths,
            copied_markdown_path=copied_markdown_path,
        )
        payload_to_write = dict(payload)
        if copied_markdown_path is not None:
            payload_to_write["markdown_path"] = copied_markdown_path
            Path(copied_markdown_path).parent.mkdir(parents=True, exist_ok=True)
            Path(copied_markdown_path).write_text(markdown or "", encoding="utf-8")

        self.assets.write_json(f"bundles/{export_id}/payload.json", payload_to_write)

        manifest_to_write = {
            "export_id": persisted.export_id,
            "export_kind": persisted.export_kind,
            "owner_tool": persisted.owner_tool,
            "source": {
                "kind": persisted.source_kind,
                "id": persisted.source_id,
            },
            "paths": {
                "manifest_path": persisted.manifest_path,
                "payload_path": persisted.payload_path,
                "copied_paths": list(persisted.copied_paths),
                "copied_markdown_path": persisted.copied_markdown_path,
            },
            "freshness": persisted.freshness.to_dict(),
            "artifact": manifest,
        }
        if persisted.scan_id is not None:
            manifest_to_write["scan_id"] = persisted.scan_id
        if persisted.evidence_pack_id is not None:
            manifest_to_write["evidence_pack_id"] = persisted.evidence_pack_id
        if persisted.report_id is not None:
            manifest_to_write["report_id"] = persisted.report_id

        self.assets.write_json(f"bundles/{export_id}/manifest.json", manifest_to_write)
        self.assets.write_json(f"results/{export_id}.json", persisted.to_dict())
        self.assets.write_json("latest.json", {"export_id": export_id})
        return persisted

    def load_latest(self) -> ExportArtifact:
        return self.load()

    def load(self, export_id: str | None = None) -> ExportArtifact:
        if export_id is None:
            resolved_export_id = _validated_export_id(str(self.assets.read_json("latest.json")["export_id"]))
        else:
            resolved_export_id = _validated_export_id(export_id)
        payload = self.assets.read_json(f"results/{resolved_export_id}.json")
        return ExportArtifact.from_dict(payload)
