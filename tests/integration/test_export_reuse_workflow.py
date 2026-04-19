import json
import tempfile
import unittest
from pathlib import Path

from repo_analysis_tools.mcp.tools.anchors_tools import describe_anchor
from repo_analysis_tools.mcp.tools.evidence_tools import build_evidence_pack
from repo_analysis_tools.mcp.tools.export_tools import (
    export_analysis_bundle,
    export_evidence_bundle,
    export_scope_snapshot,
)
from repo_analysis_tools.mcp.tools.impact_tools import impact_from_paths
from repo_analysis_tools.mcp.tools.report_tools import render_focus_report, render_module_summary
from repo_analysis_tools.mcp.tools.scan_tools import scan_repo
from repo_analysis_tools.mcp.tools.slice_tools import plan_slice
from tests.fixtures.scope_first_repo import build_scope_first_repo


class ExportReuseWorkflowTest(unittest.TestCase):
    def test_exported_manifests_recover_ids_for_follow_up_workflows(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            repo = build_scope_first_repo(Path(tmpdir))
            scan_payload = scan_repo(str(repo))
            slice_payload = plan_slice(str(repo), "Where is flash_init defined?")
            evidence_payload = build_evidence_pack(str(repo), slice_payload["data"]["slice_id"])
            report_payload = render_module_summary(
                str(repo),
                evidence_payload["data"]["evidence_pack_id"],
                "flash",
            )

            scope_export = export_scope_snapshot(str(repo), scan_payload["data"]["scan_id"])
            evidence_export = export_evidence_bundle(
                str(repo),
                evidence_payload["data"]["evidence_pack_id"],
            )
            analysis_export = export_analysis_bundle(str(repo), report_payload["data"]["report_id"])

            scope_manifest = json.loads(Path(scope_export["data"]["manifest_path"]).read_text(encoding="utf-8"))
            evidence_manifest = json.loads(
                Path(evidence_export["data"]["manifest_path"]).read_text(encoding="utf-8")
            )
            analysis_manifest = json.loads(
                Path(analysis_export["data"]["manifest_path"]).read_text(encoding="utf-8")
            )

            self.assertEqual(scope_manifest["export_kind"], "scope-snapshot")
            self.assertEqual(scope_manifest["freshness"]["state"], "fresh")
            self.assertEqual(evidence_manifest["export_kind"], "evidence-bundle")
            self.assertEqual(evidence_manifest["freshness"]["state"], "fresh")
            self.assertEqual(analysis_manifest["export_kind"], "analysis-bundle")
            self.assertEqual(analysis_manifest["freshness"]["state"], "fresh")

            repo_follow_up = describe_anchor(str(repo), "flash_init", scope_manifest["scan_id"])
            impact_follow_up = impact_from_paths(str(repo), ["src/flash.c"], scope_manifest["scan_id"])
            writing_follow_up = render_focus_report(
                str(repo),
                evidence_manifest["evidence_pack_id"],
                "issue-analysis",
            )

            self.assertEqual(repo_follow_up["status"], "ok")
            self.assertEqual(repo_follow_up["data"]["anchor_name"], "flash_init")
            self.assertEqual(impact_follow_up["status"], "ok")
            self.assertEqual(impact_follow_up["data"]["scan_id"], scope_manifest["scan_id"])
            self.assertEqual(writing_follow_up["status"], "ok")
            self.assertEqual(
                writing_follow_up["data"]["evidence_pack_id"],
                evidence_manifest["evidence_pack_id"],
            )
            self.assertEqual(analysis_manifest["report_id"], report_payload["data"]["report_id"])
            self.assertEqual(
                analysis_manifest["artifact"]["document_type"],
                "module-summary",
            )
            self.assertEqual(
                analysis_manifest["paths"]["copied_markdown_path"],
                analysis_export["data"]["copied_markdown_path"],
            )

            copied_markdown = Path(analysis_export["data"]["copied_markdown_path"]).read_text(encoding="utf-8")
            self.assertIn("# Module Summary: flash", copied_markdown)
            self.assertIn("```mermaid", copied_markdown)
