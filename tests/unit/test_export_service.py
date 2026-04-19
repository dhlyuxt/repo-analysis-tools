import json
import tempfile
import unittest
from pathlib import Path

from repo_analysis_tools.evidence.service import EvidenceService
from repo_analysis_tools.export.service import ExportService
from repo_analysis_tools.report.service import ReportService
from repo_analysis_tools.scan.service import ScanService
from repo_analysis_tools.slice.service import SliceService
from tests.fixtures.scope_first_repo import build_scope_first_repo


class ExportServiceTest(unittest.TestCase):
    def test_export_scope_snapshot_persists_manifest_and_payload(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            repo = build_scope_first_repo(Path(tmpdir))
            scan_snapshot = ScanService().scan(repo)

            artifact = ExportService().export_scope_snapshot(repo, scan_snapshot.scan_id)

            self.assertRegex(artifact.export_id, r"^export_[0-9a-f]{12}$")
            self.assertEqual(artifact.export_kind, "scope-snapshot")
            self.assertEqual(artifact.source_kind, "scope")
            self.assertEqual(artifact.source_id, scan_snapshot.scan_id)
            self.assertEqual(artifact.owner_tool, "export_scope_snapshot")
            self.assertTrue(Path(artifact.manifest_path).is_file())
            self.assertTrue(Path(artifact.payload_path).is_file())
            self.assertEqual(artifact.freshness.state, "fresh")

            manifest = json.loads(Path(artifact.manifest_path).read_text(encoding="utf-8"))
            payload = json.loads(Path(artifact.payload_path).read_text(encoding="utf-8"))

            self.assertEqual(manifest["source"]["kind"], "scope")
            self.assertEqual(manifest["freshness"]["state"], "fresh")
            self.assertEqual(payload["scan_id"], scan_snapshot.scan_id)

    def test_export_analysis_bundle_copies_report_markdown_and_provenance(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            repo = build_scope_first_repo(Path(tmpdir))
            ScanService().scan(repo)
            slice_manifest = SliceService().plan(repo, "Where is flash_init defined?")
            evidence_pack = EvidenceService().build(repo, slice_manifest.slice_id)
            report = ReportService().render_module_summary(repo, evidence_pack.evidence_pack_id, "flash")

            artifact = ExportService().export_analysis_bundle(repo, report.report_id)

            self.assertEqual(artifact.export_kind, "analysis-bundle")
            self.assertEqual(artifact.source_kind, "report")
            self.assertEqual(artifact.source_id, report.report_id)
            self.assertEqual(artifact.owner_tool, "export_analysis_bundle")
            self.assertEqual(artifact.freshness.state, "fresh")
            self.assertTrue(Path(artifact.manifest_path).is_file())
            self.assertTrue(Path(artifact.payload_path).is_file())
            self.assertTrue(any(path.endswith("report.md") for path in artifact.copied_paths))

            manifest = json.loads(Path(artifact.manifest_path).read_text(encoding="utf-8"))
            payload = json.loads(Path(artifact.payload_path).read_text(encoding="utf-8"))
            copied_markdown_path = next(
                path for path in artifact.copied_paths
                if path.endswith("report.md")
            )

            self.assertEqual(manifest["source"]["kind"], "report")
            self.assertEqual(manifest["source"]["id"], report.report_id)
            self.assertEqual(payload["evidence_pack_id"], evidence_pack.evidence_pack_id)
            self.assertEqual(payload["scan_id"], evidence_pack.scan_id)
            self.assertIn("# Module Summary: flash", Path(copied_markdown_path).read_text(encoding="utf-8"))

    def test_export_analysis_bundle_becomes_stale_when_report_markdown_drifts(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            repo = build_scope_first_repo(Path(tmpdir))
            ScanService().scan(repo)
            slice_manifest = SliceService().plan(repo, "Where is flash_init defined?")
            evidence_pack = EvidenceService().build(repo, slice_manifest.slice_id)
            report = ReportService().render_module_summary(repo, evidence_pack.evidence_pack_id, "flash")

            report_markdown_path = Path(report.markdown_path)
            report_markdown_path.write_text(
                report_markdown_path.read_text(encoding="utf-8") + "\n<!-- drift -->\n",
                encoding="utf-8",
            )

            artifact = ExportService().export_analysis_bundle(repo, report.report_id)

            self.assertEqual(artifact.freshness.state, "stale")
            self.assertTrue(
                any(
                    path.endswith(f"report/rendered/{report.report_id}.md")
                    for path in artifact.freshness.drifted_paths
                ),
                artifact.freshness.drifted_paths,
            )
