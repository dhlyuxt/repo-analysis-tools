import tempfile
import unittest
from pathlib import Path

from repo_analysis_tools.core.errors import ErrorCode
from repo_analysis_tools.mcp.tools.scope_tools import explain_scope_node, list_scope_nodes, show_scope
from repo_analysis_tools.scan.service import ScanService
from repo_analysis_tools.scope.service import ScopeService
from repo_analysis_tools.scope.store import ScopeStore
from tests.fixtures.scope_first_repo import build_scope_first_repo


def build_scope_edge_case_repo(tmp_path: Path) -> Path:
    repo = tmp_path / "scope-edge-case-repo"
    (repo / "support").mkdir(parents=True, exist_ok=True)
    (repo / "src").mkdir(parents=True, exist_ok=True)
    (repo / "tests").mkdir(parents=True, exist_ok=True)
    (repo / "src" / "tests").mkdir(parents=True, exist_ok=True)
    (repo / "third-party").mkdir(parents=True, exist_ok=True)
    (repo / "third_party").mkdir(parents=True, exist_ok=True)

    (repo / "main.c").write_text("int main(void) { return 0; }\n", encoding="utf-8")
    (repo / "config.h").write_text("#define ROOT_CONFIG 1\n", encoding="utf-8")
    (repo / "support" / "helper.c").write_text("int support_helper(void) { return 1; }\n", encoding="utf-8")
    (repo / "src" / "app.c").write_text("int app(void) { return 0; }\n", encoding="utf-8")
    (repo / "tests" / "root_test.c").write_text("int root_test(void) { return 0; }\n", encoding="utf-8")
    (repo / "src" / "tests" / "nested_test.c").write_text("int nested_test(void) { return 0; }\n", encoding="utf-8")
    (repo / "third-party" / "demo.c").write_text("int third_party_dash(void) { return 0; }\n", encoding="utf-8")
    (repo / "third_party" / "demo.c").write_text("int third_party_underscore(void) { return 0; }\n", encoding="utf-8")
    return repo


class ScopeServiceTest(unittest.TestCase):
    def test_build_snapshot_persists_enriched_file_facts(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            repo = build_scope_first_repo(Path(tmpdir))
            scan_snapshot = ScanService().scan(repo)

            snapshot = ScopeService().build_snapshot(repo, scan_snapshot.scan_id)
            stored = ScopeStore.for_repo(repo).load(scan_snapshot.scan_id)
            by_path = {scoped_file.path: scoped_file for scoped_file in snapshot.files}
            stored_by_path = {scoped_file.path: scoped_file for scoped_file in stored.files}

            self.assertEqual(by_path["src/main.c"].role, "primary")
            self.assertTrue(by_path["src/main.c"].has_main_definition)
            self.assertEqual(by_path["src/main.c"].line_count, 3)
            self.assertEqual(by_path["src/main.c"].symbol_count, 2)
            self.assertEqual(by_path["src/main.c"].function_count, 2)
            self.assertEqual(by_path["src/main.c"].include_count, 1)
            self.assertEqual(by_path["src/main.c"].incoming_call_count, 0)
            self.assertEqual(by_path["src/main.c"].outgoing_call_count, 1)
            self.assertEqual(by_path["src/main.c"].root_function_count, 1)
            self.assertEqual(by_path["src/main.c"].priority_score, 110)
            self.assertEqual(by_path["src/flash.c"].priority_score, 44)
            self.assertEqual(by_path["demo/demo_main.c"].priority_score, 25)
            self.assertGreater(by_path["src/main.c"].priority_score, by_path["src/flash.c"].priority_score)
            self.assertGreater(by_path["src/flash.c"].priority_score, by_path["demo/demo_main.c"].priority_score)
            self.assertEqual(by_path["src/flash.c"].incoming_call_count, 2)
            self.assertEqual(by_path["src/flash.c"].root_function_count, 0)
            self.assertEqual(by_path["src/config.h"].macro_count, 1)

            self.assertEqual(stored_by_path["src/main.c"].line_count, 3)
            self.assertTrue(stored_by_path["src/main.c"].has_main_definition)
            self.assertEqual(stored_by_path["src/main.c"].symbol_count, 2)
            self.assertEqual(stored_by_path["src/main.c"].function_count, 2)
            self.assertEqual(stored_by_path["src/main.c"].incoming_call_count, 0)
            self.assertEqual(stored_by_path["src/main.c"].outgoing_call_count, 1)
            self.assertEqual(stored_by_path["src/main.c"].root_function_count, 1)
            self.assertEqual(stored_by_path["src/main.c"].priority_score, 110)
            self.assertEqual(stored_by_path["src/flash.c"].priority_score, 44)
            self.assertEqual(stored_by_path["src/flash.c"].incoming_call_count, 2)
            self.assertEqual(stored_by_path["src/flash.c"].root_function_count, 0)
            self.assertEqual(stored_by_path["src/config.h"].macro_count, 1)

    def test_scope_store_loads_old_format_scope_snapshot_without_enriched_fields(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            repo = Path(tmpdir) / "scope-old-format-repo"
            store = ScopeStore.for_repo(repo)
            scan_id = "scan_abcdef123456"
            store.assets.write_json(
                f"snapshots/{scan_id}.json",
                {
                    "scan_id": scan_id,
                    "repo_root": str(repo),
                    "scope_summary": "1 scope node covers 1 files across primary roles.",
                    "role_counts": {"primary": 1},
                    "nodes": [
                        {
                            "node_id": "scope_src",
                            "label": "src",
                            "role": "primary",
                            "file_count": 1,
                            "related_files": ["src/main.c"],
                        }
                    ],
                    "files": [
                        {
                            "path": "src/main.c",
                            "role": "primary",
                            "node_id": "scope_src",
                        }
                    ],
                },
            )
            store.assets.write_json("latest.json", {"scan_id": scan_id})

            loaded = store.load()

            self.assertEqual(loaded.files[0].path, "src/main.c")
            self.assertEqual(loaded.files[0].priority_score, 0)
            self.assertEqual(loaded.files[0].line_count, 0)
            self.assertEqual(loaded.files[0].symbol_count, 0)
            self.assertFalse(loaded.files[0].has_main_definition)

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

    def test_build_snapshot_includes_root_level_c_and_h_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            repo = build_scope_edge_case_repo(Path(tmpdir))
            scan_snapshot = ScanService().scan(repo)

            snapshot = ScopeService().build_snapshot(repo, scan_snapshot.scan_id)

            self.assertIn("main.c", {scoped_file.path for scoped_file in snapshot.files})
            self.assertIn("config.h", {scoped_file.path for scoped_file in snapshot.files})
            self.assertEqual(
                {scoped_file.path: scoped_file.role for scoped_file in snapshot.files if scoped_file.path in {"main.c", "config.h"}},
                {"main.c": "primary", "config.h": "primary"},
            )

    def test_build_snapshot_classifies_support_directory_as_support(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            repo = build_scope_edge_case_repo(Path(tmpdir))
            scan_snapshot = ScanService().scan(repo)

            snapshot = ScopeService().build_snapshot(repo, scan_snapshot.scan_id)

            self.assertEqual(
                {scoped_file.path: scoped_file.role for scoped_file in snapshot.files if scoped_file.path == "support/helper.c"},
                {"support/helper.c": "support"},
            )

    def test_build_snapshot_excludes_root_and_nested_tests_directories(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            repo = build_scope_edge_case_repo(Path(tmpdir))
            scan_snapshot = ScanService().scan(repo)

            snapshot = ScopeService().build_snapshot(repo, scan_snapshot.scan_id)

            self.assertNotIn("tests/root_test.c", {scoped_file.path for scoped_file in snapshot.files})
            self.assertNotIn("src/tests/nested_test.c", {scoped_file.path for scoped_file in snapshot.files})

    def test_build_snapshot_keeps_distinct_node_ids_for_common_separator_variants(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            repo = build_scope_edge_case_repo(Path(tmpdir))
            scan_snapshot = ScanService().scan(repo)

            snapshot = ScopeService().build_snapshot(repo, scan_snapshot.scan_id)
            node_ids = {
                node.label: node.node_id
                for node in snapshot.nodes
                if node.label in {"third-party", "third_party"}
            }

            self.assertEqual(set(node_ids), {"third-party", "third_party"})
            self.assertNotEqual(node_ids["third-party"], node_ids["third_party"])
            self.assertEqual(
                {
                    node.label: node.related_files
                    for node in snapshot.nodes
                    if node.label in {"third-party", "third_party"}
                },
                {
                    "third-party": ["third-party/demo.c"],
                    "third_party": ["third_party/demo.c"],
                },
            )
