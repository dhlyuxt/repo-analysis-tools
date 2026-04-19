from __future__ import annotations

from pathlib import Path

from repo_analysis_tools.anchors.models import AnchorDescription, AnchorRelation, AnchorSnapshot
from repo_analysis_tools.anchors.parser import CAnchorParser
from repo_analysis_tools.anchors.store import AnchorStore
from repo_analysis_tools.scan.store import ScanStore


class AnchorService:
    def __init__(self, parser: CAnchorParser | None = None) -> None:
        self.parser = parser or CAnchorParser()

    def build_snapshot(self, target_repo: Path | str, scan_id: str | None = None) -> AnchorSnapshot:
        repo = Path(target_repo).expanduser().resolve()
        scan_snapshot = ScanStore.for_repo(repo).load(scan_id=scan_id)
        anchors = []
        relations = []
        extraction_backend = "unknown"
        for scanned_file in sorted(scan_snapshot.files, key=lambda item: item.path):
            suffix = Path(scanned_file.path).suffix.lower()
            if suffix not in self.parser.SUPPORTED_SUFFIXES:
                continue
            source_text = (repo / scanned_file.path).read_text(encoding="utf-8", errors="ignore")
            parsed = self.parser.parse_file(scanned_file.path, source_text)
            extraction_backend = parsed.backend
            anchors.extend(parsed.anchors)
            relations.extend(parsed.relations)
        snapshot = AnchorSnapshot(
            scan_id=scan_snapshot.scan_id,
            repo_root=scan_snapshot.repo_root,
            extraction_backend=extraction_backend,
            anchors=anchors,
            relations=relations,
        )
        AnchorStore.for_repo(repo).save(snapshot)
        return snapshot

    def load_snapshot(self, target_repo: Path | str, scan_id: str | None = None) -> AnchorSnapshot:
        return AnchorStore.for_repo(target_repo).load(scan_id=scan_id)

    def find_anchor_matches(
        self,
        target_repo: Path | str,
        anchor_name: str,
        scan_id: str | None = None,
    ) -> list:
        validated_anchor_name = self._validated_anchor_name(anchor_name)
        snapshot = self.load_snapshot(target_repo, scan_id=scan_id)
        exact_matches = [anchor for anchor in snapshot.anchors if anchor.name == validated_anchor_name]
        if exact_matches:
            return sorted(
                exact_matches,
                key=lambda item: (
                    0 if item.kind == "function_definition" else 1,
                    item.path,
                    item.start_line,
                    item.kind,
                ),
            )
        lowered = validated_anchor_name.lower()
        return sorted(
            [anchor for anchor in snapshot.anchors if lowered in anchor.name.lower()],
            key=lambda item: (
                0 if item.kind == "function_definition" else 1,
                item.path,
                item.start_line,
                item.kind,
            ),
        )

    def describe_anchor(
        self,
        target_repo: Path | str,
        anchor_name: str,
        scan_id: str | None = None,
    ) -> AnchorDescription:
        validated_anchor_name = self._validated_anchor_name(anchor_name)
        snapshot = self.load_snapshot(target_repo, scan_id=scan_id)
        matches = self.find_anchor_matches(target_repo, validated_anchor_name, scan_id=scan_id)
        if not matches:
            raise FileNotFoundError(f"anchor {validated_anchor_name} was not found")
        anchor = sorted(
            matches,
            key=lambda item: (
                0 if item.kind == "function_definition" else 1,
                item.path,
                item.start_line,
                item.kind,
            ),
        )[0]
        relations = self._relations_for_anchor(snapshot.relations, anchor.anchor_id)
        location = f"{anchor.path}:{anchor.start_line}-{anchor.end_line}"
        description = f"{anchor.kind} {anchor.name} in {location}"
        return AnchorDescription(anchor=anchor, description=description, relations=relations)

    def _relations_for_anchor(
        self,
        relations: list[AnchorRelation],
        anchor_id: str,
    ) -> list[AnchorRelation]:
        return [
            relation
            for relation in relations
            if relation.source_anchor_id == anchor_id
        ]

    def _validated_anchor_name(self, anchor_name: str) -> str:
        normalized = anchor_name.strip()
        if not normalized:
            raise ValueError("anchor_name must not be empty")
        return normalized
