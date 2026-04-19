import tempfile
import unittest
from pathlib import Path

from repo_analysis_tools.mcp.tools.scan_tools import get_scan_status, scan_repo
from repo_analysis_tools.scan.service import ScanService
from repo_analysis_tools.scan.store import ScanStore
from tests.fixtures.scope_first_repo import build_scope_first_repo


class ScanServiceTest(unittest.TestCase):
    def test_scan_service_persists_latest_scan_summary(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            repo = build_scope_first_repo(Path(tmpdir))
            result = ScanService().scan(repo)
            stored = ScanStore.for_repo(repo).load_latest()

            self.assertEqual(stored.scan_id, result.scan_id)
            self.assertEqual(stored.file_count, 6)
            self.assertEqual(stored.repo_root, str(repo.resolve()))

    def test_scan_tools_return_real_payloads(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            repo = build_scope_first_repo(Path(tmpdir))
            created = scan_repo(str(repo))
            status = get_scan_status(str(repo))

            self.assertEqual(created["status"], "ok")
            self.assertRegex(created["data"]["scan_id"], r"^scan_[0-9a-f]{12}$")
            self.assertEqual(created["data"]["file_count"], 6)
            self.assertEqual(status["data"]["scan_id"], created["data"]["scan_id"])
