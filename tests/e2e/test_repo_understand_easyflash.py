import tempfile
import unittest
from pathlib import Path

from repo_analysis_tools.mcp.tools.anchors_tools import find_anchor
from repo_analysis_tools.mcp.tools.evidence_tools import build_evidence_pack, open_span, read_evidence_pack
from repo_analysis_tools.mcp.tools.scan_tools import scan_repo
from repo_analysis_tools.mcp.tools.scope_tools import show_scope
from repo_analysis_tools.mcp.tools.slice_tools import plan_slice
from tests.fixtures.easyflash_repo import materialize_easyflash_repo


class RepoUnderstandEasyflashTest(unittest.TestCase):
    def test_easyflash_mainline_traces_back_to_source_definition(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            repo = materialize_easyflash_repo(Path(tmpdir))

            scan_payload = scan_repo(str(repo))
            scope_payload = show_scope(str(repo), scan_payload["data"]["scan_id"])
            find_payload = find_anchor(str(repo), "easyflash_init", scan_payload["data"]["scan_id"])
            plan_payload = plan_slice(str(repo), "Where is easyflash_init defined?")
            build_payload = build_evidence_pack(str(repo), plan_payload["data"]["slice_id"])
            read_payload = read_evidence_pack(str(repo), build_payload["data"]["evidence_pack_id"])
            open_payload = open_span(
                str(repo),
                build_payload["data"]["evidence_pack_id"],
                "easyflash/src/easyflash.c",
                65,
                65,
            )

            self.assertRegex(scan_payload["data"]["scan_id"], r"^scan_[0-9a-f]{12}$")
            self.assertIn("primary", scope_payload["data"]["scope_summary"])
            self.assertEqual(find_payload["data"]["matches"][0]["path"], "easyflash/src/easyflash.c")
            self.assertEqual(read_payload["data"]["citations"][0]["file_path"], "easyflash/src/easyflash.c")
            self.assertIn("EfErrCode easyflash_init(void)", open_payload["data"]["lines"][0])
