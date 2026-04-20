import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
README = ROOT / "README.md"
LAUNCH_DOC = ROOT / "docs" / "self-use-launch.md"


class LaunchDocsTest(unittest.TestCase):
    def read_text(self, path: Path) -> str:
        self.assertTrue(path.exists(), f"missing documentation file: {path.relative_to(ROOT)}")
        return path.read_text(encoding="utf-8")

    def test_readme_contains_codex_first_launch_strings(self) -> None:
        text = self.read_text(README)

        for needle in (
            "query-first MCP surface",
            ".codex/config.toml",
            ".mcp.json",
            "repo_analysis_tools.mcp.server",
            "rebuild_repo_snapshot",
            "list_priority_files",
            "get_file_info",
            "list_file_symbols",
            "resolve_symbols",
            "open_symbol_context",
            "query_call_relations",
            "find_root_functions",
            "find_call_paths",
            "/home/hyx/anaconda3/envs/agent/bin/python tools/run_self_use_demo.py",
        ):
            self.assertIn(needle, text)
        for needle in (
            "scan_repo",
            "build_evidence_pack",
            "summarize_impact",
            "render_module_summary",
            "export_analysis_bundle",
            "refresh_scan",
        ):
            self.assertNotIn(needle, text)

    def test_launch_doc_contains_daily_use_workflow_strings(self) -> None:
        text = self.read_text(LAUNCH_DOC)

        for needle in (
            "rebuild_repo_snapshot",
            "list_priority_files",
            "get_file_info",
            "list_file_symbols",
            "resolve_symbols",
            "open_symbol_context",
            "query_call_relations",
            "find_root_functions",
            "find_call_paths",
        ):
            self.assertIn(needle, text)
        for needle in (
            "scan_repo",
            "build_evidence_pack",
            "summarize_impact",
            "render_module_summary",
            "export_analysis_bundle",
            "refresh_scan",
        ):
            self.assertNotIn(needle, text)
