from __future__ import annotations

from pathlib import Path, PurePosixPath
import re

from repo_analysis_tools.anchors.models import AnchorDescription, AnchorRelation, AnchorSnapshot
from repo_analysis_tools.anchors.parser import CAnchorParser, _strip_comments_and_strings
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
        relations = self._relinked_relations(repo, anchors, relations)
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

    def _relinked_relations(
        self,
        repo: Path,
        anchors: list,
        relations: list[AnchorRelation],
    ) -> list[AnchorRelation]:
        anchors_by_id = {anchor.anchor_id: anchor for anchor in anchors}
        definition_anchors_by_name: dict[str, list] = {}
        static_definition_ids = self._static_definition_ids(repo, anchors)
        known_paths = {anchor.path for anchor in anchors}

        for anchor in anchors:
            if anchor.kind != "function_definition":
                continue
            definition_anchors_by_name.setdefault(anchor.name, []).append(anchor)

        for candidates in definition_anchors_by_name.values():
            candidates.sort(key=lambda item: (item.path, item.start_line, item.end_line))

        relinked: list[AnchorRelation] = []
        for relation in relations:
            if relation.kind == "direct_call":
                source_anchor = anchors_by_id.get(relation.source_anchor_id)
                target_anchor = self._resolve_call_target(
                    definition_anchors_by_name,
                    static_definition_ids,
                    source_anchor.path if source_anchor is not None else None,
                    relation.target_name,
                )
                if target_anchor is not None:
                    relinked.append(
                        AnchorRelation(
                            kind=relation.kind,
                            source_anchor_id=relation.source_anchor_id,
                            source_name=relation.source_name,
                            target_name=relation.target_name,
                            target_anchor_id=target_anchor.anchor_id,
                            target_path=target_anchor.path,
                            line=relation.line,
                        )
                    )
                    continue

            if relation.kind == "includes":
                resolved_target_path = self._resolve_include_target_path(
                    anchors_by_id=anchors_by_id,
                    known_paths=known_paths,
                    relation=relation,
                )
                relinked.append(
                    AnchorRelation(
                        kind=relation.kind,
                        source_anchor_id=relation.source_anchor_id,
                        source_name=relation.source_name,
                        target_name=relation.target_name,
                        target_anchor_id=relation.target_anchor_id,
                        target_path=resolved_target_path,
                        line=relation.line,
                    )
                )
                continue

            relinked.append(relation)
        return relinked

    def _resolve_call_target(
        self,
        definition_anchors_by_name: dict[str, list],
        static_definition_ids: set[str],
        source_path: str | None,
        target_name: str,
    ):
        candidates = definition_anchors_by_name.get(target_name, [])
        if source_path is not None:
            same_file_candidates = [candidate for candidate in candidates if candidate.path == source_path]
            if len(same_file_candidates) == 1:
                return same_file_candidates[0]

        visible_candidates = [
            candidate for candidate in candidates if candidate.anchor_id not in static_definition_ids
        ]
        if len(visible_candidates) != 1:
            return None
        return visible_candidates[0]

    def _static_definition_ids(self, repo: Path, anchors: list) -> set[str]:
        static_ids: set[str] = set()
        source_cache: dict[str, str] = {}
        for anchor in anchors:
            if anchor.kind != "function_definition":
                continue
            source_text = source_cache.get(anchor.path)
            if source_text is None:
                source_text = (repo / anchor.path).read_text(encoding="utf-8", errors="ignore")
                source_cache[anchor.path] = source_text
            if self._is_static_function_definition(source_text, anchor.name, anchor.start_line, anchor.end_line):
                static_ids.add(anchor.anchor_id)
        return static_ids

    def _is_static_function_definition(self, source_text: str, name: str, start_line: int, end_line: int) -> bool:
        lines = source_text.splitlines()
        header_start = max(0, start_line - 1)
        header_end = min(len(lines), max(start_line, end_line))
        header = "\n".join(lines[header_start:header_end])
        cleaned_header = _strip_comments_and_strings(header)
        match = re.search(rf"\b{re.escape(name)}\s*\(", cleaned_header)
        if match is None:
            return False
        return re.search(r"\bstatic\b", cleaned_header[: match.start()]) is not None

    def _resolve_include_target_path(
        self,
        *,
        anchors_by_id: dict[str, object],
        known_paths: set[str],
        relation: AnchorRelation,
    ) -> str | None:
        raw_target = relation.target_path or relation.target_name
        if raw_target is None:
            return relation.target_path
        if raw_target in known_paths:
            return raw_target

        source_anchor = anchors_by_id.get(relation.source_anchor_id)
        if source_anchor is not None:
            source_dir = PurePosixPath(source_anchor.path).parent
            relative_candidate = (source_dir / raw_target).as_posix()
            if relative_candidate in known_paths:
                return relative_candidate

        basename_matches = sorted(
            path for path in known_paths if PurePosixPath(path).name == PurePosixPath(raw_target).name
        )
        if len(basename_matches) == 1:
            return basename_matches[0]
        return relation.target_path
