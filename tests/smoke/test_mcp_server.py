import os
from pathlib import Path
import subprocess
import sys
import time
import unittest


class McpServerSmokeTest(unittest.TestCase):
    def test_server_process_starts_under_stdio(self) -> None:
        src_root = Path(__file__).resolve().parents[2] / "src"
        env = dict(os.environ)
        env["PYTHONPATH"] = str(src_root)
        process = subprocess.Popen(
            [sys.executable, "-m", "repo_analysis_tools.mcp.server"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            env=env,
        )
        try:
            deadline = time.monotonic() + 1.0
            while time.monotonic() < deadline:
                poll_result = process.poll()
                if poll_result is not None:
                    stderr_output = process.stderr.read()
                    self.fail(f"server exited early: {stderr_output}")
                time.sleep(0.1)
        finally:
            if process.poll() is None:
                try:
                    process.terminate()
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    process.kill()
                    process.wait(timeout=5)
            if process.stdin is not None:
                process.stdin.close()
            if process.stdout is not None:
                process.stdout.close()
            if process.stderr is not None:
                process.stderr.close()
