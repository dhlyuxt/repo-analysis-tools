import tempfile
import unittest
from pathlib import Path

from repo_analysis_tools.mcp.tools.evidence_tools import build_evidence_pack
from repo_analysis_tools.mcp.tools.report_tools import render_module_summary
from repo_analysis_tools.mcp.tools.scan_tools import scan_repo
from repo_analysis_tools.mcp.tools.slice_tools import plan_slice
from tests.fixtures.easyflash_repo import materialize_easyflash_repo


class AnalysisWritingEasyflashTest(unittest.TestCase):
    def test_easyflash_module_summary_contains_mermaid_diagram(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            repo = materialize_easyflash_repo(Path(tmpdir))

            scan_repo(str(repo))
            plan_payload = plan_slice(str(repo), "Where is easyflash_init defined?")
            evidence_payload = build_evidence_pack(str(repo), plan_payload["data"]["slice_id"])
            payload = render_module_summary(
                str(repo),
                evidence_payload["data"]["evidence_pack_id"],
                "easyflash",
            )
            markdown = Path(payload["data"]["markdown_path"]).read_text(encoding="utf-8")

            self.assertIn("```mermaid", markdown)
            self.assertIn("easyflash_init", markdown)
