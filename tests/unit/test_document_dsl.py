import unittest

from repo_analysis_tools.doc_dsl.builders import (
    build_design_note_document,
    build_issue_analysis_document,
    build_module_summary_document,
    build_reading_order_document,
    build_review_report_document,
)
from repo_analysis_tools.doc_dsl.models import (
    Document,
    EvidenceBinding,
    MermaidBlock,
    Section,
    TextBlock,
)
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
            {
                "module-summary",
                "issue-analysis",
                "design-note",
                "review-report",
                "repo-architecture",
                "module-map",
                "module-detail",
                "evidence-index",
                "reading-order",
            },
        )
        self.assertEqual(
            registry["design-note"].section_policies["Flow"].mermaid_policy,
            "required",
        )
        self.assertEqual(
            registry["module-detail"].section_policies["Internal Flow"].mermaid_policy,
            "required",
        )
        self.assertTrue(
            registry["repo-architecture"]
            .section_policies["Overview"]
            .requires_evidence_bindings
        )

    def test_validator_rejects_required_section_without_evidence_bound_blocks(self) -> None:
        document = Document(
            document_type="repo-architecture",
            title="Repo architecture",
            sections=[
                Section(title="Overview", blocks=[TextBlock(text="Architecture overview")]),
                Section(
                    title="System Boundaries",
                    blocks=[
                        TextBlock(
                            text="Boundaries",
                            evidence_bindings=[
                                EvidenceBinding(
                                    file_path="src/repo_analysis_tools/query/service.py",
                                    line_start=1,
                                    line_end=80,
                                )
                            ],
                        )
                    ],
                ),
                Section(
                    title="Runtime Flow",
                    blocks=[
                        MermaidBlock(
                            diagram_kind="flowchart",
                            source="flowchart TD\nA-->B",
                            caption="Runtime flow",
                            placement="inline",
                            evidence_bindings=[
                                EvidenceBinding(
                                    file_path="src/repo_analysis_tools/query/service.py",
                                    line_start=1,
                                    line_end=80,
                                )
                            ],
                        )
                    ],
                ),
                Section(
                    title="Constraints",
                    blocks=[
                        TextBlock(
                            text="Constraints",
                            evidence_bindings=[
                                EvidenceBinding(
                                    file_path="src/repo_analysis_tools/query/service.py",
                                    line_start=1,
                                    line_end=80,
                                )
                            ],
                        )
                    ],
                ),
                Section(title="Unknowns", blocks=[TextBlock(text="Unknowns")]),
            ],
        )

        errors = validate_document(
            document, build_document_spec_registry()["repo-architecture"]
        )

        self.assertIn("section 'Overview' requires evidence-bound blocks", errors)

    def test_validator_rejects_mixed_required_section_with_uncited_block(self) -> None:
        document = Document(
            document_type="repo-architecture",
            title="Repo architecture",
            sections=[
                Section(
                    title="Overview",
                    blocks=[
                        TextBlock(
                            text="Evidence-backed overview",
                            evidence_bindings=[
                                EvidenceBinding(
                                    file_path="src/repo_analysis_tools/query/service.py",
                                    line_start=1,
                                    line_end=80,
                                )
                            ],
                        ),
                        TextBlock(text="Uncited follow-up claim"),
                    ],
                ),
            ],
        )

        errors = validate_document(
            document, build_document_spec_registry()["repo-architecture"]
        )

        self.assertIn(
            "section 'Overview' requires every block to be evidence-bound", errors
        )

    def test_validator_rejects_required_mermaid_section_without_evidence_bound_mermaid(
        self,
    ) -> None:
        document = Document(
            document_type="repo-architecture",
            title="Repo architecture",
            sections=[
                Section(
                    title="Runtime Flow",
                    blocks=[
                        TextBlock(
                            text="Evidence-backed flow context",
                            evidence_bindings=[
                                EvidenceBinding(
                                    file_path="src/repo_analysis_tools/query/service.py",
                                    line_start=1,
                                    line_end=80,
                                )
                            ],
                        ),
                        MermaidBlock(
                            diagram_kind="flowchart",
                            source="flowchart TD\nA-->B",
                            caption="Runtime flow",
                            placement="inline",
                            evidence_bindings=[],
                        ),
                    ],
                ),
            ],
        )

        errors = validate_document(
            document, build_document_spec_registry()["repo-architecture"]
        )

        self.assertIn(
            "section 'Runtime Flow' requires an evidence-bound MermaidBlock", errors
        )

    def test_renderer_includes_text_block_evidence_binding_line_range(self) -> None:
        from repo_analysis_tools.renderers.markdown import MarkdownRenderer

        document = Document(
            document_type="repo-architecture",
            title="Repo architecture",
            sections=[
                Section(
                    title="Overview",
                    blocks=[
                        TextBlock(
                            text="Architecture overview",
                            evidence_bindings=[
                                EvidenceBinding(
                                    file_path="src/repo_analysis_tools/query/service.py",
                                    line_start=1,
                                    line_end=80,
                                )
                            ],
                            title="Evidence-backed overview",
                        )
                    ],
                )
            ],
        )

        rendered = MarkdownRenderer().render(document)

        self.assertIn("### Evidence-backed overview", rendered)
        self.assertIn("`src/repo_analysis_tools/query/service.py:1-80`", rendered)

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

    def test_build_reading_order_document_uses_controlled_sections(self) -> None:
        from tests.unit.test_repo_doc_writer_service import sample_payload
        from repo_analysis_tools.report.repo_design_models import RepositoryFindingsPackage

        package = RepositoryFindingsPackage.from_dict(sample_payload("/tmp/out"))

        document = build_reading_order_document(package)

        self.assertEqual("reading-order", document.document_type)
        self.assertEqual(
            [section.title for section in document.sections],
            ["Reading Order", "Source"],
        )
        errors = validate_document(document, build_document_spec_registry()["reading-order"])
        self.assertEqual([], errors)
