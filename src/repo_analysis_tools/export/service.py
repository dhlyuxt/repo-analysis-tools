from __future__ import annotations

from pathlib import Path

from repo_analysis_tools.core.ids import StableIdKind, make_stable_id
from repo_analysis_tools.evidence.store import EvidenceStore
from repo_analysis_tools.export.freshness import (
    evaluate_evidence_freshness,
    evaluate_report_freshness,
    evaluate_scope_freshness,
)
from repo_analysis_tools.export.models import ExportArtifact
from repo_analysis_tools.export.store import ExportStore
from repo_analysis_tools.report.store import ReportStore
from repo_analysis_tools.scope.store import ScopeStore


class ExportService:
    def export_analysis_bundle(self, target_repo: Path | str, report_id: str) -> ExportArtifact:
        repo = Path(target_repo).expanduser().resolve()
        report = ReportStore.for_repo(repo).load(report_id)
        freshness = evaluate_report_freshness(repo, report)
        artifact = ExportArtifact(
            export_id=make_stable_id(StableIdKind.EXPORT),
            export_kind="analysis-bundle",
            source_kind="report",
            source_id=report.report_id,
            owner_tool="export_analysis_bundle",
            manifest_path="",
            payload_path="",
            copied_paths=[],
            freshness=freshness,
            scan_id=report.scan_id,
            evidence_pack_id=report.evidence_pack_id,
            report_id=report.report_id,
        )
        return ExportStore.for_repo(repo).save(
            artifact,
            manifest={
                "report_id": report.report_id,
                "document_type": report.document_type,
                "title": report.title,
                "section_titles": list(report.section_titles),
                "evidence_pack_id": report.evidence_pack_id,
                "scan_id": report.scan_id,
            },
            payload=report.to_dict(),
            markdown=report.markdown,
        )

    def export_scope_snapshot(self, target_repo: Path | str, scan_id: str | None = None) -> ExportArtifact:
        repo = Path(target_repo).expanduser().resolve()
        snapshot = ScopeStore.for_repo(repo).load(scan_id)
        freshness = evaluate_scope_freshness(repo, snapshot.scan_id)
        artifact = ExportArtifact(
            export_id=make_stable_id(StableIdKind.EXPORT),
            export_kind="scope-snapshot",
            source_kind="scope",
            source_id=snapshot.scan_id,
            owner_tool="export_scope_snapshot",
            manifest_path="",
            payload_path="",
            copied_paths=[],
            freshness=freshness,
            scan_id=snapshot.scan_id,
        )
        return ExportStore.for_repo(repo).save(
            artifact,
            manifest={
                "scan_id": snapshot.scan_id,
                "scope_summary": snapshot.scope_summary,
                "node_count": len(snapshot.nodes),
                "file_count": len(snapshot.files),
            },
            payload=snapshot.to_dict(),
        )

    def export_evidence_bundle(self, target_repo: Path | str, evidence_pack_id: str) -> ExportArtifact:
        repo = Path(target_repo).expanduser().resolve()
        evidence_pack = EvidenceStore.for_repo(repo).load(evidence_pack_id)
        freshness = evaluate_evidence_freshness(repo, evidence_pack)
        artifact = ExportArtifact(
            export_id=make_stable_id(StableIdKind.EXPORT),
            export_kind="evidence-bundle",
            source_kind="evidence",
            source_id=evidence_pack.evidence_pack_id,
            owner_tool="export_evidence_bundle",
            manifest_path="",
            payload_path="",
            copied_paths=[],
            freshness=freshness,
            scan_id=evidence_pack.scan_id,
            evidence_pack_id=evidence_pack.evidence_pack_id,
        )
        return ExportStore.for_repo(repo).save(
            artifact,
            manifest={
                "evidence_pack_id": evidence_pack.evidence_pack_id,
                "scan_id": evidence_pack.scan_id,
                "summary": evidence_pack.summary,
                "citation_count": evidence_pack.citation_count,
            },
            payload=evidence_pack.to_dict(),
        )
