import tempfile
import unittest
from pathlib import Path

from repo_analysis_tools.mcp.tools.anchors_tools import find_anchor
from repo_analysis_tools.mcp.tools.evidence_tools import build_evidence_pack, open_span
from repo_analysis_tools.mcp.tools.export_tools import export_analysis_bundle
from repo_analysis_tools.mcp.tools.impact_tools import impact_from_paths, summarize_impact
from repo_analysis_tools.mcp.tools.report_tools import render_module_summary
from repo_analysis_tools.mcp.tools.scan_tools import refresh_scan, scan_repo
from repo_analysis_tools.mcp.tools.slice_tools import plan_slice
from tests.fixtures.easyflash_repo import materialize_easyflash_repo


class SelfUseLaunchEasyflashTest(unittest.TestCase):
    def test_easyflash_launch_flow_reaches_exported_markdown(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            repo = materialize_easyflash_repo(Path(tmpdir))

            scan_payload = scan_repo(str(repo))
            refresh_payload = refresh_scan(str(repo), scan_payload["data"]["scan_id"])
            find_payload = find_anchor(str(repo), "easyflash_init", refresh_payload["data"]["scan_id"])
            plan_payload = plan_slice(str(repo), "Where is easyflash_init defined?")
            build_payload = build_evidence_pack(str(repo), plan_payload["data"]["slice_id"])
            open_payload = open_span(
                str(repo),
                build_payload["data"]["evidence_pack_id"],
                "easyflash/src/easyflash.c",
                65,
                65,
            )
            impact_payload = impact_from_paths(
                str(repo),
                ["easyflash/src/easyflash.c"],
                refresh_payload["data"]["scan_id"],
            )
            summary_payload = summarize_impact(str(repo), impact_payload["data"]["impact_id"])
            report_payload = render_module_summary(
                str(repo),
                build_payload["data"]["evidence_pack_id"],
                "easyflash",
            )
            export_payload = export_analysis_bundle(str(repo), report_payload["data"]["report_id"])

            report_markdown = Path(report_payload["data"]["markdown_path"])
            copied_markdown = Path(export_payload["data"]["copied_markdown_path"])

            self.assertEqual(refresh_payload["status"], "ok")
            self.assertNotEqual(refresh_payload["data"]["scan_id"], scan_payload["data"]["scan_id"])
            self.assertEqual(find_payload["data"]["matches"][0]["path"], "easyflash/src/easyflash.c")
            self.assertGreaterEqual(build_payload["data"]["citation_count"], 1)
            self.assertEqual(open_payload["status"], "ok")
            self.assertIn("easyflash_init", open_payload["data"]["lines"][0])
            self.assertEqual(impact_payload["status"], "ok")
            self.assertTrue(summary_payload["data"]["regression_focus"])
            self.assertTrue(report_markdown.is_file())
            self.assertIn("# Module Summary: easyflash", report_markdown.read_text(encoding="utf-8"))
            self.assertEqual(export_payload["status"], "ok")
            self.assertTrue(copied_markdown.is_file())
            self.assertIn("# Module Summary: easyflash", copied_markdown.read_text(encoding="utf-8"))
