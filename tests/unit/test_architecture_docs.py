import unittest
from pathlib import Path

from repo_analysis_tools.core.errors import ErrorCode
from repo_analysis_tools.core.ids import StableIdKind
from repo_analysis_tools.mcp.contracts import CONTRACT_BY_NAME, DOMAIN_CONTRACTS
from repo_analysis_tools.storage.contracts import STORAGE_BOUNDARIES


REPO_ROOT = Path(__file__).resolve().parents[2]
ARCHITECTURE_DOC = REPO_ROOT / "docs" / "architecture.md"
CONTRACT_DOC = REPO_ROOT / "docs" / "contracts" / "mcp-tool-contracts.md"

EXPECTED_ARCHITECTURE_BOUNDARIES = {
    "core",
    "storage",
    "scan",
    "scope",
    "anchors",
    "slice",
    "evidence",
    "impact",
    "report",
    "export",
    "mcp",
    "skills",
    "doc_specs",
    "doc_dsl",
    "renderers",
}

EXPECTED_ID_LABELS = {
    StableIdKind.SCAN: "scan_",
    StableIdKind.SLICE: "slice_",
    StableIdKind.EVIDENCE_PACK: "evidence_pack_",
    StableIdKind.REPORT: "report_",
    StableIdKind.EXPORT: "export_",
}


class ArchitectureDocsTest(unittest.TestCase):
    def read_text(self, path: Path) -> str:
        self.assertTrue(path.exists(), f"missing documentation file: {path.relative_to(REPO_ROOT)}")
        return path.read_text(encoding="utf-8")

    def test_architecture_doc_records_m1_boundaries_runtime_and_errors(self) -> None:
        document = self.read_text(ARCHITECTURE_DOC)

        self.assertIn("<target_repo>/.codewiki/", document)
        self.assertIn("recommended_next_tools", document)

        for boundary in EXPECTED_ARCHITECTURE_BOUNDARIES:
            self.assertIn(f"`{boundary}`", document, boundary)

        for storage_boundary in STORAGE_BOUNDARIES.values():
            self.assertIn(f"`{storage_boundary.domain}`", document, storage_boundary.domain)
            self.assertIn(f"`{storage_boundary.directory_name}`", document, storage_boundary.domain)

        for error_code in ErrorCode:
            self.assertIn(f"`{error_code.value}`", document, error_code.value)

        for id_prefix in EXPECTED_ID_LABELS.values():
            self.assertIn(f"`{id_prefix}`", document, id_prefix)

    def test_contract_doc_lists_every_domain_tool_and_standard_envelope(self) -> None:
        document = self.read_text(CONTRACT_DOC)

        self.assertIn("`schema_version`", document)
        self.assertIn("`status`", document)
        self.assertIn("`data`", document)
        self.assertIn("`messages`", document)
        self.assertIn("`recommended_next_tools`", document)

        for error_code in ErrorCode:
            self.assertIn(f"`{error_code.value}`", document, error_code.value)

        for domain_name, contracts in DOMAIN_CONTRACTS.items():
            self.assertIn(f"## `{domain_name}`", document, domain_name)
            for contract in contracts:
                self.assertIn(f"`{contract.name}`", document, contract.name)
                for field_name in contract.input_schema:
                    self.assertIn(f"`{field_name}`", document, f"{contract.name}:{field_name}")
                for field_name in contract.output_schema:
                    self.assertIn(f"`{field_name}`", document, f"{contract.name}:{field_name}")

    def test_contract_doc_mentions_every_declared_stable_id_family(self) -> None:
        document = self.read_text(CONTRACT_DOC)

        for id_kind in {
            stable_id
            for contract in CONTRACT_BY_NAME.values()
            for stable_id in contract.stable_ids
        }:
            self.assertIn(f"`{id_kind.value}`", document, id_kind.value)
