import unittest
from unittest.mock import patch
import subprocess

from repo_analysis_tools.doc_dsl.mermaid_validator import MermaidSyntaxError, MermaidValidator


class MermaidValidatorTest(unittest.TestCase):
    def test_valid_flowchart_normalizes_flowchart_v2_to_flowchart(self) -> None:
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

    def test_default_node_binary_prefers_path_resolution(self) -> None:
        with patch("repo_analysis_tools.doc_dsl.mermaid_validator.shutil.which", return_value="/usr/bin/node"):
            validator = MermaidValidator()

        self.assertEqual(validator.node_binary, "/usr/bin/node")

    def test_validate_raises_syntax_error_when_node_cannot_start(self) -> None:
        with patch(
            "repo_analysis_tools.doc_dsl.mermaid_validator.subprocess.run",
            side_effect=FileNotFoundError("node not found"),
        ):
            with self.assertRaises(MermaidSyntaxError) as context:
                MermaidValidator(node_binary="node").validate("flowchart LR\nA-->B\n", diagram_kind="flowchart")

        self.assertIn("could not start node process", str(context.exception))

    def test_validate_raises_syntax_error_when_node_start_fails_with_oserror(self) -> None:
        with patch(
            "repo_analysis_tools.doc_dsl.mermaid_validator.subprocess.run",
            side_effect=PermissionError("permission denied"),
        ):
            with self.assertRaises(MermaidSyntaxError) as context:
                MermaidValidator(node_binary="node").validate("flowchart LR\nA-->B\n", diagram_kind="flowchart")

        self.assertIn("could not start node process", str(context.exception))
        self.assertIn("permission denied", str(context.exception))

    def test_validate_raises_syntax_error_when_node_emits_invalid_json(self) -> None:
        with patch(
            "repo_analysis_tools.doc_dsl.mermaid_validator.subprocess.run",
            return_value=subprocess.CompletedProcess(
                args=["node"],
                returncode=0,
                stdout="not json",
                stderr="",
            ),
        ):
            with self.assertRaises(MermaidSyntaxError) as context:
                MermaidValidator(node_binary="node").validate("flowchart LR\nA-->B\n", diagram_kind="flowchart")

        self.assertIn("invalid validator response", str(context.exception))
