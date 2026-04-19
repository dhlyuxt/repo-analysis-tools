import inspect
import tempfile
import unittest
from pathlib import Path

from repo_analysis_tools.mcp.contracts import CONTRACT_BY_NAME, DOMAIN_CONTRACTS
from repo_analysis_tools.mcp.tools import anchors_tools, evidence_tools, export_tools, impact_tools, report_tools, scan_tools, scope_tools, slice_tools
from repo_analysis_tools.mcp.tools.export_tools import export_scope_snapshot
from repo_analysis_tools.mcp.tools.scan_tools import get_scan_status, refresh_scan, scan_repo
from repo_analysis_tools.mcp.tools.shared import stub_payload
from tests.fixtures.scope_first_repo import build_scope_first_repo


EXPECTED_DOMAINS = {
    "scan",
    "scope",
    "anchors",
    "slice",
    "evidence",
    "impact",
    "report",
    "export",
}

TOOL_MODULES = (
    scan_tools,
    scope_tools,
    anchors_tools,
    slice_tools,
    evidence_tools,
    impact_tools,
    report_tools,
    export_tools,
)

TOOL_BY_NAME = {
    name: tool
    for module in TOOL_MODULES
    for name, tool in inspect.getmembers(module, inspect.isfunction)
    if tool.__module__ == module.__name__
}

TOOL_CALL_KWARGS = {
    "scan_repo": {"target_repo": "/tmp/demo-repo"},
    "refresh_scan": {"target_repo": "/tmp/demo-repo", "scan_id": "scan_000000000001"},
    "get_scan_status": {"target_repo": "/tmp/demo-repo"},
    "show_scope": {"target_repo": "/tmp/demo-repo"},
    "list_scope_nodes": {"target_repo": "/tmp/demo-repo"},
    "explain_scope_node": {"target_repo": "/tmp/demo-repo", "node_id": "src"},
    "list_anchors": {"target_repo": "/tmp/demo-repo"},
    "find_anchor": {"target_repo": "/tmp/demo-repo", "anchor_name": "main"},
    "describe_anchor": {"target_repo": "/tmp/demo-repo", "anchor_name": "main"},
    "plan_slice": {"target_repo": "/tmp/demo-repo", "question": "Where does the entrypoint flow go?"},
    "expand_slice": {"target_repo": "/tmp/demo-repo", "slice_id": "slice_000000000001"},
    "inspect_slice": {"target_repo": "/tmp/demo-repo", "slice_id": "slice_000000000001"},
    "build_evidence_pack": {"target_repo": "/tmp/demo-repo", "slice_id": "slice_000000000001"},
    "read_evidence_pack": {"target_repo": "/tmp/demo-repo", "evidence_pack_id": "evidence_pack_000000000001"},
    "open_span": {
        "target_repo": "/tmp/demo-repo",
        "evidence_pack_id": "evidence_pack_000000000001",
        "path": "src/main.c",
        "line_start": 1,
        "line_end": 2,
    },
    "impact_from_paths": {"target_repo": "/tmp/demo-repo", "paths": ["src/main.c"]},
    "impact_from_anchor": {"target_repo": "/tmp/demo-repo", "anchor_name": "main"},
    "summarize_impact": {"target_repo": "/tmp/demo-repo", "focus": "entrypoint"},
    "render_focus_report": {"target_repo": "/tmp/demo-repo", "evidence_pack_id": "evidence_pack_000000000001"},
    "render_module_summary": {
        "target_repo": "/tmp/demo-repo",
        "evidence_pack_id": "evidence_pack_000000000001",
        "module_name": "core",
    },
    "render_analysis_outline": {"target_repo": "/tmp/demo-repo", "focus": "entrypoint"},
    "export_analysis_bundle": {"target_repo": "/tmp/demo-repo", "report_id": "report_000000000001"},
    "export_scope_snapshot": {"target_repo": "/tmp/demo-repo"},
    "export_evidence_bundle": {"target_repo": "/tmp/demo-repo", "evidence_pack_id": "evidence_pack_000000000001"},
}


class ToolContractsTest(unittest.TestCase):
    def _invoke_tool(self, contract_name: str) -> dict:
        if contract_name not in {"scan_repo", "refresh_scan", "get_scan_status"}:
            return TOOL_BY_NAME[contract_name](**TOOL_CALL_KWARGS[contract_name])

        with tempfile.TemporaryDirectory() as tmpdir:
            repo = build_scope_first_repo(Path(tmpdir))
            target_repo = str(repo)
            if contract_name == "scan_repo":
                return scan_repo(target_repo)

            created = scan_repo(target_repo)
            if contract_name == "refresh_scan":
                return TOOL_BY_NAME[contract_name](
                    target_repo=target_repo,
                    scan_id=created["data"]["scan_id"],
                )
            return TOOL_BY_NAME[contract_name](target_repo=target_repo)

    def test_every_required_domain_group_exists(self) -> None:
        self.assertEqual(set(DOMAIN_CONTRACTS), EXPECTED_DOMAINS)
        for domain_name, contracts in DOMAIN_CONTRACTS.items():
            self.assertEqual(len(contracts), 3, domain_name)

    def test_every_contract_declares_shape_and_failure_modes(self) -> None:
        for contract in CONTRACT_BY_NAME.values():
            self.assertTrue(contract.input_schema, contract.name)
            self.assertTrue(contract.output_schema, contract.name)
            self.assertTrue(contract.failure_modes, contract.name)

    def test_contract_names_and_imported_tool_set_stay_aligned(self) -> None:
        self.assertEqual(set(TOOL_BY_NAME), set(CONTRACT_BY_NAME))

    def test_every_contract_has_callable_stub_tool(self) -> None:
        for contract_name in CONTRACT_BY_NAME:
            payload = self._invoke_tool(contract_name)
            self.assertEqual(payload["status"], "ok", contract_name)

    def test_tool_signatures_match_contract_input_schemas(self) -> None:
        for contract_name, contract in CONTRACT_BY_NAME.items():
            signature = inspect.signature(TOOL_BY_NAME[contract_name])
            self.assertEqual(set(signature.parameters), set(contract.input_schema), contract_name)
            for field_name, schema in contract.input_schema.items():
                parameter = signature.parameters[field_name]
                is_nullable = schema.endswith("|null")
                if is_nullable:
                    self.assertIsNot(parameter.default, inspect._empty, f"{contract_name}:{field_name}")
                else:
                    self.assertIs(parameter.default, inspect._empty, f"{contract_name}:{field_name}")

    def test_stub_output_data_keys_match_declared_output_schema(self) -> None:
        for contract_name, contract in CONTRACT_BY_NAME.items():
            payload = self._invoke_tool(contract_name)
            self.assertEqual(set(payload["data"]), set(contract.output_schema), contract_name)

    def test_scan_repo_stub_uses_standard_envelope(self) -> None:
        payload = stub_payload(
            "scan_repo",
            target_repo="/tmp/demo-repo",
            scan_id="scan_stub000001",
        )
        self.assertEqual(payload["schema_version"], "1")
        self.assertEqual(payload["status"], "ok")
        self.assertEqual(payload["data"]["scan_id"], "scan_stub000001")
        self.assertEqual(payload["recommended_next_tools"], ["get_scan_status", "show_scope"])

    def test_scan_backed_stubs_generate_declared_scan_id_when_omitted(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            repo = build_scope_first_repo(Path(tmpdir))
            scan_repo(str(repo))
            scan_status_payload = get_scan_status(str(repo))
            export_payload = export_scope_snapshot("/tmp/demo-repo")

        self.assertRegex(scan_status_payload["data"]["scan_id"], r"^scan_[0-9a-f]{12}$")
        self.assertRegex(export_payload["data"]["scan_id"], r"^scan_[0-9a-f]{12}$")

    def test_stub_outputs_do_not_include_undeclared_contract_version(self) -> None:
        payload = stub_payload("get_scan_status", target_repo="/tmp/demo-repo")
        with tempfile.TemporaryDirectory() as tmpdir:
            repo = build_scope_first_repo(Path(tmpdir))
            scan_repo(str(repo))
            tool_payload = get_scan_status(str(repo))

        self.assertNotIn("contract_version", payload["data"])
        self.assertNotIn("contract_version", tool_payload["data"])

    def test_scan_repo_and_get_scan_status_use_real_services(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            repo = build_scope_first_repo(Path(tmpdir))
            created = scan_repo(str(repo))
            status = get_scan_status(str(repo))

            self.assertEqual(created["data"]["file_count"], 6)
            self.assertEqual(
                status["data"]["latest_completed_at"],
                created["data"]["latest_completed_at"],
            )

    def test_refresh_scan_returns_error_for_unknown_scan_id(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            repo = build_scope_first_repo(Path(tmpdir))

            payload = refresh_scan(str(repo), "scan_deadbeefcafe")

            self.assertEqual(payload["status"], "error")
            self.assertEqual(payload["data"]["error"]["code"], "not_found")
            self.assertEqual(payload["recommended_next_tools"], [])
