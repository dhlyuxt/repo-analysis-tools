from __future__ import annotations

import hashlib
from pathlib import Path

from repo_analysis_tools.core.paths import normalize_repo_relative_path
from repo_analysis_tools.doc_dsl.builders import (
    build_design_note_document,
    build_issue_analysis_document,
    build_module_summary_document,
    build_review_report_document,
)
from repo_analysis_tools.doc_dsl.models import Document
from repo_analysis_tools.renderers.markdown import MarkdownRenderer
from repo_analysis_tools.evidence.freshness import evaluate_selected_file_freshness
from repo_analysis_tools.evidence.models import EvidencePack
from repo_analysis_tools.evidence.store import EvidenceStore
from repo_analysis_tools.export.models import FreshnessReport
from repo_analysis_tools.report.models import ReportArtifact
from repo_analysis_tools.scan.store import ScanStore


def _collect_repo_digests(target_repo: Path) -> dict[str, str]:
    digests: dict[str, str] = {}
    for candidate in sorted(target_repo.rglob("*")):
        if not candidate.is_file():
            continue
        relative_path = normalize_repo_relative_path(target_repo, candidate)
        if relative_path.startswith(".git/") or relative_path.startswith(".codewiki/"):
            continue
        digests[relative_path] = hashlib.sha256(candidate.read_bytes()).hexdigest()
    return digests


def evaluate_scope_freshness(target_repo: Path | str, scan_id: str) -> FreshnessReport:
    repo = Path(target_repo).expanduser().resolve()
    snapshot = ScanStore.for_repo(repo).load(scan_id)
    expected_digests = {
        scanned_file.path: scanned_file.content_sha256
        for scanned_file in snapshot.files
    }
    current_digests = _collect_repo_digests(repo)
    drifted_paths = sorted(
        {
            path
            for path, expected_digest in expected_digests.items()
            if current_digests.get(path) != expected_digest
        }
        | {path for path in current_digests if path not in expected_digests}
    )
    if drifted_paths:
        return FreshnessReport(
            state="stale",
            summary=f"{len(drifted_paths)} file(s) drifted since scan {scan_id}.",
            drifted_paths=drifted_paths,
        )
    return FreshnessReport(
        state="fresh",
        summary=f"Repository contents still match scan {scan_id}.",
        drifted_paths=[],
    )


def evaluate_evidence_freshness(target_repo: Path | str, evidence_pack: EvidencePack) -> FreshnessReport:
    repo = Path(target_repo).expanduser().resolve()
    selected_files = sorted({citation.file_path for citation in evidence_pack.citations})
    drifted_paths = evaluate_selected_file_freshness(repo, evidence_pack.scan_id, selected_files)
    if drifted_paths:
        return FreshnessReport(
            state="stale",
            summary=(
                f"{len(drifted_paths)} cited file(s) drifted since scan {evidence_pack.scan_id}."
            ),
            drifted_paths=drifted_paths,
        )
    return FreshnessReport(
        state="fresh",
        summary=f"Cited files still match scan {evidence_pack.scan_id}.",
        drifted_paths=[],
    )


def _expected_report_document(report: ReportArtifact, evidence_pack: EvidencePack) -> Document | None:
    if report.document_type == "module-summary":
        module_prefix = "Module Summary: "
        if not report.title.startswith(module_prefix):
            return None
        module_name = report.title[len(module_prefix) :]
        if not module_name:
            return None
        return build_module_summary_document(evidence_pack, module_name)
    if report.document_type == "issue-analysis":
        return build_issue_analysis_document(evidence_pack, "Evidence-backed focus")
    if report.document_type == "review-report":
        return build_review_report_document(evidence_pack, "Evidence-backed review")
    if report.document_type == "design-note":
        design_prefix = "Design Note: "
        if not report.title.startswith(design_prefix):
            return None
        focus = report.title[len(design_prefix) :]
        if not focus:
            return None
        return build_design_note_document(focus)
    return None


def _evaluate_report_artifact_freshness(
    target_repo: Path,
    report: ReportArtifact,
    evidence_pack: EvidencePack,
) -> FreshnessReport:
    expected_document = _expected_report_document(report, evidence_pack)
    if expected_document is None:
        return FreshnessReport(
            state="stale",
            summary=f"Report {report.report_id} no longer matches its persisted analysis inputs.",
            drifted_paths=[
                normalize_repo_relative_path(
                    target_repo,
                    target_repo / ".codewiki" / "report" / "results" / f"{report.report_id}.json",
                ),
                normalize_repo_relative_path(
                    target_repo,
                    Path(report.markdown_path),
                ),
            ],
        )

    expected_markdown = MarkdownRenderer().render(expected_document)
    expected_payload_path = normalize_repo_relative_path(
        target_repo,
        target_repo / ".codewiki" / "report" / "results" / f"{report.report_id}.json",
    )
    expected_markdown_path = normalize_repo_relative_path(
        target_repo,
        target_repo / ".codewiki" / "report" / "rendered" / f"{report.report_id}.md",
    )
    drifted_paths: list[str] = []

    if report.document_type != expected_document.document_type:
        drifted_paths.append(expected_payload_path)
    if report.title != expected_document.title:
        drifted_paths.append(expected_payload_path)
    if list(report.section_titles) != [section.title for section in expected_document.sections]:
        drifted_paths.append(expected_payload_path)
    if report.evidence_pack_id != evidence_pack.evidence_pack_id or report.scan_id != evidence_pack.scan_id:
        drifted_paths.append(expected_payload_path)
    if normalize_repo_relative_path(target_repo, Path(report.markdown_path)) != expected_markdown_path:
        drifted_paths.append(expected_payload_path)
    if report.markdown != expected_markdown:
        drifted_paths.append(expected_markdown_path)

    if drifted_paths:
        return FreshnessReport(
            state="stale",
            summary=f"Report {report.report_id} drifted from its persisted analysis artifact.",
            drifted_paths=sorted(set(drifted_paths)),
        )
    return FreshnessReport(
        state="fresh",
        summary=f"Report {report.report_id} still matches its persisted analysis artifact.",
        drifted_paths=[],
    )


def evaluate_report_freshness(target_repo: Path | str, report: ReportArtifact) -> FreshnessReport:
    repo = Path(target_repo).expanduser().resolve()
    if report.evidence_pack_id is not None:
        evidence_pack = EvidenceStore.for_repo(repo).load(report.evidence_pack_id)
        report_freshness = _evaluate_report_artifact_freshness(repo, report, evidence_pack)
        if report_freshness.state != "fresh":
            return report_freshness
        return evaluate_evidence_freshness(repo, evidence_pack)
    if report.scan_id is not None:
        return evaluate_scope_freshness(repo, report.scan_id)
    return FreshnessReport(
        state="unknown",
        summary=f"Report {report.report_id} has no persisted source provenance to evaluate freshness.",
        drifted_paths=[],
    )
