import json
import tomllib
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
CODEX_CONFIG_PATH = ROOT / ".codex" / "config.toml"
MCP_CONFIG_PATH = ROOT / ".mcp.json"


class ClientBootstrapAssetsTest(unittest.TestCase):
    def test_codex_config_declares_repo_analysis_tools_mcp_server(self) -> None:
        config = tomllib.loads(CODEX_CONFIG_PATH.read_text(encoding="utf-8"))
        server = config["mcp_servers"]["repo_analysis_tools"]

        self.assertEqual(server["command"], "/home/hyx/anaconda3/envs/agent/bin/python")
        self.assertEqual(server["args"], ["-m", "repo_analysis_tools.mcp.server"])

    def test_mcp_json_declares_repo_analysis_tools_mcp_server(self) -> None:
        config = json.loads(MCP_CONFIG_PATH.read_text(encoding="utf-8"))
        server = config["mcpServers"]["repo-analysis-tools"]

        self.assertEqual(server["command"], "/home/hyx/anaconda3/envs/agent/bin/python")
        self.assertEqual(server["args"], ["-m", "repo_analysis_tools.mcp.server"])
