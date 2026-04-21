import json
import subprocess
import unittest
import tempfile
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
from tests.fixtures.easyflash_repo import materialize_easyflash_repo


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "tools" / "run_self_use_demo.py"


class SelfUseDemoIntegrationTest(unittest.TestCase):
    def test_self_use_demo_emits_expected_json_summary(self) -> None:
        result = subprocess.run(
            ["/home/hyx/anaconda3/envs/agent/bin/python", str(SCRIPT)],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=True,
        )

        payload = json.loads(result.stdout)
        self.assertEqual(
            set(payload),
            {
                "repo_root",
                "scan_id",
                "symbol_name",
                "symbol_path",
                "priority_files",
                "file_info",
                "context_line_start",
                "context_line_end",
                "caller_count",
                "callee_count",
                "root_names",
                "call_path_status",
                "call_path_count",
            },
        )
        self.assertRegex(payload["scan_id"], r"^scan_[0-9a-f]{12}$")
        self.assertEqual(payload["symbol_name"], "easyflash_init")
        self.assertEqual(payload["symbol_path"], "easyflash/src/easyflash.c")
        self.assertEqual(payload["file_info"]["path"], "easyflash/src/easyflash.c")
        self.assertIsInstance(payload["priority_files"], list)
        self.assertGreater(len(payload["priority_files"]), 0)
        self.assertGreaterEqual(payload["caller_count"], 0)
        self.assertGreaterEqual(payload["callee_count"], 0)
        self.assertIsInstance(payload["root_names"], list)
        self.assertGreater(len(payload["root_names"]), 0)
        self.assertIn(payload["call_path_status"], {"found", "no_path", "truncated"})
        self.assertGreaterEqual(payload["call_path_count"], 0)
        self.assertIn("file_info", payload)
        self.assertIn("symbol_path", payload)
        self.assertIn("context_line_start", payload)
        self.assertIn("context_line_end", payload)

    def test_demo_uses_the_full_query_first_path(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            repo = materialize_easyflash_repo(Path(tmpdir))
            rebuild_payload = rebuild_repo_snapshot(str(repo))
            scan_id = rebuild_payload["data"]["scan_id"]

            priority_payload = list_priority_files(scan_id)
            self.assertGreater(len(priority_payload["data"]["files"]), 0)

            file_info_payload = get_file_info(scan_id, "easyflash/src/easyflash.c")
            self.assertEqual(file_info_payload["data"]["path"], "easyflash/src/easyflash.c")

            symbol_payload = resolve_symbols(scan_id, "easyflash_init")
            symbol_row = symbol_payload["data"]["matches"][0]
            context_payload = open_symbol_context(scan_id, symbol_row["symbol_id"], 2)
            relations_payload = query_call_relations(scan_id, symbol_row["symbol_id"])
            roots_payload = find_root_functions(scan_id, ["easyflash/src/easyflash.c", "easyflash/port/ef_port.c"])
            path_payload = None
            self.assertGreaterEqual(len(relations_payload["data"]["callees"]), 0)
            self.assertGreaterEqual(len(roots_payload["data"]["roots"]), 0)
            self.assertGreaterEqual(context_payload["data"]["context_line_end"], context_payload["data"]["context_line_start"])

            if roots_payload["data"]["roots"]:
                path_payload = find_call_paths(
                    scan_id,
                    roots_payload["data"]["roots"][0]["symbol_id"],
                    symbol_row["symbol_id"],
                )
                self.assertIn(path_payload["data"]["status"], {"found", "no_path", "truncated"})
                self.assertIn("returned_path_count", path_payload["data"])
            else:
                self.assertIsNone(path_payload)
            self.assertEqual(context_payload["data"]["symbol_id"], symbol_row["symbol_id"])
