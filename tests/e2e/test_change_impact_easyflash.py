import tempfile
import unittest
from pathlib import Path

from repo_analysis_tools.mcp.tools.evidence_tools import build_evidence_pack, read_evidence_pack
from repo_analysis_tools.mcp.tools.impact_tools import impact_from_paths, summarize_impact
from repo_analysis_tools.mcp.tools.scan_tools import refresh_scan, scan_repo
from repo_analysis_tools.mcp.tools.slice_tools import inspect_slice, plan_slice
from tests.fixtures.easyflash_repo import materialize_easyflash_repo


class ChangeImpactEasyflashTest(unittest.TestCase):
    def test_easyflash_core_change_routes_through_real_demo_callers(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            repo = materialize_easyflash_repo(Path(tmpdir))

            scan_payload = scan_repo(str(repo))
            refresh_payload = refresh_scan(str(repo), scan_payload["data"]["scan_id"])
            impact_payload = impact_from_paths(
                str(repo),
                ["easyflash/src/easyflash.c"],
                refresh_payload["data"]["scan_id"],
            )
            summary_payload = summarize_impact(str(repo), impact_payload["data"]["impact_id"])
            plan_payload = plan_slice(str(repo), "Where is easyflash_init defined?")
            inspect_payload = inspect_slice(str(repo), plan_payload["data"]["slice_id"])
            build_payload = build_evidence_pack(str(repo), plan_payload["data"]["slice_id"])
            read_payload = read_evidence_pack(str(repo), build_payload["data"]["evidence_pack_id"])

            self.assertEqual(impact_payload["status"], "ok")
            self.assertEqual(impact_payload["data"]["changed_paths"], ["easyflash/src/easyflash.c"])
            self.assertIn(
                "demo/log/easylogger.c",
                {target["path"] for target in impact_payload["data"]["likely_propagation"]},
            )
            self.assertIn(
                "demo/env/stm32f10x/non_os/app/src/app.c",
                {target["path"] for target in impact_payload["data"]["likely_propagation"]},
            )
            self.assertIn(
                "demo/env/stm32f10x/rtt/app/src/app_task.c",
                {target["path"] for target in impact_payload["data"]["likely_propagation"]},
            )
            self.assertTrue(summary_payload["data"]["risks"])
            self.assertTrue(summary_payload["data"]["regression_focus"])
            self.assertIn(
                "demo/log/easylogger.c",
                "\n".join(summary_payload["data"]["regression_focus"]),
            )
            self.assertIn("easyflash/src/easyflash.c", plan_payload["data"]["selected_files"])
            self.assertEqual(plan_payload["data"]["selected_anchor_names"], ["easyflash_init"])
            self.assertIn("easyflash/src/easyflash.c", inspect_payload["data"]["members"])
            self.assertGreaterEqual(build_payload["data"]["citation_count"], 1)
            self.assertIn(
                "easyflash/src/easyflash.c",
                {citation["file_path"] for citation in read_payload["data"]["citations"]},
            )
