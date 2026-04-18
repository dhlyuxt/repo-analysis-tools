import unittest

from repo_analysis_tools.mcp.contracts import CONTRACT_BY_NAME, DOMAIN_CONTRACTS
from repo_analysis_tools.mcp.tools.export_tools import export_scope_snapshot
from repo_analysis_tools.mcp.tools.scan_tools import get_scan_status
from repo_analysis_tools.mcp.tools.shared import stub_payload


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


class ToolContractsTest(unittest.TestCase):
    def test_every_required_domain_group_exists(self) -> None:
        self.assertEqual(set(DOMAIN_CONTRACTS), EXPECTED_DOMAINS)
        for domain_name, contracts in DOMAIN_CONTRACTS.items():
            self.assertEqual(len(contracts), 3, domain_name)

    def test_every_contract_declares_shape_and_failure_modes(self) -> None:
        for contract in CONTRACT_BY_NAME.values():
            self.assertTrue(contract.input_schema, contract.name)
            self.assertTrue(contract.output_schema, contract.name)
            self.assertTrue(contract.failure_modes, contract.name)

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
        scan_status_payload = get_scan_status("/tmp/demo-repo")
        export_payload = export_scope_snapshot("/tmp/demo-repo")

        self.assertRegex(scan_status_payload["data"]["scan_id"], r"^scan_[0-9a-f]{12}$")
        self.assertRegex(export_payload["data"]["scan_id"], r"^scan_[0-9a-f]{12}$")

    def test_stub_outputs_do_not_include_undeclared_contract_version(self) -> None:
        payload = stub_payload("get_scan_status", target_repo="/tmp/demo-repo")
        tool_payload = get_scan_status("/tmp/demo-repo")

        self.assertNotIn("contract_version", payload["data"])
        self.assertNotIn("contract_version", tool_payload["data"])
