import unittest

from repo_analysis_tools.doc_dsl.builders import (
    build_design_note_document,
    build_issue_analysis_document,
    build_module_summary_document,
    build_review_report_document,
)
from repo_analysis_tools.doc_dsl.models import Document, MermaidBlock, Section, TextBlock
from repo_analysis_tools.doc_dsl.validators import validate_document
from repo_analysis_tools.doc_specs.base import build_document_spec_registry
from repo_analysis_tools.evidence.models import CitationRecord, EvidencePack


class DocumentDslTest(unittest.TestCase):
    def sample_evidence_pack(self) -> EvidencePack:
        return EvidencePack(
            evidence_pack_id="evidence_pack_123456789abc",
            slice_id="slice_123456789abc",
            scan_id="scan_123456789abc",
            repo_root="/tmp/demo-repo",
            summary="Evidence summary",
            citations=[
                CitationRecord("src/module.c", "module_init", "function", 10, 20),
                CitationRecord("src/caller.c", "main", "function", 30, 40),
                CitationRecord("include/module.h", "module_init", "declaration", 5, 8),
                CitationRecord("src/ignored.c", "ignored", "function", 50, 60),
            ],
        )

    def test_registry_exposes_all_m4_document_types(self) -> None:
        registry = build_document_spec_registry()

        self.assertEqual(
            set(registry),
            {"module-summary", "issue-analysis", "design-note", "review-report"},
        )
        self.assertEqual(
            registry["design-note"].section_policies["Flow"].mermaid_policy,
            "required",
        )

    def test_validator_rejects_missing_required_mermaid_block(self) -> None:
        document = Document(
            document_type="design-note",
            title="Design note",
            sections=[
                Section(title="Context", blocks=[TextBlock(text="Context")]),
                Section(title="Flow", blocks=[TextBlock(text="Flow text only")]),
            ],
        )

        errors = validate_document(document, build_document_spec_registry()["design-note"])

        self.assertIn("section 'Flow' requires at least one MermaidBlock", errors)

    def test_validator_rejects_mermaid_block_in_disallowed_section(self) -> None:
        document = Document(
            document_type="module-summary",
            title="Module summary",
            sections=[
                Section(
                    title="Recommendations",
                    blocks=[
                        MermaidBlock(
                            diagram_kind="flowchart",
                            source="flowchart TD\nA-->B",
                            caption="Bad placement",
                            placement="inline",
                            evidence_bindings=[],
                        ),
                    ],
                ),
            ],
        )

        errors = validate_document(document, build_document_spec_registry()["module-summary"])

        self.assertIn("section 'Recommendations' disallows MermaidBlock", errors)

    def test_build_module_summary_document_matches_planned_sections_and_mermaid_block(self) -> None:
        document = build_module_summary_document(self.sample_evidence_pack(), "flash")

        self.assertIsInstance(document.sections, list)
        self.assertEqual(
            [section.title for section in document.sections],
            ["Summary", "Key Anchors", "Call Flow", "Risks", "Recommendations"],
        )
        self.assertIsInstance(document.sections[2].blocks, list)
        mermaid_block = document.sections[2].blocks[0]
        self.assertIsInstance(mermaid_block, MermaidBlock)
        self.assertEqual(mermaid_block.title, "Module Flow")
        self.assertEqual(
            mermaid_block.caption,
            "High-level module flow derived from the selected evidence.",
        )
        self.assertEqual(
            mermaid_block.source,
            "flowchart LR\nQuestion --> Evidence --> Module\n",
        )
        self.assertIsInstance(mermaid_block.evidence_bindings, list)
        self.assertEqual(len(mermaid_block.evidence_bindings), 3)

    def test_build_design_note_document_matches_planned_sections_and_mermaid_block(self) -> None:
        document = build_design_note_document("Render reports")

        self.assertIsInstance(document.sections, list)
        self.assertEqual(
            [section.title for section in document.sections],
            ["Context", "Proposed Design", "Flow", "Tradeoffs", "Open Questions"],
        )
        mermaid_block = document.sections[2].blocks[0]
        self.assertEqual(mermaid_block.title, "Proposed Flow")
        self.assertEqual(mermaid_block.caption, "Proposed flow for the design note.")
        self.assertEqual(
            mermaid_block.source,
            "flowchart LR\nInput --> Decision --> Output\n",
        )
        self.assertEqual(mermaid_block.evidence_bindings, [])

    def test_build_issue_analysis_document_matches_planned_causal_chain_block(self) -> None:
        document = build_issue_analysis_document(self.sample_evidence_pack(), "Flash init fails")

        self.assertEqual(
            [section.title for section in document.sections],
            ["Issue Summary", "Evidence", "Causal Chain", "Unknowns", "Recommendations"],
        )
        mermaid_block = document.sections[2].blocks[0]
        self.assertEqual(
            mermaid_block.source,
            "flowchart TD\nSymptom --> Evidence --> SuspectedCause\n",
        )
        self.assertEqual(mermaid_block.title, "Causal Chain")

    def test_build_review_report_document_matches_planned_risk_map_block(self) -> None:
        document = build_review_report_document(self.sample_evidence_pack(), "Review report")

        self.assertEqual(
            [section.title for section in document.sections],
            ["Scope", "Findings", "Risk Map", "Unknowns", "Next Steps"],
        )
        mermaid_block = document.sections[2].blocks[0]
        self.assertEqual(
            mermaid_block.source,
            "flowchart TD\nFinding --> Risk --> NextStep\n",
        )
        self.assertEqual(mermaid_block.title, "Risk Map")
