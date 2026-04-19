import unittest
from copy import deepcopy
from datetime import datetime, timezone
import tempfile
from pathlib import Path
from unittest.mock import patch

from repo_analysis_tools.mcp.contracts import CONTRACT_BY_NAME
from repo_analysis_tools.mcp.tools.evidence_tools import build_evidence_pack, read_evidence_pack
from repo_analysis_tools.mcp.tools import export_tools
from repo_analysis_tools.mcp.tools.impact_tools import impact_from_paths, summarize_impact
from repo_analysis_tools.mcp.tools import report_tools
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

    def _deterministic_impact_id(self) -> str:
        return "impact_000000000001"

    def _deterministic_report_id(self) -> str:
        return "report_000000000001"

    def _deterministic_export_id(self) -> str:
        return "export_000000000001"

    def _deterministic_make_stable_id(self, kind) -> str:
        return {
            "scan": self._deterministic_scan_id(),
            "slice": self._deterministic_slice_id(),
            "impact": self._deterministic_impact_id(),
            "evidence_pack": self._deterministic_evidence_pack_id(),
            "report": self._deterministic_report_id(),
            "export": self._deterministic_export_id(),
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
        if "markdown_path" in data and isinstance(data["markdown_path"], str):
            data["markdown_path"] = data["markdown_path"].replace(
                str(Path(data["markdown_path"]).parents[3]),
                "<repo>",
            )
        for path_field in ("manifest_path", "payload_path", "copied_markdown_path"):
            if path_field in data and isinstance(data[path_field], str):
                data[path_field] = data[path_field].replace(
                    str(Path(data[path_field]).parents[4]),
                    "<repo>",
                )
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
                patch("repo_analysis_tools.impact.service.make_stable_id", side_effect=self._deterministic_make_stable_id),
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

    def test_summarize_impact_payload_matches_golden_fixture(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            repo = build_scope_first_repo(Path(tmpdir))
            with (
                patch("repo_analysis_tools.scan.service.make_stable_id", side_effect=self._deterministic_make_stable_id),
                patch("repo_analysis_tools.slice.service.make_stable_id", side_effect=self._deterministic_make_stable_id),
                patch("repo_analysis_tools.evidence.service.make_stable_id", side_effect=self._deterministic_make_stable_id),
                patch("repo_analysis_tools.impact.service.make_stable_id", side_effect=self._deterministic_make_stable_id),
                patch("repo_analysis_tools.scan.service.datetime") as mock_datetime,
            ):
                mock_datetime.now.return_value = datetime(2026, 4, 19, 3, 13, 48, 74284, tzinfo=timezone.utc)
                scan_repo(str(repo))
                impact_payload = impact_from_paths(str(repo), ["src/flash.c"])
                payload = summarize_impact(str(repo), impact_payload["data"]["impact_id"])

        self.assertEqual(impact_payload["data"]["impact_id"], self._deterministic_impact_id())
        assert_matches_fixture(self, "summarize_impact_scope_first.json", self._normalize_repo_paths(payload))

    def test_render_module_summary_payload_matches_golden_fixture(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            repo = build_scope_first_repo(Path(tmpdir))
            with (
                patch("repo_analysis_tools.scan.service.make_stable_id", side_effect=self._deterministic_make_stable_id),
                patch("repo_analysis_tools.slice.service.make_stable_id", side_effect=self._deterministic_make_stable_id),
                patch("repo_analysis_tools.evidence.service.make_stable_id", side_effect=self._deterministic_make_stable_id),
                patch("repo_analysis_tools.report.service.make_stable_id", side_effect=self._deterministic_make_stable_id),
                patch("repo_analysis_tools.scan.service.datetime") as mock_datetime,
            ):
                mock_datetime.now.return_value = datetime(2026, 4, 19, 3, 13, 48, 74284, tzinfo=timezone.utc)
                scan_repo(str(repo))
                plan_payload = plan_slice(str(repo), "Where is flash_init defined?")
                build_payload = build_evidence_pack(str(repo), plan_payload["data"]["slice_id"])
                payload = report_tools.render_module_summary(
                    str(repo),
                    build_payload["data"]["evidence_pack_id"],
                    "flash",
                )

        assert_matches_fixture(
            self,
            "render_module_summary_scope_first.json",
            self._normalize_repo_paths(payload),
        )

    def test_export_scope_snapshot_payload_matches_golden_fixture(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            repo = build_scope_first_repo(Path(tmpdir))
            with (
                patch("repo_analysis_tools.scan.service.make_stable_id", side_effect=self._deterministic_make_stable_id),
                patch("repo_analysis_tools.export.service.make_stable_id", side_effect=self._deterministic_make_stable_id),
                patch("repo_analysis_tools.scan.service.datetime") as mock_datetime,
            ):
                mock_datetime.now.return_value = datetime(2026, 4, 19, 3, 13, 48, 74284, tzinfo=timezone.utc)
                scan_payload = scan_repo(str(repo))
                payload = export_tools.export_scope_snapshot(
                    str(repo),
                    scan_payload["data"]["scan_id"],
                )

        assert_matches_fixture(
            self,
            "export_scope_snapshot_scope_first.json",
            self._normalize_repo_paths(payload),
        )

    def test_export_evidence_bundle_payload_matches_golden_fixture(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            repo = build_scope_first_repo(Path(tmpdir))
            with (
                patch("repo_analysis_tools.scan.service.make_stable_id", side_effect=self._deterministic_make_stable_id),
                patch("repo_analysis_tools.slice.service.make_stable_id", side_effect=self._deterministic_make_stable_id),
                patch("repo_analysis_tools.evidence.service.make_stable_id", side_effect=self._deterministic_make_stable_id),
                patch("repo_analysis_tools.export.service.make_stable_id", side_effect=self._deterministic_make_stable_id),
                patch("repo_analysis_tools.scan.service.datetime") as mock_datetime,
            ):
                mock_datetime.now.return_value = datetime(2026, 4, 19, 3, 13, 48, 74284, tzinfo=timezone.utc)
                scan_repo(str(repo))
                plan_payload = plan_slice(str(repo), "Where is flash_init defined?")
                build_payload = build_evidence_pack(str(repo), plan_payload["data"]["slice_id"])
                payload = export_tools.export_evidence_bundle(
                    str(repo),
                    build_payload["data"]["evidence_pack_id"],
                )

        assert_matches_fixture(
            self,
            "export_evidence_bundle_scope_first.json",
            self._normalize_repo_paths(payload),
        )

    def test_export_analysis_bundle_payload_matches_golden_fixture(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            repo = build_scope_first_repo(Path(tmpdir))
            with (
                patch("repo_analysis_tools.scan.service.make_stable_id", side_effect=self._deterministic_make_stable_id),
                patch("repo_analysis_tools.slice.service.make_stable_id", side_effect=self._deterministic_make_stable_id),
                patch("repo_analysis_tools.evidence.service.make_stable_id", side_effect=self._deterministic_make_stable_id),
                patch("repo_analysis_tools.report.service.make_stable_id", side_effect=self._deterministic_make_stable_id),
                patch("repo_analysis_tools.export.service.make_stable_id", side_effect=self._deterministic_make_stable_id),
                patch("repo_analysis_tools.scan.service.datetime") as mock_datetime,
            ):
                mock_datetime.now.return_value = datetime(2026, 4, 19, 3, 13, 48, 74284, tzinfo=timezone.utc)
                scan_repo(str(repo))
                plan_payload = plan_slice(str(repo), "Where is flash_init defined?")
                build_payload = build_evidence_pack(str(repo), plan_payload["data"]["slice_id"])
                report_payload = report_tools.render_module_summary(
                    str(repo),
                    build_payload["data"]["evidence_pack_id"],
                    "flash",
                )
                payload = export_tools.export_analysis_bundle(
                    str(repo),
                    report_payload["data"]["report_id"],
                )

        assert_matches_fixture(
            self,
            "export_analysis_bundle_scope_first.json",
            self._normalize_repo_paths(payload),
        )

    def test_scan_repo_fixture_tracks_declared_scan_fields(self) -> None:
        fixture = load_fixture("scan_repo.json")

        self.assertEqual(
            set(fixture["data"]),
            set(CONTRACT_BY_NAME["scan_repo"].output_schema),
        )
