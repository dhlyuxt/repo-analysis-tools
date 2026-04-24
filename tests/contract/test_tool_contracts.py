import inspect
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from repo_analysis_tools.mcp.contracts import CONTRACT_BY_NAME, DOMAIN_CONTRACTS
from repo_analysis_tools.mcp.tools import query_tools, scan_tools
from repo_analysis_tools.mcp.tools.query_tools import (
    find_call_paths,
    find_root_functions,
    get_file_info,
    list_file_symbols,
    list_priority_files,
    open_symbol_context,
    query_call_relations,
    resolve_symbols,
)
from repo_analysis_tools.mcp.tools.scan_tools import rebuild_repo_snapshot
from tests.fixtures.query_path_repo import build_query_path_repo
from tests.fixtures.query_repo import build_query_repo


EXPECTED_TOOL_NAMES = {
    "rebuild_repo_snapshot",
    "list_priority_files",
    "get_file_info",
    "list_file_symbols",
    "resolve_symbols",
    "open_symbol_context",
    "query_call_relations",
    "find_root_functions",
    "find_call_paths",
}

LEGACY_TOOL_NAMES = {
    "scan_repo",
    "refresh_scan",
    "get_scan_status",
    "show_scope",
    "list_scope_nodes",
    "explain_scope_node",
    "list_anchors",
    "find_anchor",
    "describe_anchor",
    "plan_slice",
    "expand_slice",
    "inspect_slice",
    "build_evidence_pack",
    "read_evidence_pack",
    "open_span",
    "impact_from_paths",
    "impact_from_anchor",
    "summarize_impact",
    "render_focus_report",
    "render_module_summary",
    "render_analysis_outline",
    "export_analysis_bundle",
    "export_scope_snapshot",
    "export_evidence_bundle",
}

TOOL_MODULES = (scan_tools, query_tools)
TOOL_BY_NAME = {
    name: tool
    for module in TOOL_MODULES
    for name, tool in inspect.getmembers(module, inspect.isfunction)
    if tool.__module__ == module.__name__ and not name.startswith("_")
}


class ToolContractsTest(unittest.TestCase):
    def test_contract_registry_exposes_only_the_new_domains(self) -> None:
        self.assertEqual(set(DOMAIN_CONTRACTS), {"scan", "query"})
        self.assertEqual(set(CONTRACT_BY_NAME), EXPECTED_TOOL_NAMES)
        self.assertTrue(LEGACY_TOOL_NAMES.isdisjoint(CONTRACT_BY_NAME))

    def test_contract_schemas_match_the_new_surface(self) -> None:
        self.assertEqual(
            CONTRACT_BY_NAME["rebuild_repo_snapshot"].input_schema,
            {"target_repo": "string"},
        )
        self.assertEqual(
            CONTRACT_BY_NAME["rebuild_repo_snapshot"].output_schema,
            {
                "scan_id": "scan_<12-hex>",
                "file_count": "int",
                "symbol_count": "int",
                "function_count": "int",
                "call_edge_count": "int",
            },
        )
        self.assertEqual(
            CONTRACT_BY_NAME["get_file_info"].input_schema,
            {"scan_id": "scan_<12-hex>", "path": "string"},
        )
        self.assertEqual(
            CONTRACT_BY_NAME["open_symbol_context"].input_schema,
            {
                "scan_id": "scan_<12-hex>",
                "symbol_id": "string",
                "context_lines": "int",
            },
        )
        self.assertEqual(
            CONTRACT_BY_NAME["find_call_paths"].output_schema,
            {
                "status": "string",
                "returned_path_count": "int",
                "truncated": "bool",
                "paths": "list",
            },
        )

    def test_imported_tool_set_matches_contract_registry(self) -> None:
        self.assertEqual(set(TOOL_BY_NAME), EXPECTED_TOOL_NAMES)

    def test_tool_signatures_match_contract_input_schemas(self) -> None:
        for contract_name, contract in CONTRACT_BY_NAME.items():
            signature = inspect.signature(TOOL_BY_NAME[contract_name])
            self.assertEqual(set(signature.parameters), set(contract.input_schema), contract_name)

    def test_every_tool_returns_ok_with_real_repo_state(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            repo = build_query_repo(Path(tmpdir))
            rebuild_payload = rebuild_repo_snapshot(str(repo))
            scan_id = rebuild_payload["data"]["scan_id"]

            self.assertEqual(set(rebuild_payload["data"]), set(CONTRACT_BY_NAME["rebuild_repo_snapshot"].output_schema))
            self.assertEqual(rebuild_payload["messages"], [])
            self.assertEqual(rebuild_payload["data"]["file_count"], 5)
            self.assertGreater(rebuild_payload["data"]["symbol_count"], 0)
            self.assertGreater(rebuild_payload["data"]["function_count"], 0)

            priority_payload = list_priority_files(scan_id)
            file_info_payload = get_file_info(scan_id, "src/main.c")
            file_symbols_payload = list_file_symbols(scan_id, ["src/main.c", "src/flash.c"])
            symbol_payload = resolve_symbols(scan_id, "flash_init")
            symbol_id = symbol_payload["data"]["matches"][0]["symbol_id"]
            context_payload = open_symbol_context(scan_id, symbol_id, 1)
            relations_payload = query_call_relations(scan_id, symbol_id)
            roots_payload = find_root_functions(scan_id, ["src/main.c", "src/flash.c"])
            paths_payload = find_call_paths(scan_id, roots_payload["data"]["roots"][0]["symbol_id"], symbol_id)

            self.assertEqual(priority_payload["status"], "ok")
            self.assertEqual(priority_payload["messages"], [])
            self.assertEqual(priority_payload["data"]["files"][0]["path"], "src/main.c")
            self.assertEqual(file_info_payload["messages"], [])
            self.assertEqual(file_info_payload["data"]["path"], "src/main.c")
            self.assertTrue(file_info_payload["data"]["has_main_definition"])
            self.assertEqual(file_symbols_payload["messages"], [])
            self.assertEqual(
                {row["path"] for row in file_symbols_payload["data"]["files"]},
                {"src/flash.c", "src/main.c"},
            )
            self.assertEqual(symbol_payload["messages"], [])
            self.assertEqual(symbol_payload["data"]["match_count"], 2)
            self.assertEqual(context_payload["messages"], [])
            self.assertEqual(context_payload["data"]["path"], "src/flash.c")
            self.assertEqual(relations_payload["messages"], [])
            self.assertEqual(relations_payload["data"]["callers"][0]["name"], "main")
            self.assertIsInstance(relations_payload["data"]["callers"][0]["call_lines"], list)
            self.assertIsInstance(relations_payload["data"]["callees"][0]["call_lines"], list)
            self.assertEqual(roots_payload["messages"], [])
            self.assertEqual(roots_payload["data"]["roots"][0]["name"], "main")
            self.assertEqual(paths_payload["messages"], [])
            self.assertEqual(paths_payload["data"]["status"], "found")

        with tempfile.TemporaryDirectory() as tmpdir:
            repo = build_query_path_repo(Path(tmpdir), branch_count=2)
            rebuild_payload = rebuild_repo_snapshot(str(repo))
            scan_id = rebuild_payload["data"]["scan_id"]
            dst_id = resolve_symbols(scan_id, "dst")["data"]["matches"][0]["symbol_id"]

            relations_payload = query_call_relations(scan_id, dst_id)

            self.assertEqual(relations_payload["messages"], [])
            self.assertIsInstance(relations_payload["data"]["callers"][0]["call_lines"], list)
            self.assertIsInstance(relations_payload["data"]["callees"][0]["call_lines"], list)
            self.assertIsInstance(
                relations_payload["data"]["non_resolved_callees"][0]["call_lines"],
                list,
            )

    def test_rebuild_repo_snapshot_rejects_missing_repo_path(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            missing_repo = Path(tmpdir) / "missing-repo"
            payload = rebuild_repo_snapshot(str(missing_repo))

            self.assertEqual(payload["status"], "error")
            self.assertEqual(payload["data"]["error"]["code"], "invalid_input")

    def test_rebuild_repo_snapshot_rejects_non_directory_repo_path(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            repo_file = Path(tmpdir) / "repo.txt"
            repo_file.write_text("not a directory", encoding="utf-8")

            payload = rebuild_repo_snapshot(str(repo_file))

            self.assertEqual(payload["status"], "error")
            self.assertEqual(payload["data"]["error"]["code"], "invalid_input")

    def test_rebuild_repo_snapshot_wraps_unexpected_scan_error(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            with mock.patch.object(scan_tools.ScanService, "scan", side_effect=PermissionError("no access")):
                payload = rebuild_repo_snapshot(tmpdir)

            self.assertEqual(payload["status"], "error")
            self.assertEqual(payload["data"]["error"]["code"], "internal")

    def test_query_tool_wraps_unexpected_service_error(self) -> None:
        with mock.patch.object(query_tools, "repo_root_for_scan", return_value="/repo"), mock.patch.object(
            query_tools.QueryService,
            "list_priority_files",
            side_effect=OSError("storage unavailable"),
        ):
            payload = list_priority_files("scan_123456abcdef")

        self.assertEqual(payload["status"], "error")
        self.assertEqual(payload["data"]["error"]["code"], "internal")
