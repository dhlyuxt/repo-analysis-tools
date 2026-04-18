import unittest

from repo_analysis_tools.mcp.tools.shared import stub_payload
from tests.golden.harness import assert_matches_fixture, load_fixture


class ContractGoldenTest(unittest.TestCase):
    maxDiff = None

    def test_scan_repo_payload_matches_golden_fixture(self) -> None:
        payload = stub_payload(
            "scan_repo",
            target_repo="/tmp/demo-repo",
            scan_id="scan_stub000001",
        )

        assert_matches_fixture(self, "scan_repo.json", payload)

    def test_scan_repo_fixture_tracks_declared_scan_fields(self) -> None:
        fixture = load_fixture("scan_repo.json")

        self.assertEqual(
            set(fixture["data"]),
            {"target_repo", "runtime_root", "scan_id"},
        )
