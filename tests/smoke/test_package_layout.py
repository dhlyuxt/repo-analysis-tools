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


class PackageLayoutTest(unittest.TestCase):
    def test_root_package_imports(self) -> None:
        self.assertEqual(repo_analysis_tools.__version__, "0.1.0")

    def test_required_top_level_directories_exist(self) -> None:
        for path in EXPECTED_DIRECTORIES:
            self.assertTrue(path.is_dir(), str(path))
