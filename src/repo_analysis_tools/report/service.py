from __future__ import annotations

from pathlib import Path

from repo_analysis_tools.core.ids import StableIdKind, make_stable_id
from repo_analysis_tools.doc_dsl.builders import (
    build_design_note_document,
    build_issue_analysis_document,
    build_module_summary_document,
    build_review_report_document,
)
from repo_analysis_tools.doc_dsl.mermaid_validator import MermaidValidator
from repo_analysis_tools.doc_dsl.models import Document, MermaidBlock
from repo_analysis_tools.doc_dsl.validators import validate_document
from repo_analysis_tools.doc_specs.base import build_document_spec_registry
from repo_analysis_tools.evidence.models import EvidencePack
from repo_analysis_tools.evidence.store import EvidenceStore
from repo_analysis_tools.renderers.markdown import MarkdownRenderer
from repo_analysis_tools.report.models import ReportArtifact
from repo_analysis_tools.report.store import ReportStore


class ReportService:
    def __init__(
        self,
        renderer: MarkdownRenderer | None = None,
        mermaid_validator: MermaidValidator | None = None,
    ) -> None:
        self.renderer = renderer or MarkdownRenderer()
        self.mermaid_validator = mermaid_validator or MermaidValidator()

    def render_module_summary(
        self,
        target_repo: Path | str,
        evidence_pack_id: str,
        module_name: str,
    ) -> ReportArtifact:
        repo = Path(target_repo).expanduser().resolve()
        evidence_pack = EvidenceStore.for_repo(repo).load(evidence_pack_id)
        document = build_module_summary_document(evidence_pack, module_name)
        return self._render_and_persist(repo, document, evidence_pack=evidence_pack)

    def render_focus_report(
        self,
        target_repo: Path | str,
        evidence_pack_id: str,
        document_type: str = "review-report",
    ) -> ReportArtifact:
        repo = Path(target_repo).expanduser().resolve()
        evidence_pack = EvidenceStore.for_repo(repo).load(evidence_pack_id)
        if document_type == "issue-analysis":
            document = build_issue_analysis_document(evidence_pack, "Evidence-backed focus")
        elif document_type == "review-report":
            document = build_review_report_document(evidence_pack, "Evidence-backed review")
        else:
            raise ValueError(f"unsupported document_type: {document_type}")
        return self._render_and_persist(repo, document, evidence_pack=evidence_pack)

    def render_analysis_outline(self, target_repo: Path | str, focus: str) -> ReportArtifact:
        repo = Path(target_repo).expanduser().resolve()
        document = build_design_note_document(focus)
        return self._render_and_persist(repo, document)

    def _render_and_persist(
        self,
        target_repo: Path,
        document: Document,
        *,
        evidence_pack: EvidencePack | None = None,
    ) -> ReportArtifact:
        spec = build_document_spec_registry()[document.document_type]
        errors = validate_document(document, spec)
        if errors:
            raise ValueError("; ".join(errors))
        for section in document.sections:
            for block in section.blocks:
                if isinstance(block, MermaidBlock):
                    self.mermaid_validator.validate(block.source, diagram_kind=block.diagram_kind)
        markdown = self.renderer.render(document)
        artifact = ReportArtifact(
            report_id=make_stable_id(StableIdKind.REPORT),
            document_type=document.document_type,
            title=document.title,
            markdown=markdown,
            markdown_path="",
            section_titles=[section.title for section in document.sections],
            evidence_pack_id=None if evidence_pack is None else evidence_pack.evidence_pack_id,
            scan_id=None if evidence_pack is None else evidence_pack.scan_id,
        )
        return ReportStore.for_repo(target_repo).save(artifact)
