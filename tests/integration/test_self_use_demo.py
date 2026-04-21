import json
import subprocess
import unittest
from pathlib import Path

from tools.run_self_use_demo import run_demo


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "tools" / "run_self_use_demo.py"


class SelfUseDemoIntegrationTest(unittest.TestCase):
    def test_run_demo_emits_expected_json_summary_and_cleans_previous_fixture(self) -> None:
        payload = run_demo()
        repo_root = Path(payload["repo_root"])
        self.assertEqual(
            set(payload),
            {
                "repo_root",
                "scan_id",
                "symbol_name",
                "symbol_path",
                "priority_files",
                "file_info",
                "file_symbols",
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
        self.assertTrue(repo_root.is_dir())
        self.assertTrue(str(repo_root).startswith("/tmp/"))
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
        self.assertIn("easyflash/src/easyflash.c", payload["file_symbols"])
        self.assertIn("easyflash/port/ef_port.c", payload["file_symbols"])
        self.assertGreater(payload["file_symbols"]["easyflash/src/easyflash.c"]["symbol_count"], 0)
        self.assertIn("easyflash_init", payload["file_symbols"]["easyflash/src/easyflash.c"]["symbol_names"])

        sentinel = repo_root / "stale-marker.txt"
        sentinel.write_text("stale", encoding="utf-8")

        rerun_payload = run_demo()
        self.assertEqual(rerun_payload["repo_root"], payload["repo_root"])
        self.assertTrue(Path(rerun_payload["repo_root"]).is_dir())
        self.assertFalse(sentinel.exists())

    def test_self_use_demo_script_emits_expected_json_summary(self) -> None:
        result = subprocess.run(
            ["/home/hyx/anaconda3/envs/agent/bin/python", str(SCRIPT)],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=True,
        )

        payload = json.loads(result.stdout)
        self.assertEqual(payload["symbol_name"], "easyflash_init")
        self.assertTrue(Path(payload["repo_root"]).is_dir())
        self.assertTrue(str(Path(payload["repo_root"])).startswith("/tmp/"))
        self.assertGreater(payload["file_symbols"]["easyflash/src/easyflash.c"]["symbol_count"], 0)
        self.assertIn("easyflash_init", payload["file_symbols"]["easyflash/src/easyflash.c"]["symbol_names"])
