import os
import unittest
from contextlib import contextmanager
from pathlib import Path
from tempfile import TemporaryDirectory

from repo_analysis_tools.core.errors import ErrorCode, error_response
from repo_analysis_tools.core.ids import StableIdKind, make_stable_id
from repo_analysis_tools.core.paths import (
    domain_storage_root,
    normalize_repo_relative_path,
    runtime_root,
)
from repo_analysis_tools.storage.contracts import STORAGE_BOUNDARIES


class RuntimeContractsTest(unittest.TestCase):
    def setUp(self) -> None:
        self.repo_root = Path("/tmp/example-repo")

    @contextmanager
    def chdir(self, path: Path):
        previous_cwd = Path.cwd()
        os.chdir(path)
        try:
            yield
        finally:
            os.chdir(previous_cwd)

    def test_runtime_root_is_codewiki(self) -> None:
        self.assertEqual(runtime_root(self.repo_root), self.repo_root / ".codewiki")

    def test_runtime_root_matches_absolute_and_relative_repo_paths(self) -> None:
        with TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            repo_dir = temp_path / "example-repo"
            repo_dir.mkdir()
            with self.chdir(temp_path):
                self.assertEqual(runtime_root("example-repo"), runtime_root(repo_dir))

    def test_normalize_repo_relative_path_rejects_escape(self) -> None:
        with self.assertRaises(ValueError):
            normalize_repo_relative_path(self.repo_root, "../outside.c")

    def test_make_stable_id_uses_expected_prefix(self) -> None:
        self.assertTrue(make_stable_id(StableIdKind.SCAN).startswith("scan_"))
        self.assertTrue(make_stable_id(StableIdKind.SLICE).startswith("slice_"))

    def test_error_response_preserves_mcp_envelope_shape(self) -> None:
        payload = error_response(ErrorCode.INVALID_INPUT, "bad input")
        self.assertEqual(
            set(payload),
            {"schema_version", "status", "data", "messages", "recommended_next_tools"},
        )
        self.assertEqual(payload["status"], "error")
        self.assertEqual(payload["data"]["error"]["code"], "invalid_input")

    def test_storage_boundaries_live_under_runtime_root(self) -> None:
        self.assertEqual(
            domain_storage_root(self.repo_root, "scan"),
            self.repo_root / ".codewiki" / "scan",
        )
        self.assertEqual(STORAGE_BOUNDARIES["evidence"].directory_name, "evidence")

    def test_domain_storage_root_rejects_undeclared_domains(self) -> None:
        with self.assertRaisesRegex(ValueError, "undeclared storage domain"):
            domain_storage_root(self.repo_root, "unknown")
