import tempfile
import unittest
from pathlib import Path
from unittest import mock

from repo_analysis_tools.anchors.store import AnchorStore
from repo_analysis_tools.anchors.service import AnchorService
from repo_analysis_tools.core.errors import ErrorCode
from repo_analysis_tools.mcp.scan_registry import repo_root_for_scan
from repo_analysis_tools.mcp.tools.scan_tools import rebuild_repo_snapshot
from repo_analysis_tools.scan.service import ScanService
from repo_analysis_tools.scan.store import ScanStore
from repo_analysis_tools.scope.store import ScopeStore
from repo_analysis_tools.scope.service import ScopeService
from tests.fixtures.git_helpers import init_git_fixture
from tests.fixtures.scope_first_repo import build_scope_first_repo


class ScanServiceTest(unittest.TestCase):
    def test_scan_service_counts_lines_without_text_decoding(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            repo = build_scope_first_repo(Path(tmpdir))

            with mock.patch.object(AnchorService, "build_snapshot", return_value=None), mock.patch.object(
                ScopeService, "build_snapshot", return_value=None
            ), mock.patch.object(Path, "read_text", side_effect=AssertionError("read_text should not be used")):
                snapshot = ScanService().scan(repo)

            by_path = {scanned_file.path: scanned_file for scanned_file in snapshot.files}
            self.assertEqual(by_path["src/main.c"].line_count, 3)

    def test_scan_service_builds_anchor_snapshot_before_scope_snapshot(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            repo = build_scope_first_repo(Path(tmpdir))

            result = ScanService().scan(repo)
            scope_snapshot = ScopeStore.for_repo(repo).load(result.scan_id)
            by_path = {scoped_file.path: scoped_file for scoped_file in scope_snapshot.files}

            self.assertEqual(by_path["src/flash.c"].incoming_call_count, 2)
            self.assertEqual(by_path["src/flash.c"].root_function_count, 0)
            self.assertEqual(by_path["src/config.h"].macro_count, 1)

    def test_scan_store_loads_old_format_scan_snapshot_without_line_count(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            repo = Path(tmpdir) / "scan-old-format-repo"
            store = ScanStore.for_repo(repo)
            scan_id = "scan_123456abcdef"
            store.assets.write_json(
                f"snapshots/{scan_id}.json",
                {
                    "scan_id": scan_id,
                    "repo_root": str(repo),
                    "file_count": 1,
                    "completed_at": "2026-04-20T00:00:00+00:00",
                    "git_head": None,
                    "workspace_dirty": None,
                    "files": [
                        {
                            "path": "src/main.c",
                            "content_sha256": "deadbeef",
                            "size_bytes": 3,
                        }
                    ],
                },
            )
            store.assets.write_json("latest.json", {"scan_id": scan_id})

            loaded = store.load()

            self.assertEqual(loaded.files[0].path, "src/main.c")
            self.assertEqual(loaded.files[0].line_count, 0)

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

    def test_rebuild_repo_snapshot_returns_real_payload_and_registers_repo_root(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            repo = build_scope_first_repo(Path(tmpdir))
            payload = rebuild_repo_snapshot(str(repo))

            self.assertEqual(payload["status"], "ok")
            self.assertEqual(payload["messages"], [])
            self.assertRegex(payload["data"]["scan_id"], r"^scan_[0-9a-f]{12}$")
            self.assertEqual(payload["data"]["file_count"], 6)
            self.assertGreater(payload["data"]["symbol_count"], 0)
            self.assertEqual(repo_root_for_scan(payload["data"]["scan_id"]), str(repo.resolve()))

    def test_rebuild_repo_snapshot_rejects_unknown_repo_path(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            repo = Path(tmpdir) / "missing-repo"

            payload = rebuild_repo_snapshot(str(repo))

            self.assertEqual(payload["status"], "error")
            self.assertEqual(payload["data"]["error"]["code"], ErrorCode.INVALID_INPUT.value)

    def test_rebuild_repo_snapshot_rejects_non_directory_repo_path(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            repo = Path(tmpdir) / "repo.txt"
            repo.write_text("not a directory", encoding="utf-8")

            payload = rebuild_repo_snapshot(str(repo))

            self.assertEqual(payload["status"], "error")
            self.assertEqual(payload["data"]["error"]["code"], ErrorCode.INVALID_INPUT.value)

    def test_scan_service_marks_workspace_dirty_for_untracked_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            repo = build_scope_first_repo(Path(tmpdir))
            init_git_fixture(repo)
            (repo / "notes.txt").write_text("untracked\n", encoding="utf-8")

            snapshot = ScanService().scan(repo)

            self.assertTrue(snapshot.workspace_dirty)
