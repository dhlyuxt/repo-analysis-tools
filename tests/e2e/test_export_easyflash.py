import json
import tempfile
import unittest
from pathlib import Path

from repo_analysis_tools.mcp.tools.evidence_tools import build_evidence_pack
from repo_analysis_tools.mcp.tools.export_tools import export_analysis_bundle
from repo_analysis_tools.mcp.tools.report_tools import render_module_summary
from repo_analysis_tools.mcp.tools.scan_tools import scan_repo
from repo_analysis_tools.mcp.tools.slice_tools import plan_slice
from tests.fixtures.easyflash_repo import materialize_easyflash_repo


class ExportEasyflashTest(unittest.TestCase):
    def test_easyflash_module_summary_exports_copied_markdown_artifact(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            repo = materialize_easyflash_repo(Path(tmpdir))

            scan_repo(str(repo))
            plan_payload = plan_slice(str(repo), "Where is easyflash_init defined?")
            evidence_payload = build_evidence_pack(str(repo), plan_payload["data"]["slice_id"])
            report_payload = render_module_summary(
                str(repo),
                evidence_payload["data"]["evidence_pack_id"],
                "easyflash",
            )
            export_payload = export_analysis_bundle(str(repo), report_payload["data"]["report_id"])

            manifest_path = Path(export_payload["data"]["manifest_path"])
            copied_markdown_path = Path(export_payload["data"]["copied_markdown_path"])
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            markdown = copied_markdown_path.read_text(encoding="utf-8")

            self.assertEqual(export_payload["status"], "ok")
            self.assertEqual(export_payload["data"]["export_kind"], "analysis-bundle")
            self.assertEqual(manifest["paths"]["copied_markdown_path"], str(copied_markdown_path))
            self.assertEqual(manifest["paths"]["copied_markdown_path"], export_payload["data"]["copied_markdown_path"])
            self.assertTrue(copied_markdown_path.is_file())
            self.assertIn("# Module Summary: easyflash", markdown)
            self.assertIn("```mermaid", markdown)
