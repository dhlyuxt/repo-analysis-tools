import unittest
from copy import deepcopy
from datetime import datetime, timezone
import tempfile
from pathlib import Path
from unittest.mock import patch

from repo_analysis_tools.mcp.contracts import CONTRACT_BY_NAME
from repo_analysis_tools.mcp.tools.evidence_tools import build_evidence_pack, read_evidence_pack
from repo_analysis_tools.mcp.tools.scan_tools import scan_repo
from repo_analysis_tools.mcp.tools.slice_tools import plan_slice
from tests.fixtures.scope_first_repo import build_scope_first_repo
from tests.golden.harness import assert_matches_fixture, load_fixture


class ContractGoldenTest(unittest.TestCase):
    maxDiff = None

    def _deterministic_scan_id(self) -> str:
        return "scan_000000000001"

    def _deterministic_slice_id(self) -> str:
        return "slice_000000000001"

    def _deterministic_evidence_pack_id(self) -> str:
        return "evidence_pack_000000000001"

    def _deterministic_make_stable_id(self, kind) -> str:
        return {
            "scan": self._deterministic_scan_id(),
            "slice": self._deterministic_slice_id(),
            "evidence_pack": self._deterministic_evidence_pack_id(),
        }[kind.value]

    def _normalize_repo_paths(self, payload: dict[str, object]) -> dict[str, object]:
        normalized = deepcopy(payload)
        data = normalized["data"]
        if "target_repo" in data:
            data["target_repo"] = "<repo>"
        if "runtime_root" in data:
            data["runtime_root"] = "<repo>/.codewiki"
        if "repo_root" in data:
            data["repo_root"] = "<repo>"
        return normalized

    def test_scan_repo_payload_matches_golden_fixture(self) -> None:
        fixed_completed_at = datetime(2026, 4, 19, 3, 13, 48, 74284, tzinfo=timezone.utc)

        with tempfile.TemporaryDirectory() as tmpdir:
            repo = build_scope_first_repo(Path(tmpdir))
            with (
                patch("repo_analysis_tools.scan.service.make_stable_id", side_effect=self._deterministic_make_stable_id),
                patch("repo_analysis_tools.scan.service.datetime") as mock_datetime,
            ):
                mock_datetime.now.return_value = fixed_completed_at
                payload = scan_repo(str(repo))

        assert_matches_fixture(self, "scan_repo.json", self._normalize_repo_paths(payload))

    def test_read_evidence_pack_payload_matches_golden_fixture(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            repo = build_scope_first_repo(Path(tmpdir))
            with (
                patch("repo_analysis_tools.scan.service.make_stable_id", side_effect=self._deterministic_make_stable_id),
                patch("repo_analysis_tools.slice.service.make_stable_id", side_effect=self._deterministic_make_stable_id),
                patch("repo_analysis_tools.evidence.service.make_stable_id", side_effect=self._deterministic_make_stable_id),
                patch("repo_analysis_tools.scan.service.datetime") as mock_datetime,
            ):
                mock_datetime.now.return_value = datetime(2026, 4, 19, 3, 13, 48, 74284, tzinfo=timezone.utc)
                scan_payload = scan_repo(str(repo))
                plan_payload = plan_slice(str(repo), "Where is flash_init defined?")
                build_payload = build_evidence_pack(str(repo), plan_payload["data"]["slice_id"])
                payload = read_evidence_pack(str(repo), build_payload["data"]["evidence_pack_id"])

        self.assertEqual(scan_payload["data"]["scan_id"], self._deterministic_scan_id())
        self.assertEqual(plan_payload["data"]["slice_id"], self._deterministic_slice_id())
        self.assertEqual(build_payload["data"]["evidence_pack_id"], self._deterministic_evidence_pack_id())
        assert_matches_fixture(self, "read_evidence_pack_scope_first.json", self._normalize_repo_paths(payload))

    def test_scan_repo_fixture_tracks_declared_scan_fields(self) -> None:
        fixture = load_fixture("scan_repo.json")

        self.assertEqual(
            set(fixture["data"]),
            set(CONTRACT_BY_NAME["scan_repo"].output_schema),
        )
