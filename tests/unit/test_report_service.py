import tempfile
import unittest
from pathlib import Path

from repo_analysis_tools.evidence.service import EvidenceService
from repo_analysis_tools.report.service import ReportService
from repo_analysis_tools.scan.service import ScanService
from repo_analysis_tools.slice.service import SliceService
from tests.fixtures.scope_first_repo import build_scope_first_repo


class ReportServiceTest(unittest.TestCase):
    def test_render_module_summary_persists_markdown_and_metadata(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            repo = build_scope_first_repo(Path(tmpdir))
            ScanService().scan(repo)
            slice_manifest = SliceService().plan(repo, "Where is flash_init defined?")
            evidence_pack = EvidenceService().build(repo, slice_manifest.slice_id)

            artifact = ReportService().render_module_summary(repo, evidence_pack.evidence_pack_id, "flash")

            self.assertRegex(artifact.report_id, r"^report_[0-9a-f]{12}$")
            self.assertEqual(artifact.document_type, "module-summary")
            self.assertIn("```mermaid", artifact.markdown)
            self.assertTrue(Path(artifact.markdown_path).is_file())

    def test_render_focus_report_supports_issue_analysis_document_type(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            repo = build_scope_first_repo(Path(tmpdir))
            ScanService().scan(repo)
            slice_manifest = SliceService().plan(repo, "Where is flash_init defined?")
            evidence_pack = EvidenceService().build(repo, slice_manifest.slice_id)

            artifact = ReportService().render_focus_report(
                repo,
                evidence_pack.evidence_pack_id,
                document_type="issue-analysis",
            )

            self.assertEqual(artifact.document_type, "issue-analysis")
            self.assertIn("# ", artifact.markdown)

    def test_render_analysis_outline_persists_design_note(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            repo = build_scope_first_repo(Path(tmpdir))
            ScanService().scan(repo)

            artifact = ReportService().render_analysis_outline(repo, "flash init flow")

            self.assertEqual(artifact.document_type, "design-note")
            self.assertTrue(Path(artifact.markdown_path).is_file())
