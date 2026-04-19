import tempfile
import unittest
from pathlib import Path

from repo_analysis_tools.core.errors import ErrorCode
from repo_analysis_tools.mcp.tools.scope_tools import explain_scope_node, list_scope_nodes, show_scope
from repo_analysis_tools.scan.service import ScanService
from repo_analysis_tools.scope.service import ScopeService
from repo_analysis_tools.scope.store import ScopeStore
from tests.fixtures.scope_first_repo import build_scope_first_repo


class ScopeServiceTest(unittest.TestCase):
    def test_build_snapshot_classifies_expected_roles_and_persists_snapshot(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            repo = build_scope_first_repo(Path(tmpdir))
            scan_snapshot = ScanService().scan(repo)

            snapshot = ScopeService().build_snapshot(repo, scan_snapshot.scan_id)
            stored = ScopeStore.for_repo(repo).load(scan_snapshot.scan_id)

            self.assertEqual(snapshot.scan_id, scan_snapshot.scan_id)
            self.assertEqual(
                {scoped_file.path: scoped_file.role for scoped_file in snapshot.files},
                {
                    "demo/demo_main.c": "external",
                    "generated/autoconf.h": "generated",
                    "ports/board_port.c": "support",
                    "src/config.h": "primary",
                    "src/flash.c": "primary",
                    "src/main.c": "primary",
                },
            )
            self.assertEqual(
                snapshot.role_counts,
                {"external": 1, "generated": 1, "primary": 3, "support": 1},
            )
            self.assertEqual(
                [(node.node_id, node.label, node.role, node.file_count) for node in snapshot.nodes],
                [
                    ("scope_demo", "demo", "external", 1),
                    ("scope_generated", "generated", "generated", 1),
                    ("scope_ports", "ports", "support", 1),
                    ("scope_src", "src", "primary", 3),
                ],
            )
            self.assertEqual(stored.role_counts, snapshot.role_counts)

    def test_scan_service_also_builds_scope_snapshot(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            repo = build_scope_first_repo(Path(tmpdir))

            scan_snapshot = ScanService().scan(repo)
            scope_snapshot = ScopeStore.for_repo(repo).load(scan_snapshot.scan_id)

            self.assertEqual(scope_snapshot.scan_id, scan_snapshot.scan_id)
            self.assertEqual(scope_snapshot.role_counts["primary"], 3)

    def test_scope_tools_return_real_payloads(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            repo = build_scope_first_repo(Path(tmpdir))
            scan_snapshot = ScanService().scan(repo)

            scope_payload = show_scope(str(repo))
            nodes_payload = list_scope_nodes(str(repo), scan_snapshot.scan_id)
            explain_payload = explain_scope_node(str(repo), "scope_src", scan_snapshot.scan_id)

            self.assertEqual(scope_payload["status"], "ok")
            self.assertEqual(scope_payload["data"]["scan_id"], scan_snapshot.scan_id)
            self.assertEqual(
                scope_payload["data"]["role_counts"],
                {"external": 1, "generated": 1, "primary": 3, "support": 1},
            )
            self.assertEqual(
                scope_payload["data"]["scope_summary"],
                "4 scope nodes cover 6 files across primary, support, external, and generated roles.",
            )
            self.assertEqual(
                nodes_payload["data"]["nodes"],
                [
                    {"file_count": 1, "label": "demo", "node_id": "scope_demo", "role": "external"},
                    {"file_count": 1, "label": "generated", "node_id": "scope_generated", "role": "generated"},
                    {"file_count": 1, "label": "ports", "node_id": "scope_ports", "role": "support"},
                    {"file_count": 3, "label": "src", "node_id": "scope_src", "role": "primary"},
                ],
            )
            self.assertEqual(explain_payload["data"]["node_id"], "scope_src")
            self.assertEqual(explain_payload["data"]["summary"], "src is a primary scope node with 3 related files.")
            self.assertEqual(
                explain_payload["data"]["related_files"],
                ["src/config.h", "src/flash.c", "src/main.c"],
            )

    def test_explain_scope_node_returns_not_found_for_unknown_node(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            repo = build_scope_first_repo(Path(tmpdir))
            scan_snapshot = ScanService().scan(repo)

            payload = explain_scope_node(str(repo), "scope_missing", scan_snapshot.scan_id)

            self.assertEqual(payload["status"], "error")
            self.assertEqual(payload["data"]["error"]["code"], ErrorCode.NOT_FOUND.value)
