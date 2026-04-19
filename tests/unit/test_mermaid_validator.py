import unittest

from repo_analysis_tools.doc_dsl.mermaid_validator import MermaidSyntaxError, validate_mermaid


class MermaidValidatorTest(unittest.TestCase):
    def test_valid_flowchart_returns_diagram_type(self) -> None:
        result = validate_mermaid("flowchart TD\n    A-->B\n")

        self.assertEqual(result.diagram_type, "flowchart")

    def test_invalid_diagram_raises_syntax_error(self) -> None:
        with self.assertRaisesRegex(MermaidSyntaxError, "Mermaid syntax error"):
            validate_mermaid("flowchart TD\n    A-->\n")
