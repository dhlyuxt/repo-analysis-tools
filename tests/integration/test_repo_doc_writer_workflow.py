import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from tests.unit.test_repo_doc_writer_service import sample_payload


class RepositoryDesignWriterWorkflowTest(unittest.TestCase):
    def test_cli_writes_repo_design_manifest(self) -> None:
        project_root = Path(__file__).resolve().parents[2]
        script_path = project_root / "tools" / "write_repo_design_docs.py"
        with tempfile.TemporaryDirectory() as tmpdir:
            temp_path = Path(tmpdir)
            output_root = temp_path / "docs" / "repo-design"
            input_path = temp_path / "findings.json"
            input_path.write_text(
                json.dumps(sample_payload(str(output_root))), encoding="utf-8"
            )

            env = dict(os.environ)
            env["PYTHONPATH"] = str(project_root / "src")
            completed = subprocess.run(
                [sys.executable, str(script_path), "--input", str(input_path)],
                text=True,
                capture_output=True,
                check=False,
                env=env,
            )

            self.assertEqual(0, completed.returncode, completed.stderr)
            stdout_manifest = json.loads(completed.stdout)
            self.assertEqual("ok", stdout_manifest["validation_status"])

            persisted_manifest = json.loads(
                (output_root / "manifest.json").read_text(encoding="utf-8")
            )
            self.assertEqual("ok", persisted_manifest["validation_status"])
