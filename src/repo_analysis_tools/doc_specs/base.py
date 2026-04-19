from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class SectionPolicy:
    title: str
    mermaid_policy: str


@dataclass(frozen=True)
class DocumentSpec:
    document_type: str
    required_sections: tuple[str, ...]
    section_policies: dict[str, SectionPolicy]


def build_document_spec_registry() -> dict[str, DocumentSpec]:
    from repo_analysis_tools.doc_specs.design_note import DESIGN_NOTE_SPEC
    from repo_analysis_tools.doc_specs.issue_analysis import ISSUE_ANALYSIS_SPEC
    from repo_analysis_tools.doc_specs.module_summary import MODULE_SUMMARY_SPEC
    from repo_analysis_tools.doc_specs.review_report import REVIEW_REPORT_SPEC

    return {
        MODULE_SUMMARY_SPEC.document_type: MODULE_SUMMARY_SPEC,
        ISSUE_ANALYSIS_SPEC.document_type: ISSUE_ANALYSIS_SPEC,
        DESIGN_NOTE_SPEC.document_type: DESIGN_NOTE_SPEC,
        REVIEW_REPORT_SPEC.document_type: REVIEW_REPORT_SPEC,
    }
