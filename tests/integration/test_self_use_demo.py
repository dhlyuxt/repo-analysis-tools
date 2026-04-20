import json
import subprocess
import unittest
from pathlib import Path


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
            {"scan_id", "symbol_name", "priority_files", "caller_count", "call_path_status"},
        )
        self.assertRegex(payload["scan_id"], r"^scan_[0-9a-f]{12}$")
        self.assertEqual(payload["symbol_name"], "easyflash_init")
        self.assertIsInstance(payload["priority_files"], list)
        self.assertGreater(len(payload["priority_files"]), 0)
        self.assertGreaterEqual(payload["caller_count"], 0)
        self.assertIn(payload["call_path_status"], {"found", "no_path", "truncated"})
