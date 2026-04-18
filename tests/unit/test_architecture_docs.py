import re
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
    "tests",
}

EXPECTED_ID_LABELS = {
    StableIdKind.SCAN: "scan_",
    StableIdKind.SLICE: "slice_",
    StableIdKind.EVIDENCE_PACK: "evidence_pack_",
    StableIdKind.REPORT: "report_",
    StableIdKind.EXPORT: "export_",
}


class ArchitectureDocsTest(unittest.TestCase):
    maxDiff = None

    def read_text(self, path: Path) -> str:
        self.assertTrue(path.exists(), f"missing documentation file: {path.relative_to(REPO_ROOT)}")
        return path.read_text(encoding="utf-8")

    def section_text(self, document: str, heading: str) -> str:
        pattern = re.compile(
            rf"^## {re.escape(heading)}\n(?P<body>.*?)(?=^## |\Z)",
            re.MULTILINE | re.DOTALL,
        )
        match = pattern.search(document)
        self.assertIsNotNone(match, f"missing section: {heading}")
        return match.group("body")

    def parse_markdown_row(self, line: str) -> list[str]:
        self.assertTrue(line.startswith("|"), f"not a markdown table row: {line}")
        return [cell.strip() for cell in line.strip().strip("|").split("|")]

    def parse_markdown_table(self, section: str) -> tuple[list[str], list[dict[str, str]]]:
        table_lines: list[str] = []
        for line in section.splitlines():
            stripped = line.strip()
            if stripped.startswith("|"):
                table_lines.append(stripped)
            elif table_lines:
                break

        self.assertGreaterEqual(len(table_lines), 3, "expected a markdown table with header and rows")

        header = self.parse_markdown_row(table_lines[0])
        separator = self.parse_markdown_row(table_lines[1])
        self.assertEqual(len(header), len(separator), "table separator width drifted from header width")

        rows = [dict(zip(header, self.parse_markdown_row(line), strict=True)) for line in table_lines[2:]]
        return header, rows

    def parse_backticked_values(self, cell: str) -> list[str]:
        if cell.strip() == "none":
            return []
        return re.findall(r"`([^`]+)`", cell)

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
            section = self.section_text(document, f"`{domain_name}`")
            header, rows = self.parse_markdown_table(section)
            self.assertEqual(
                header,
                ["Tool", "Inputs", "Outputs", "Stable IDs", "Failure modes", "Next tools"],
                domain_name,
            )

            row_by_tool = {}
            for row in rows:
                tool_names = self.parse_backticked_values(row["Tool"])
                self.assertEqual(len(tool_names), 1, row)
                row_by_tool[tool_names[0]] = row

            self.assertEqual(set(row_by_tool), {contract.name for contract in contracts}, domain_name)

            for contract in contracts:
                row = row_by_tool[contract.name]
                self.assertEqual(
                    self.parse_backticked_values(row["Inputs"]),
                    list(contract.input_schema),
                    f"{domain_name}:{contract.name}:inputs",
                )
                self.assertEqual(
                    self.parse_backticked_values(row["Outputs"]),
                    list(contract.output_schema),
                    f"{domain_name}:{contract.name}:outputs",
                )
                self.assertEqual(
                    self.parse_backticked_values(row["Stable IDs"]),
                    [stable_id.value for stable_id in contract.stable_ids],
                    f"{domain_name}:{contract.name}:stable_ids",
                )
                self.assertEqual(
                    self.parse_backticked_values(row["Failure modes"]),
                    [failure_mode.value for failure_mode in contract.failure_modes],
                    f"{domain_name}:{contract.name}:failure_modes",
                )
                self.assertEqual(
                    self.parse_backticked_values(row["Next tools"]),
                    list(contract.recommended_next_tools),
                    f"{domain_name}:{contract.name}:recommended_next_tools",
                )

    def test_contract_doc_mentions_every_declared_stable_id_family(self) -> None:
        document = self.read_text(CONTRACT_DOC)

        for id_kind in {
            stable_id
            for contract in CONTRACT_BY_NAME.values()
            for stable_id in contract.stable_ids
        }:
            self.assertIn(f"`{id_kind.value}`", document, id_kind.value)
