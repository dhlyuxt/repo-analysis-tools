from __future__ import annotations

from pathlib import Path
from typing import Sequence

from repo_analysis_tools.anchors.models import AnchorRecord
from repo_analysis_tools.anchors.store import AnchorStore
from repo_analysis_tools.core.ids import StableIdKind, make_stable_id
from repo_analysis_tools.core.paths import normalize_repo_relative_path
from repo_analysis_tools.evidence.freshness import evaluate_selected_file_freshness
from repo_analysis_tools.evidence.models import CitationRecord, EvidencePack, OpenSpanResult
from repo_analysis_tools.evidence.snippets import read_snippet
from repo_analysis_tools.evidence.store import EvidenceStore
from repo_analysis_tools.slice.models import SliceManifest
from repo_analysis_tools.slice.store import SliceStore


MAX_OPEN_SPAN_LINES = 80


class EvidenceService:
    def build(self, target_repo: Path | str, slice_id: str) -> EvidencePack:
        repo = Path(target_repo).expanduser().resolve()
        manifest = SliceStore.for_repo(repo).load(slice_id)
        drifted_files = evaluate_selected_file_freshness(repo, manifest.scan_id, manifest.selected_files)
        if drifted_files:
            drifted_list = ", ".join(drifted_files)
            raise ValueError(f"selected files drifted since scan {manifest.scan_id}: {drifted_list}")

        anchor_snapshot = AnchorStore.for_repo(repo).load(manifest.scan_id)
        citations = self._citations_for_manifest(manifest, anchor_snapshot.anchors)
        evidence_pack = EvidencePack(
            evidence_pack_id=make_stable_id(StableIdKind.EVIDENCE_PACK),
            slice_id=manifest.slice_id,
            scan_id=manifest.scan_id,
            repo_root=repo.as_posix(),
            summary=self._build_summary(manifest, citations),
            citations=citations,
        )
        EvidenceStore.for_repo(repo).save(evidence_pack)
        return evidence_pack

    def read(self, target_repo: Path | str, evidence_pack_id: str) -> EvidencePack:
        repo = Path(target_repo).expanduser().resolve()
        return EvidenceStore.for_repo(repo).load(evidence_pack_id)

    def open_span(
        self,
        target_repo: Path | str,
        evidence_pack_id: str,
        path: str,
        line_start: int,
        line_end: int,
    ) -> OpenSpanResult:
        repo = Path(target_repo).expanduser().resolve()
        evidence_pack = EvidenceStore.for_repo(repo).load(evidence_pack_id)
        normalized_path = normalize_repo_relative_path(repo, path)
        self._validate_open_span_request(
            citations=evidence_pack.citations,
            path=normalized_path,
            line_start=line_start,
            line_end=line_end,
        )
        return OpenSpanResult(
            target_repo=repo.as_posix(),
            evidence_pack_id=evidence_pack.evidence_pack_id,
            path=normalized_path,
            line_start=line_start,
            line_end=line_end,
            lines=read_snippet(repo, normalized_path, line_start, line_end),
        )

    def _citations_for_manifest(
        self,
        manifest: SliceManifest,
        anchors: list[AnchorRecord],
    ) -> list[CitationRecord]:
        member_anchor_names = {
            member.path: set(member.anchor_names)
            for member in manifest.members
        }
        selected_files = set(manifest.selected_files)
        selected_anchor_names = set(manifest.selected_anchor_names)
        citations: dict[tuple[str, str, int, int, str], CitationRecord] = {}

        for anchor in anchors:
            if not self._anchor_matches_selection(
                anchor,
                member_anchor_names=member_anchor_names,
                selected_files=selected_files,
                selected_anchor_names=selected_anchor_names,
            ):
                continue
            citation = CitationRecord(
                file_path=anchor.path,
                anchor_name=anchor.name,
                kind=anchor.kind,
                line_start=anchor.start_line,
                line_end=anchor.end_line,
            )
            citations[
                (
                    citation.file_path,
                    citation.anchor_name,
                    citation.line_start,
                    citation.line_end,
                    citation.kind,
                )
            ] = citation

        return sorted(
            citations.values(),
            key=lambda citation: (
                citation.file_path,
                citation.line_start,
                citation.line_end,
                citation.anchor_name,
                citation.kind,
            ),
        )

    def _anchor_matches_selection(
        self,
        anchor: AnchorRecord,
        *,
        member_anchor_names: dict[str, set[str]],
        selected_files: set[str],
        selected_anchor_names: set[str],
    ) -> bool:
        if member_anchor_names:
            names_for_path = member_anchor_names.get(anchor.path)
            if names_for_path is None:
                return False
            if names_for_path:
                return anchor.name in names_for_path
            return True

        if selected_files and anchor.path not in selected_files:
            return False
        if selected_anchor_names and anchor.name not in selected_anchor_names:
            return False
        return bool(selected_files or selected_anchor_names)

    def _build_summary(self, manifest: SliceManifest, citations: list[CitationRecord]) -> str:
        file_count = len({citation.file_path for citation in citations})
        return (
            f"Evidence pack for slice {manifest.slice_id} contains {len(citations)} citations "
            f"across {file_count} file(s)."
        )

    def _validate_open_span_request(
        self,
        *,
        citations: Sequence[CitationRecord],
        path: str,
        line_start: int,
        line_end: int,
    ) -> None:
        if line_start < 1 or line_end < line_start:
            raise ValueError("line range must satisfy 1 <= line_start <= line_end")
        if line_end - line_start + 1 > MAX_OPEN_SPAN_LINES:
            raise ValueError(
                f"requested span exceeds MAX_OPEN_SPAN_LINES ({MAX_OPEN_SPAN_LINES})"
            )
        for citation in citations:
            if (
                citation.file_path == path
                and line_start >= citation.line_start
                and line_end <= citation.line_end
            ):
                return
        raise ValueError("requested span must be fully covered by an evidence citation")
