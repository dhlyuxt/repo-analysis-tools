import tempfile
import unittest
from pathlib import Path

from repo_analysis_tools.mcp.tools.anchors_tools import find_anchor
from repo_analysis_tools.mcp.tools.evidence_tools import build_evidence_pack, open_span, read_evidence_pack
from repo_analysis_tools.mcp.tools.scan_tools import scan_repo
from repo_analysis_tools.mcp.tools.scope_tools import show_scope
from repo_analysis_tools.mcp.tools.slice_tools import plan_slice
from tests.fixtures.scope_first_repo import build_scope_first_repo


class MainlineMcpWorkflowTest(unittest.TestCase):
    def test_scope_first_mainline_round_trip(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            repo = build_scope_first_repo(Path(tmpdir))

            scan_payload = scan_repo(str(repo))
            scope_payload = show_scope(str(repo), scan_payload["data"]["scan_id"])
            find_payload = find_anchor(str(repo), "flash_init", scan_payload["data"]["scan_id"])
            plan_payload = plan_slice(str(repo), "Where is flash_init defined?")
            build_payload = build_evidence_pack(str(repo), plan_payload["data"]["slice_id"])
            read_payload = read_evidence_pack(str(repo), build_payload["data"]["evidence_pack_id"])
            open_payload = open_span(
                str(repo),
                build_payload["data"]["evidence_pack_id"],
                "src/flash.c",
                1,
                1,
            )

            self.assertEqual(scan_payload["data"]["file_count"], 6)
            self.assertIn("primary", scope_payload["data"]["scope_summary"])
            self.assertEqual(find_payload["data"]["matches"][0]["path"], "src/flash.c")
            self.assertEqual(read_payload["data"]["citations"][0]["file_path"], "src/flash.c")
            self.assertIn("flash_init", open_payload["data"]["lines"][0])
