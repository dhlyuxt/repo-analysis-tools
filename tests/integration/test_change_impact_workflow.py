import tempfile
import unittest
from pathlib import Path

from repo_analysis_tools.mcp.tools.evidence_tools import build_evidence_pack, read_evidence_pack
from repo_analysis_tools.mcp.tools.impact_tools import impact_from_paths, summarize_impact
from repo_analysis_tools.mcp.tools.scan_tools import refresh_scan, scan_repo
from repo_analysis_tools.mcp.tools.slice_tools import plan_slice
from tests.fixtures.scope_first_repo import build_scope_first_repo


class ChangeImpactWorkflowTest(unittest.TestCase):
    def test_scope_first_change_impact_workflow_round_trip(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            repo = build_scope_first_repo(Path(tmpdir))

            scan_payload = scan_repo(str(repo))
            refresh_payload = refresh_scan(str(repo), scan_payload["data"]["scan_id"])
            impact_payload = impact_from_paths(
                str(repo),
                ["src/flash.c"],
                refresh_payload["data"]["scan_id"],
            )
            summary_payload = summarize_impact(str(repo), impact_payload["data"]["impact_id"])
            plan_payload = plan_slice(str(repo), "Where is flash_init defined?")
            build_payload = build_evidence_pack(str(repo), plan_payload["data"]["slice_id"])
            read_payload = read_evidence_pack(str(repo), build_payload["data"]["evidence_pack_id"])

            self.assertEqual(scan_payload["status"], "ok")
            self.assertEqual(refresh_payload["status"], "ok")
            self.assertNotEqual(refresh_payload["data"]["scan_id"], scan_payload["data"]["scan_id"])
            self.assertEqual(impact_payload["data"]["changed_paths"], ["src/flash.c"])
            self.assertEqual(impact_payload["data"]["scan_id"], refresh_payload["data"]["scan_id"])
            self.assertIn(
                "src/main.c",
                {target["path"] for target in impact_payload["data"]["likely_propagation"]},
            )
            self.assertIn(
                "demo/demo_main.c",
                {target["path"] for target in impact_payload["data"]["likely_propagation"]},
            )
            self.assertTrue(summary_payload["data"]["risks"])
            self.assertEqual(plan_payload["data"]["selected_files"], ["src/flash.c"])
            self.assertEqual(build_payload["data"]["citation_count"], 1)
            self.assertEqual(read_payload["data"]["citations"][0]["file_path"], "src/flash.c")
