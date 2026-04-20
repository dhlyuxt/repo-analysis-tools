import os
from pathlib import Path
import select
import json
import subprocess
import sys
import time
import unittest


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

    def test_server_replies_to_initialize_over_stdio(self) -> None:
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
            assert process.stdin is not None
            assert process.stdout is not None
            initialize_request = json.dumps(
                {
                    "jsonrpc": "2.0",
                    "id": 1,
                    "method": "initialize",
                    "params": {
                        "protocolVersion": "2025-11-25",
                        "capabilities": {},
                        "clientInfo": {"name": "smoke-test", "version": "0.1.0"},
                    },
                }
            )
            process.stdin.write(initialize_request + "\n")
            process.stdin.flush()

            ready, _, _ = select.select([process.stdout], [], [], 2.0)
            if not ready:
                self.fail("server did not reply to initialize over stdio within 2 seconds")

            response_line = process.stdout.readline()
            response = json.loads(response_line)
            self.assertEqual(response["id"], 1)
            self.assertEqual(response["result"]["serverInfo"]["name"], "repo-analysis-tools")

            initialized_notification = json.dumps(
                {
                    "jsonrpc": "2.0",
                    "method": "notifications/initialized",
                }
            )
            process.stdin.write(initialized_notification + "\n")
            process.stdin.flush()

            list_tools_request = json.dumps(
                {
                    "jsonrpc": "2.0",
                    "id": 2,
                    "method": "tools/list",
                    "params": {},
                }
            )
            process.stdin.write(list_tools_request + "\n")
            process.stdin.flush()

            ready, _, _ = select.select([process.stdout], [], [], 2.0)
            if not ready:
                self.fail("server did not reply to tools/list over stdio within 2 seconds")

            tools_response_line = process.stdout.readline()
            tools_response = json.loads(tools_response_line)
            self.assertEqual(tools_response["id"], 2)
            tool_names = [tool["name"] for tool in tools_response["result"]["tools"]]
            self.assertEqual(set(tool_names), EXPECTED_TOOL_NAMES)
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
