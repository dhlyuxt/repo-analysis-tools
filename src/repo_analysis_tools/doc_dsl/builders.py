from __future__ import annotations

from repo_analysis_tools.doc_dsl.models import Document, EvidenceBinding, MermaidBlock, Section, TextBlock
from repo_analysis_tools.evidence.models import EvidencePack


def _bindings_from_evidence(evidence_pack: EvidencePack) -> list[EvidenceBinding]:
    return [
        EvidenceBinding(
            file_path=citation.file_path,
            anchor_name=citation.anchor_name,
            line_start=citation.line_start,
            line_end=citation.line_end,
        )
        for citation in evidence_pack.citations[:3]
    ]


def build_module_summary_document(evidence_pack: EvidencePack, module_name: str) -> Document:
    bindings = _bindings_from_evidence(evidence_pack)
    anchor_labels = ", ".join(binding.anchor_name or binding.file_path for binding in bindings)
    return Document(
        document_type="module-summary",
        title=f"Module Summary: {module_name}",
        sections=[
            Section("Summary", [TextBlock(f"Evidence-backed summary for module {module_name}.")]),
            Section("Key Anchors", [TextBlock(anchor_labels or evidence_pack.summary)]),
            Section(
                "Call Flow",
                [
                    MermaidBlock(
                        diagram_kind="flowchart",
                        source="flowchart LR\nQuestion --> Evidence --> Module\n",
                        caption="High-level module flow derived from the selected evidence.",
                        placement="inline",
                        evidence_bindings=bindings,
                        title="Module Flow",
                    ),
                ],
            ),
            Section("Risks", [TextBlock("Risk statements stay tied to cited evidence.")]),
            Section("Recommendations", [TextBlock("Prefer follow-up slices for deeper inspection.")]),
        ],
    )


def build_issue_analysis_document(evidence_pack: EvidencePack, issue_title: str) -> Document:
    bindings = _bindings_from_evidence(evidence_pack)
    return Document(
        document_type="issue-analysis",
        title=f"Issue Analysis: {issue_title}",
        sections=[
            Section("Issue Summary", [TextBlock(issue_title)]),
            Section("Evidence", [TextBlock(evidence_pack.summary)]),
            Section(
                "Causal Chain",
                [
                    MermaidBlock(
                        diagram_kind="flowchart",
                        source="flowchart TD\nSymptom --> Evidence --> SuspectedCause\n",
                        caption="Causal chain grounded in the selected evidence pack.",
                        placement="inline",
                        evidence_bindings=bindings,
                        title="Causal Chain",
                    ),
                ],
            ),
            Section("Unknowns", [TextBlock("List unresolved questions before concluding.")]),
            Section("Recommendations", [TextBlock("Recommend the next evidence-backed follow-up.")]),
        ],
    )


def build_design_note_document(focus: str) -> Document:
    return Document(
        document_type="design-note",
        title=f"Design Note: {focus}",
        sections=[
            Section("Context", [TextBlock(f"Design context for {focus}.")]),
            Section("Proposed Design", [TextBlock("Describe the proposed structure in concise terms.")]),
            Section(
                "Flow",
                [
                    MermaidBlock(
                        diagram_kind="flowchart",
                        source="flowchart LR\nInput --> Decision --> Output\n",
                        caption="Proposed flow for the design note.",
                        placement="inline",
                        evidence_bindings=[],
                        title="Proposed Flow",
                    ),
                ],
            ),
            Section("Tradeoffs", [TextBlock("Record the main tradeoffs explicitly.")]),
            Section("Open Questions", [TextBlock("List remaining unresolved design questions.")]),
        ],
    )


def build_review_report_document(evidence_pack: EvidencePack, title: str) -> Document:
    bindings = _bindings_from_evidence(evidence_pack)
    return Document(
        document_type="review-report",
        title=title,
        sections=[
            Section("Scope", [TextBlock(evidence_pack.summary)]),
            Section("Findings", [TextBlock("Summarize the evidence-backed findings.")]),
            Section(
                "Risk Map",
                [
                    MermaidBlock(
                        diagram_kind="flowchart",
                        source="flowchart TD\nFinding --> Risk --> NextStep\n",
                        caption="Risk map for the reviewed focus area.",
                        placement="inline",
                        evidence_bindings=bindings,
                        title="Risk Map",
                    ),
                ],
            ),
            Section("Unknowns", [TextBlock("Call out any remaining blind spots.")]),
            Section("Next Steps", [TextBlock("Recommend the next bounded workflow step.")]),
        ],
    )
