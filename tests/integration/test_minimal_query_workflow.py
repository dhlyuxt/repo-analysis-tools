import tempfile
import unittest
from pathlib import Path

from repo_analysis_tools.mcp.tools.query_tools import (
    find_call_paths,
    find_root_functions,
    get_file_info,
    list_priority_files,
    open_symbol_context,
    query_call_relations,
    resolve_symbols,
)
from repo_analysis_tools.mcp.tools.scan_tools import rebuild_repo_snapshot
from tests.fixtures.query_repo import build_query_repo


class MinimalQueryWorkflowTest(unittest.TestCase):
    def test_query_first_workflow_uses_only_the_new_tool_chain(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            repo = build_query_repo(Path(tmpdir))

            rebuild_payload = rebuild_repo_snapshot(str(repo))
            scan_id = rebuild_payload["data"]["scan_id"]
            priority_payload = list_priority_files(scan_id)
            file_info_payload = get_file_info(scan_id, "src/main.c")
            symbol_payload = resolve_symbols(scan_id, "flash_init")
            symbol_id = symbol_payload["data"]["matches"][0]["symbol_id"]
            context_payload = open_symbol_context(scan_id, symbol_id, 1)
            relations_payload = query_call_relations(scan_id, symbol_id)
            roots_payload = find_root_functions(scan_id, ["src/main.c", "src/flash.c"])
            root_id = roots_payload["data"]["roots"][0]["symbol_id"]
            paths_payload = find_call_paths(scan_id, root_id, symbol_id)

            self.assertEqual(priority_payload["data"]["files"][0]["path"], "src/main.c")
            self.assertTrue(file_info_payload["data"]["has_main_definition"])
            self.assertEqual(symbol_payload["data"]["match_count"], 2)
            self.assertEqual(context_payload["data"]["path"], "src/flash.c")
            self.assertEqual(relations_payload["data"]["callers"][0]["name"], "main")
            self.assertEqual(roots_payload["data"]["roots"][0]["name"], "main")
            self.assertEqual(paths_payload["data"]["status"], "found")

