import inspect
import tempfile
import unittest
from pathlib import Path

from repo_analysis_tools.mcp.contracts import CONTRACT_BY_NAME, DOMAIN_CONTRACTS
from repo_analysis_tools.mcp.tools import anchors_tools, evidence_tools, export_tools, impact_tools, report_tools, scan_tools, scope_tools, slice_tools
from repo_analysis_tools.mcp.tools.anchors_tools import describe_anchor, find_anchor, list_anchors
from repo_analysis_tools.mcp.tools.evidence_tools import build_evidence_pack, open_span, read_evidence_pack
from repo_analysis_tools.mcp.tools.export_tools import export_scope_snapshot
from repo_analysis_tools.mcp.tools.scope_tools import explain_scope_node, list_scope_nodes, show_scope
from repo_analysis_tools.mcp.tools.scan_tools import get_scan_status, refresh_scan, scan_repo
from repo_analysis_tools.mcp.tools.shared import stub_payload
from tests.fixtures.easyflash_repo import materialize_easyflash_repo
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
    if tool.__module__ == module.__name__ and not name.startswith("_")
}

TOOL_CALL_KWARGS = {
    "scan_repo": {"target_repo": "/tmp/demo-repo"},
    "refresh_scan": {"target_repo": "/tmp/demo-repo", "scan_id": "scan_000000000001"},
    "get_scan_status": {"target_repo": "/tmp/demo-repo"},
    "show_scope": {"target_repo": "/tmp/demo-repo"},
    "list_scope_nodes": {"target_repo": "/tmp/demo-repo"},
    "explain_scope_node": {"target_repo": "/tmp/demo-repo", "node_id": "scope_src"},
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
        if contract_name not in {
            "scan_repo",
            "refresh_scan",
            "get_scan_status",
            "show_scope",
            "list_scope_nodes",
            "explain_scope_node",
            "list_anchors",
            "find_anchor",
            "describe_anchor",
            "plan_slice",
            "expand_slice",
            "inspect_slice",
            "build_evidence_pack",
            "read_evidence_pack",
            "open_span",
        }:
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
            if contract_name == "show_scope":
                return show_scope(target_repo, created["data"]["scan_id"])
            if contract_name == "list_scope_nodes":
                return list_scope_nodes(target_repo, created["data"]["scan_id"])
            if contract_name == "explain_scope_node":
                return explain_scope_node(target_repo, "scope_src", created["data"]["scan_id"])
            if contract_name == "list_anchors":
                return list_anchors(target_repo, created["data"]["scan_id"])
            if contract_name == "find_anchor":
                return find_anchor(target_repo, "main", created["data"]["scan_id"])
            if contract_name == "describe_anchor":
                return describe_anchor(target_repo, "main", created["data"]["scan_id"])
            if contract_name == "plan_slice":
                return slice_tools.plan_slice(target_repo, "Where is flash_init defined?")
            planned = slice_tools.plan_slice(target_repo, "Where is flash_init defined?")
            if contract_name == "expand_slice":
                return slice_tools.expand_slice(target_repo, planned["data"]["slice_id"])
            if contract_name == "inspect_slice":
                return slice_tools.inspect_slice(target_repo, planned["data"]["slice_id"])
            if contract_name == "build_evidence_pack":
                return build_evidence_pack(target_repo, planned["data"]["slice_id"])
            evidence_pack = build_evidence_pack(target_repo, planned["data"]["slice_id"])
            if contract_name == "read_evidence_pack":
                return read_evidence_pack(target_repo, evidence_pack["data"]["evidence_pack_id"])
            if contract_name == "open_span":
                return open_span(
                    target_repo,
                    evidence_pack["data"]["evidence_pack_id"],
                    "src/flash.c",
                    1,
                    1,
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

    def test_plan_slice_contract_recommended_next_tools_match_runtime_behavior(self) -> None:
        self.assertEqual(
            CONTRACT_BY_NAME["plan_slice"].recommended_next_tools,
            ("inspect_slice", "build_evidence_pack"),
        )

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

    def test_scope_tools_use_real_services(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            repo = build_scope_first_repo(Path(tmpdir))
            created = scan_repo(str(repo))

            scope_payload = show_scope(str(repo))
            nodes_payload = list_scope_nodes(str(repo), created["data"]["scan_id"])
            explain_payload = explain_scope_node(str(repo), "scope_src", created["data"]["scan_id"])

            self.assertEqual(scope_payload["data"]["scan_id"], created["data"]["scan_id"])
            self.assertEqual(
                scope_payload["data"]["role_counts"],
                {"external": 1, "generated": 1, "primary": 3, "support": 1},
            )
            self.assertEqual(nodes_payload["data"]["nodes"][0]["node_id"], "scope_demo")
            self.assertEqual(explain_payload["data"]["related_files"][0], "src/config.h")

    def test_anchor_tools_use_real_services(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            repo = build_scope_first_repo(Path(tmpdir))
            created = scan_repo(str(repo))

            anchors_payload = list_anchors(str(repo), created["data"]["scan_id"])
            find_payload = find_anchor(str(repo), "main", created["data"]["scan_id"])
            describe_payload = describe_anchor(str(repo), "main", created["data"]["scan_id"])

            self.assertEqual(anchors_payload["data"]["scan_id"], created["data"]["scan_id"])
            self.assertTrue(
                {"EF_USING_ENV", "flash_init", "main"}.issubset(
                    {anchor["name"] for anchor in anchors_payload["data"]["anchors"]}
                )
            )
            self.assertEqual(find_payload["data"]["matches"][0]["name"], "main")
            self.assertEqual(describe_payload["data"]["anchor_name"], "main")
            self.assertIn(
                "direct_call",
                {relation["kind"] for relation in describe_payload["data"]["relations"]},
            )

    def test_slice_tools_use_real_services(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            repo = build_scope_first_repo(Path(tmpdir))
            created = scan_repo(str(repo))

            plan_payload = slice_tools.plan_slice(str(repo), "Where is flash_init defined?")
            inspect_payload = slice_tools.inspect_slice(str(repo), plan_payload["data"]["slice_id"])
            expand_payload = slice_tools.expand_slice(str(repo), plan_payload["data"]["slice_id"])

            self.assertEqual(plan_payload["data"]["scan_id"], created["data"]["scan_id"])
            self.assertEqual(plan_payload["data"]["query_kind"], "locate_symbol")
            self.assertEqual(plan_payload["data"]["status"], "complete")
            self.assertEqual(plan_payload["data"]["selected_files"], ["src/flash.c"])
            self.assertEqual(plan_payload["data"]["selected_anchor_names"], ["flash_init"])
            self.assertEqual(plan_payload["data"]["notes"], ["Located definition candidates for flash_init."])
            self.assertNotIn("M1", plan_payload["messages"][0]["text"])
            self.assertEqual(
                plan_payload["recommended_next_tools"],
                ["inspect_slice", "build_evidence_pack"],
            )
            self.assertEqual(inspect_payload["data"]["members"], ["src/flash.c"])
            self.assertEqual(expand_payload["data"]["slice_id"], plan_payload["data"]["slice_id"])
            self.assertFalse(expand_payload["data"]["expanded"])

    def test_evidence_tools_use_real_services(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            repo = build_scope_first_repo(Path(tmpdir))
            scan_repo(str(repo))
            plan_payload = slice_tools.plan_slice(str(repo), "Where is flash_init defined?")

            build_payload = build_evidence_pack(str(repo), plan_payload["data"]["slice_id"])
            read_payload = read_evidence_pack(str(repo), build_payload["data"]["evidence_pack_id"])
            open_payload = open_span(str(repo), build_payload["data"]["evidence_pack_id"], "src/flash.c", 1, 1)

            self.assertEqual(build_payload["status"], "ok")
            self.assertEqual(build_payload["data"]["slice_id"], plan_payload["data"]["slice_id"])
            self.assertEqual(build_payload["data"]["citation_count"], 1)
            self.assertEqual(read_payload["data"]["citations"][0]["file_path"], "src/flash.c")
            self.assertEqual(read_payload["recommended_next_tools"], ["open_span"])
            self.assertEqual(open_payload["data"]["line_start"], 1)
            self.assertEqual(open_payload["data"]["line_end"], 1)
            self.assertEqual(open_payload["data"]["lines"], ["int flash_init(void) { return 0; }"])
            self.assertEqual(open_payload["recommended_next_tools"], ["read_evidence_pack"])

    def test_open_span_returns_invalid_input_when_request_exceeds_evidence_bounds(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            repo = build_scope_first_repo(Path(tmpdir))
            scan_repo(str(repo))
            plan_payload = slice_tools.plan_slice(str(repo), "Where is flash_init defined?")
            build_payload = build_evidence_pack(str(repo), plan_payload["data"]["slice_id"])

            payload = open_span(str(repo), build_payload["data"]["evidence_pack_id"], "src/flash.c", 1, 2)

            self.assertEqual(payload["status"], "error")
            self.assertEqual(payload["data"]["error"]["code"], "invalid_input")

    def test_open_span_returns_invalid_input_when_cited_file_has_drifted(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            repo = build_scope_first_repo(Path(tmpdir))
            scan_repo(str(repo))
            plan_payload = slice_tools.plan_slice(str(repo), "Where is flash_init defined?")
            build_payload = build_evidence_pack(str(repo), plan_payload["data"]["slice_id"])
            (repo / "src" / "flash.c").write_text("int flash_init(void) { return 9; }\n", encoding="utf-8")

            payload = open_span(str(repo), build_payload["data"]["evidence_pack_id"], "src/flash.c", 1, 1)

            self.assertEqual(payload["status"], "error")
            self.assertEqual(payload["data"]["error"]["code"], "invalid_input")

    def test_describe_anchor_reports_direct_call_relation_for_easyflash_fixture(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            repo = materialize_easyflash_repo(Path(tmpdir))
            created = scan_repo(str(repo))

            payload = describe_anchor(str(repo), "easyflash_init", created["data"]["scan_id"])

            self.assertEqual(payload["status"], "ok")
            self.assertIn("easyflash/src/easyflash.c", payload["data"]["description"])
            self.assertIn(
                "ef_port_init",
                {
                    relation["target_name"]
                    for relation in payload["data"]["relations"]
                    if relation["kind"] == "direct_call"
                },
            )

    def test_refresh_scan_returns_error_for_unknown_scan_id(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            repo = build_scope_first_repo(Path(tmpdir))

            payload = refresh_scan(str(repo), "scan_deadbeefcafe")

            self.assertEqual(payload["status"], "error")
            self.assertEqual(payload["data"]["error"]["code"], "not_found")
            self.assertEqual(payload["recommended_next_tools"], [])

    def test_refresh_scan_rejects_malformed_scan_id(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            repo = build_scope_first_repo(Path(tmpdir))

            payload = refresh_scan(str(repo), "../escape")

            self.assertEqual(payload["status"], "error")
            self.assertEqual(payload["data"]["error"]["code"], "invalid_input")

    def test_get_scan_status_returns_error_when_no_scan_exists(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            repo = build_scope_first_repo(Path(tmpdir))

            payload = get_scan_status(str(repo))

            self.assertEqual(payload["status"], "error")
            self.assertEqual(payload["data"]["error"]["code"], "not_found")

    def test_get_scan_status_rejects_malformed_scan_id(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            repo = build_scope_first_repo(Path(tmpdir))

            payload = get_scan_status(str(repo), "../escape")

            self.assertEqual(payload["status"], "error")
            self.assertEqual(payload["data"]["error"]["code"], "invalid_input")
