import tempfile
import unittest
from pathlib import Path

from repo_analysis_tools.anchors.store import AnchorStore
from repo_analysis_tools.core.errors import ErrorCode
from repo_analysis_tools.mcp.tools.scan_tools import get_scan_status, refresh_scan, scan_repo
from repo_analysis_tools.scan.service import ScanService
from repo_analysis_tools.scan.store import ScanStore
from tests.fixtures.git_helpers import init_git_fixture
from tests.fixtures.scope_first_repo import build_scope_first_repo


class ScanServiceTest(unittest.TestCase):
    def test_scan_service_builds_anchor_snapshot_before_scope_snapshot(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            repo = build_scope_first_repo(Path(tmpdir))

            result = ScanService().scan(repo)
            scope_snapshot = ScopeStore.for_repo(repo).load(result.scan_id)
            by_path = {scoped_file.path: scoped_file for scoped_file in scope_snapshot.files}

            self.assertEqual(by_path["src/flash.c"].incoming_call_count, 2)
            self.assertEqual(by_path["src/flash.c"].root_function_count, 0)
            self.assertEqual(by_path["src/config.h"].macro_count, 1)

    def test_scan_service_persists_latest_scan_summary(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            repo = build_scope_first_repo(Path(tmpdir))
            result = ScanService().scan(repo)
            stored = ScanStore.for_repo(repo).load_latest()

            self.assertEqual(stored.scan_id, result.scan_id)
            self.assertEqual(stored.file_count, 6)
            self.assertEqual(stored.repo_root, str(repo.resolve()))

    def test_scan_service_persists_anchor_snapshot(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            repo = build_scope_first_repo(Path(tmpdir))

            result = ScanService().scan(repo)
            stored = AnchorStore.for_repo(repo).load(result.scan_id)

            self.assertEqual(stored.scan_id, result.scan_id)
            self.assertIn("main", {anchor.name for anchor in stored.anchors})

    def test_scan_tools_return_real_payloads(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            repo = build_scope_first_repo(Path(tmpdir))
            created = scan_repo(str(repo))
            status = get_scan_status(str(repo))

            self.assertEqual(created["status"], "ok")
            self.assertRegex(created["data"]["scan_id"], r"^scan_[0-9a-f]{12}$")
            self.assertEqual(created["data"]["file_count"], 6)
            self.assertEqual(status["data"]["scan_id"], created["data"]["scan_id"])

    def test_refresh_scan_rejects_unknown_scan_id(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            repo = build_scope_first_repo(Path(tmpdir))

            payload = refresh_scan(str(repo), "scan_deadbeefcafe")

            self.assertEqual(payload["status"], "error")
            self.assertEqual(payload["data"]["error"]["code"], ErrorCode.NOT_FOUND.value)

    def test_refresh_scan_rescans_when_scan_id_exists(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            repo = build_scope_first_repo(Path(tmpdir))
            created = scan_repo(str(repo))

            refreshed = refresh_scan(str(repo), created["data"]["scan_id"])
            status = get_scan_status(str(repo))

            self.assertEqual(refreshed["status"], "ok")
            self.assertNotEqual(refreshed["data"]["scan_id"], created["data"]["scan_id"])
            self.assertEqual(status["data"]["scan_id"], refreshed["data"]["scan_id"])

    def test_refresh_scan_rejects_malformed_scan_id(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            repo = build_scope_first_repo(Path(tmpdir))

            payload = refresh_scan(str(repo), "../escape")

            self.assertEqual(payload["status"], "error")
            self.assertEqual(payload["data"]["error"]["code"], ErrorCode.INVALID_INPUT.value)

    def test_get_scan_status_rejects_malformed_scan_id(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            repo = build_scope_first_repo(Path(tmpdir))

            payload = get_scan_status(str(repo), "../escape")

            self.assertEqual(payload["status"], "error")
            self.assertEqual(payload["data"]["error"]["code"], ErrorCode.INVALID_INPUT.value)

    def test_get_scan_status_returns_not_found_when_repo_has_no_scans(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            repo = build_scope_first_repo(Path(tmpdir))

            payload = get_scan_status(str(repo))

            self.assertEqual(payload["status"], "error")
            self.assertEqual(payload["data"]["error"]["code"], ErrorCode.NOT_FOUND.value)

    def test_get_scan_status_returns_not_found_for_missing_scan_id(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            repo = build_scope_first_repo(Path(tmpdir))
            scan_repo(str(repo))

            payload = get_scan_status(str(repo), "scan_deadbeefcafe")

            self.assertEqual(payload["status"], "error")
            self.assertEqual(payload["data"]["error"]["code"], ErrorCode.NOT_FOUND.value)

    def test_scan_service_marks_workspace_dirty_for_untracked_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            repo = build_scope_first_repo(Path(tmpdir))
            init_git_fixture(repo)
            (repo / "notes.txt").write_text("untracked\n", encoding="utf-8")

            snapshot = ScanService().scan(repo)

            self.assertTrue(snapshot.workspace_dirty)
