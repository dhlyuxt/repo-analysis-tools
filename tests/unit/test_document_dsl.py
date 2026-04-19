import unittest

from repo_analysis_tools.doc_dsl.models import Document, MermaidBlock, Section, TextBlock
from repo_analysis_tools.doc_dsl.validators import validate_document
from repo_analysis_tools.doc_specs.base import build_document_spec_registry


class DocumentDslTest(unittest.TestCase):
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
            sections=(
                Section(title="Context", blocks=(TextBlock(text="Context"),)),
                Section(title="Flow", blocks=(TextBlock(text="Flow text only"),)),
            ),
        )

        errors = validate_document(document, build_document_spec_registry()["design-note"])

        self.assertIn("section 'Flow' requires at least one MermaidBlock", errors)

    def test_validator_rejects_mermaid_block_in_disallowed_section(self) -> None:
        document = Document(
            document_type="module-summary",
            title="Module summary",
            sections=(
                Section(
                    title="Recommendations",
                    blocks=(
                        MermaidBlock(
                            diagram_kind="flowchart",
                            source="flowchart TD\nA-->B",
                            caption="Bad placement",
                            placement="inline",
                            evidence_bindings=(),
                        ),
                    ),
                ),
            ),
        )

        errors = validate_document(document, build_document_spec_registry()["module-summary"])

        self.assertIn("section 'Recommendations' disallows MermaidBlock", errors)
