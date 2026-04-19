import tempfile
import unittest
from pathlib import Path

from repo_analysis_tools.mcp.tools.evidence_tools import build_evidence_pack
from repo_analysis_tools.mcp.tools.report_tools import (
    render_analysis_outline,
    render_focus_report,
    render_module_summary,
)
from repo_analysis_tools.mcp.tools.scan_tools import scan_repo
from repo_analysis_tools.mcp.tools.slice_tools import plan_slice
from tests.fixtures.scope_first_repo import build_scope_first_repo


class AnalysisWritingWorkflowTest(unittest.TestCase):
    def test_scope_first_repo_renders_all_m4_document_types(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            repo = build_scope_first_repo(Path(tmpdir))

            scan_payload = scan_repo(str(repo))
            plan_payload = plan_slice(str(repo), "Where is flash_init defined?")
            evidence_payload = build_evidence_pack(str(repo), plan_payload["data"]["slice_id"])
            module_payload = render_module_summary(
                str(repo),
                evidence_payload["data"]["evidence_pack_id"],
                "flash",
            )
            issue_payload = render_focus_report(
                str(repo),
                evidence_payload["data"]["evidence_pack_id"],
                "issue-analysis",
            )
            review_payload = render_focus_report(
                str(repo),
                evidence_payload["data"]["evidence_pack_id"],
            )
            outline_payload = render_analysis_outline(str(repo), "flash init flow")

            self.assertEqual(scan_payload["status"], "ok")
            self.assertEqual(module_payload["status"], "ok")
            self.assertEqual(module_payload["data"]["document_type"], "module-summary")
            self.assertTrue(Path(module_payload["data"]["markdown_path"]).is_file())
            self.assertEqual(issue_payload["status"], "ok")
            self.assertEqual(issue_payload["data"]["document_type"], "issue-analysis")
            self.assertTrue(Path(issue_payload["data"]["markdown_path"]).is_file())
            self.assertEqual(review_payload["status"], "ok")
            self.assertEqual(review_payload["data"]["document_type"], "review-report")
            self.assertTrue(Path(review_payload["data"]["markdown_path"]).is_file())
            self.assertEqual(outline_payload["status"], "ok")
            self.assertEqual(outline_payload["data"]["document_type"], "design-note")
            self.assertTrue(Path(outline_payload["data"]["markdown_path"]).is_file())
