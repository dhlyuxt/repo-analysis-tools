import unittest
from pathlib import Path

import repo_analysis_tools


ROOT = Path(__file__).resolve().parents[2]
EXPECTED_DIRECTORIES = [
    ROOT / "src" / "repo_analysis_tools" / "core",
    ROOT / "src" / "repo_analysis_tools" / "storage",
    ROOT / "src" / "repo_analysis_tools" / "scan",
    ROOT / "src" / "repo_analysis_tools" / "scope",
    ROOT / "src" / "repo_analysis_tools" / "anchors",
    ROOT / "src" / "repo_analysis_tools" / "slice",
    ROOT / "src" / "repo_analysis_tools" / "evidence",
    ROOT / "src" / "repo_analysis_tools" / "impact",
    ROOT / "src" / "repo_analysis_tools" / "report",
    ROOT / "src" / "repo_analysis_tools" / "export",
    ROOT / "src" / "repo_analysis_tools" / "mcp",
    ROOT / "src" / "repo_analysis_tools" / "skills",
    ROOT / "src" / "repo_analysis_tools" / "doc_specs",
    ROOT / "src" / "repo_analysis_tools" / "doc_dsl",
    ROOT / "src" / "repo_analysis_tools" / "renderers",
    ROOT / "tests" / "unit",
    ROOT / "tests" / "contract",
    ROOT / "tests" / "golden" / "fixtures",
    ROOT / "tests" / "fixtures",
    ROOT / "tests" / "integration",
    ROOT / "tests" / "e2e",
    ROOT / "docs" / "contracts",
]
EXPECTED_FILES = [
    ROOT / ".codex" / "config.toml",
    ROOT / ".mcp.json",
    ROOT / ".agents" / "skills" / "repo-doc-writer" / "SKILL.md",
    ROOT / ".agents" / "skills" / "repo-understand" / "SKILL.md",
    ROOT / ".claude" / "skills" / "repo-doc-writer" / "SKILL.md",
    ROOT / ".claude" / "skills" / "repo-understand" / "SKILL.md",
    ROOT / "docs" / "self-use-launch.md",
    ROOT / "tools" / "run_self_use_demo.py",
]

UNEXPECTED_FILES = [
    ROOT / "src" / "repo_analysis_tools" / "mcp" / "contracts" / "anchors.py",
    ROOT / "src" / "repo_analysis_tools" / "mcp" / "contracts" / "evidence.py",
    ROOT / "src" / "repo_analysis_tools" / "mcp" / "contracts" / "export.py",
    ROOT / "src" / "repo_analysis_tools" / "mcp" / "contracts" / "impact.py",
    ROOT / "src" / "repo_analysis_tools" / "mcp" / "contracts" / "report.py",
    ROOT / "src" / "repo_analysis_tools" / "mcp" / "contracts" / "scope.py",
    ROOT / "src" / "repo_analysis_tools" / "mcp" / "contracts" / "slice.py",
    ROOT / "src" / "repo_analysis_tools" / "mcp" / "tools" / "anchors_tools.py",
    ROOT / "src" / "repo_analysis_tools" / "mcp" / "tools" / "evidence_tools.py",
    ROOT / "src" / "repo_analysis_tools" / "mcp" / "tools" / "export_tools.py",
    ROOT / "src" / "repo_analysis_tools" / "mcp" / "tools" / "impact_tools.py",
    ROOT / "src" / "repo_analysis_tools" / "mcp" / "tools" / "report_tools.py",
    ROOT / "src" / "repo_analysis_tools" / "mcp" / "tools" / "scope_tools.py",
    ROOT / "src" / "repo_analysis_tools" / "mcp" / "tools" / "slice_tools.py",
    ROOT / ".agents" / "skills" / "analysis-writing" / "SKILL.md",
    ROOT / ".agents" / "skills" / "analysis-maintenance" / "SKILL.md",
    ROOT / ".agents" / "skills" / "change-impact" / "SKILL.md",
    ROOT / ".claude" / "skills" / "analysis-writing" / "SKILL.md",
    ROOT / ".claude" / "skills" / "analysis-maintenance" / "SKILL.md",
    ROOT / ".claude" / "skills" / "change-impact" / "SKILL.md",
    ROOT / "tests" / "integration" / "test_analysis_writing_workflow.py",
    ROOT / "tests" / "integration" / "test_change_impact_workflow.py",
    ROOT / "tests" / "integration" / "test_export_reuse_workflow.py",
    ROOT / "tests" / "integration" / "test_mainline_mcp_workflow.py",
    ROOT / "tests" / "e2e" / "test_analysis_writing_easyflash.py",
    ROOT / "tests" / "e2e" / "test_change_impact_easyflash.py",
    ROOT / "tests" / "e2e" / "test_export_easyflash.py",
    ROOT / "tests" / "e2e" / "test_repo_understand_easyflash.py",
    ROOT / "tests" / "e2e" / "test_self_use_launch_easyflash.py",
    ROOT / "tests" / "golden" / "test_contract_golden.py",
    ROOT / "tests" / "golden" / "fixtures" / "export_analysis_bundle_scope_first.json",
    ROOT / "tests" / "golden" / "fixtures" / "export_evidence_bundle_scope_first.json",
    ROOT / "tests" / "golden" / "fixtures" / "export_scope_snapshot_scope_first.json",
    ROOT / "tests" / "golden" / "fixtures" / "read_evidence_pack_scope_first.json",
    ROOT / "tests" / "golden" / "fixtures" / "render_module_summary_scope_first.json",
    ROOT / "tests" / "golden" / "fixtures" / "scan_repo.json",
    ROOT / "tests" / "golden" / "fixtures" / "summarize_impact_scope_first.json",
]


class PackageLayoutTest(unittest.TestCase):
    def test_root_package_imports(self) -> None:
        self.assertEqual(repo_analysis_tools.__version__, "0.1.0")

    def test_required_top_level_directories_exist(self) -> None:
        for path in EXPECTED_DIRECTORIES:
            self.assertTrue(path.is_dir(), str(path))

    def test_required_top_level_files_exist(self) -> None:
        for path in EXPECTED_FILES:
            self.assertTrue(path.is_file(), str(path))

    def test_legacy_interface_files_are_removed_from_active_tree(self) -> None:
        for path in UNEXPECTED_FILES:
            self.assertFalse(path.exists(), str(path))
