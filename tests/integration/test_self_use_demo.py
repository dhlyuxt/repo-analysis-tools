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
        repo_root = Path(payload["repo_root"])
        markdown_path = Path(payload["markdown_path"])
        copied_markdown_path = Path(payload["copied_markdown_path"])

        self.assertTrue(repo_root.is_dir())
        self.assertRegex(payload["scan_id"], r"^scan_[0-9a-f]{12}$")
        self.assertRegex(payload["evidence_pack_id"], r"^evidence_pack_[0-9a-f]{12}$")
        self.assertRegex(payload["impact_id"], r"^impact_[0-9a-f]{12}$")
        self.assertRegex(payload["report_id"], r"^report_[0-9a-f]{12}$")
        self.assertRegex(payload["export_id"], r"^export_[0-9a-f]{12}$")
        self.assertTrue(markdown_path.is_file())
        self.assertTrue(copied_markdown_path.is_file())
