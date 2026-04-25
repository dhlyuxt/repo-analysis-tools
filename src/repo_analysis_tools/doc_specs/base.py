from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class SectionPolicy:
    title: str
    mermaid_policy: str
    requires_evidence_bindings: bool = False


@dataclass(frozen=True)
class DocumentSpec:
    document_type: str
    required_sections: tuple[str, ...]
    section_policies: dict[str, SectionPolicy]


def build_document_spec_registry() -> dict[str, DocumentSpec]:
    from repo_analysis_tools.doc_specs.design_note import DESIGN_NOTE_SPEC
    from repo_analysis_tools.doc_specs.evidence_index import EVIDENCE_INDEX_SPEC
    from repo_analysis_tools.doc_specs.issue_analysis import ISSUE_ANALYSIS_SPEC
    from repo_analysis_tools.doc_specs.module_detail import MODULE_DETAIL_SPEC
    from repo_analysis_tools.doc_specs.module_map import MODULE_MAP_SPEC
    from repo_analysis_tools.doc_specs.module_summary import MODULE_SUMMARY_SPEC
    from repo_analysis_tools.doc_specs.reading_order import READING_ORDER_SPEC
    from repo_analysis_tools.doc_specs.repo_architecture import REPO_ARCHITECTURE_SPEC
    from repo_analysis_tools.doc_specs.review_report import REVIEW_REPORT_SPEC

    return {
        MODULE_SUMMARY_SPEC.document_type: MODULE_SUMMARY_SPEC,
        ISSUE_ANALYSIS_SPEC.document_type: ISSUE_ANALYSIS_SPEC,
        DESIGN_NOTE_SPEC.document_type: DESIGN_NOTE_SPEC,
        REVIEW_REPORT_SPEC.document_type: REVIEW_REPORT_SPEC,
        REPO_ARCHITECTURE_SPEC.document_type: REPO_ARCHITECTURE_SPEC,
        MODULE_MAP_SPEC.document_type: MODULE_MAP_SPEC,
        MODULE_DETAIL_SPEC.document_type: MODULE_DETAIL_SPEC,
        EVIDENCE_INDEX_SPEC.document_type: EVIDENCE_INDEX_SPEC,
        READING_ORDER_SPEC.document_type: READING_ORDER_SPEC,
    }
