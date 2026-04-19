from __future__ import annotations

from collections import defaultdict
from pathlib import Path

from repo_analysis_tools.anchors.models import AnchorRecord
from repo_analysis_tools.anchors.store import AnchorStore
from repo_analysis_tools.core.ids import StableIdKind, make_stable_id
from repo_analysis_tools.scan.store import ScanStore
from repo_analysis_tools.slice.models import SliceExpansion, SliceInspection, SliceManifest, SliceMember
from repo_analysis_tools.slice.query_classifier import QueryClassifier
from repo_analysis_tools.slice.seed_resolver import SeedResolver
from repo_analysis_tools.slice.store import SliceStore


class SliceService:
    def __init__(
        self,
        classifier: QueryClassifier | None = None,
        seed_resolver: SeedResolver | None = None,
    ) -> None:
        self.classifier = classifier or QueryClassifier()
        self.seed_resolver = seed_resolver or SeedResolver()

    def plan(self, target_repo: Path | str, question: str, scan_id: str | None = None) -> SliceManifest:
        repo = Path(target_repo).expanduser().resolve()
        classification = self.classifier.classify(question)
        scan_snapshot = ScanStore.for_repo(repo).load(scan_id=scan_id)
        anchor_snapshot = AnchorStore.for_repo(repo).load(scan_id=scan_snapshot.scan_id)

        selected_anchors: list[AnchorRecord]
        notes: str
        status = "complete"

        if classification.query_kind == "locate_symbol" and classification.symbol_name is not None:
            resolution = self.seed_resolver.resolve_symbol(repo, scan_snapshot.scan_id, classification.symbol_name)
            selected_anchors = self._definition_anchors(resolution.exact_matches)
            if selected_anchors:
                notes = f"Located definition candidates for {classification.symbol_name}."
            else:
                status = "no_match"
                notes = self._no_match_notes(classification.symbol_name, resolution.close_matches)
        elif classification.query_kind == "init_flow":
            selected_anchors = self._resolve_init_flow_anchors(anchor_snapshot.anchors)
            if selected_anchors:
                notes = "Selected entrypoint and init routines for startup flow inspection."
            else:
                status = "no_match"
                notes = "No startup-related anchors were found in the scanned repository."
        elif classification.query_kind == "file_role" and classification.subject is not None:
            selected_anchors = self._resolve_subject_path_anchors(anchor_snapshot.anchors, classification.subject)
            if selected_anchors:
                notes = f"Selected anchors associated with {classification.subject}."
            else:
                status = "no_match"
                notes = f"No anchors were associated with {classification.subject}."
        else:
            selected_anchors = []
            status = "no_match"
            notes = "No targeted slice heuristic matched this question yet."

        manifest = SliceManifest(
            slice_id=make_stable_id(StableIdKind.SLICE),
            scan_id=scan_snapshot.scan_id,
            repo_root=repo.as_posix(),
            question=question.strip(),
            query_kind=classification.query_kind,
            status=status,
            selected_files=self._selected_files(selected_anchors),
            selected_anchor_names=self._selected_anchor_names(selected_anchors),
            members=self._build_members(selected_anchors, classification.query_kind),
            notes=notes,
        )
        SliceStore.for_repo(repo).save(manifest)
        return manifest

    def inspect(self, target_repo: Path | str, slice_id: str) -> SliceInspection:
        repo = Path(target_repo).expanduser().resolve()
        manifest = SliceStore.for_repo(repo).load(slice_id)
        return SliceInspection(
            target_repo=repo.as_posix(),
            slice_id=manifest.slice_id,
            members=[member.to_dict() for member in manifest.members],
        )

    def expand(self, target_repo: Path | str, slice_id: str) -> SliceExpansion:
        repo = Path(target_repo).expanduser().resolve()
        manifest = SliceStore.for_repo(repo).load(slice_id)
        return SliceExpansion(
            target_repo=repo.as_posix(),
            slice_id=manifest.slice_id,
            expanded=False,
        )

    def _definition_anchors(self, anchors: list[AnchorRecord]) -> list[AnchorRecord]:
        definition_anchors = [anchor for anchor in anchors if anchor.kind.endswith("_definition")]
        if definition_anchors:
            return definition_anchors
        return anchors

    def _resolve_init_flow_anchors(self, anchors: list[AnchorRecord]) -> list[AnchorRecord]:
        return sorted(
            [
                anchor
                for anchor in anchors
                if anchor.kind == "function_definition"
                and anchor.path.startswith("src/")
                and (anchor.name == "main" or "init" in anchor.name.lower())
            ],
            key=lambda anchor: (anchor.path, anchor.start_line, anchor.end_line, anchor.anchor_id),
        )

    def _resolve_subject_path_anchors(self, anchors: list[AnchorRecord], subject: str) -> list[AnchorRecord]:
        normalized_subject = subject.strip().strip("'\"")
        if not normalized_subject:
            return []
        return sorted(
            [
                anchor
                for anchor in anchors
                if anchor.path == normalized_subject or anchor.path.endswith(normalized_subject)
            ],
            key=lambda anchor: (anchor.path, anchor.start_line, anchor.end_line, anchor.anchor_id),
        )

    def _selected_files(self, anchors: list[AnchorRecord]) -> list[str]:
        return sorted({anchor.path for anchor in anchors})

    def _selected_anchor_names(self, anchors: list[AnchorRecord]) -> list[str]:
        return sorted({anchor.name for anchor in anchors})

    def _build_members(self, anchors: list[AnchorRecord], reason: str) -> list[SliceMember]:
        member_anchor_names: dict[str, list[str]] = defaultdict(list)
        for anchor in anchors:
            member_anchor_names[anchor.path].append(anchor.name)
        return [
            SliceMember(
                path=path,
                anchor_names=sorted(set(anchor_names)),
                reason=reason,
            )
            for path, anchor_names in sorted(member_anchor_names.items())
        ]

    def _no_match_notes(self, symbol_name: str, close_matches: list[str]) -> str:
        if not close_matches:
            return f"No exact anchor match was found for {symbol_name}."
        suggestions = ", ".join(close_matches)
        return f"No exact anchor match was found for {symbol_name}. Close matches: {suggestions}."
