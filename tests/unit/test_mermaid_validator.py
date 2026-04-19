import unittest

from repo_analysis_tools.doc_dsl.mermaid_validator import MermaidSyntaxError, MermaidValidator


class MermaidValidatorTest(unittest.TestCase):
    def test_valid_flowchart_returns_diagram_type(self) -> None:
        result = MermaidValidator().validate(
            "flowchart LR\nA[Scan] --> B[Render]\n",
            diagram_kind="flowchart",
        )

        self.assertEqual(result.diagram_type, "flowchart")

    def test_invalid_diagram_raises_syntax_error(self) -> None:
        with self.assertRaises(MermaidSyntaxError) as context:
            MermaidValidator().validate(
                "flowchart LR\nA[Scan] -->\n",
                diagram_kind="flowchart",
            )

        self.assertIn("Mermaid syntax error", str(context.exception))
