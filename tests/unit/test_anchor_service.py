import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from repo_analysis_tools.anchors.parser import CAnchorParser
from repo_analysis_tools.anchors.service import AnchorService
from repo_analysis_tools.anchors.store import AnchorStore
from repo_analysis_tools.scan.service import ScanService
from tests.fixtures.easyflash_repo import materialize_easyflash_repo
from tests.fixtures.scope_first_repo import build_scope_first_repo


class AnchorServiceTest(unittest.TestCase):
    def test_parser_uses_tree_sitter_primary_path_when_runtime_is_compatible(self) -> None:
        parser = CAnchorParser()
        source_text = (
            '#include "config.h"\n'
            "int flash_init(void);\n"
            "int main(void) { return flash_init(); }\n"
        )

        with patch(
            "repo_analysis_tools.anchors.parser._extract_with_regex",
            side_effect=AssertionError("regex fallback should not be used"),
        ):
            parsed = parser.parse_file("src/main.c", source_text)

        self.assertEqual(parsed.backend, "tree-sitter-c")
        self.assertTrue({"flash_init", "main"}.issubset({anchor.name for anchor in parsed.anchors}))

    def test_build_snapshot_extracts_expected_anchors_and_relations_from_synthetic_repo(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            repo = build_scope_first_repo(Path(tmpdir))
            scan_snapshot = ScanService().scan(repo)

            snapshot = AnchorService().build_snapshot(repo, scan_snapshot.scan_id)
            stored = AnchorStore.for_repo(repo).load(scan_snapshot.scan_id)

            self.assertEqual(stored.scan_id, snapshot.scan_id)
            self.assertEqual(snapshot.extraction_backend, "tree-sitter-c")
            self.assertTrue(
                {"EF_USING_ENV", "flash_init", "main"}.issubset(
                    {anchor.name for anchor in snapshot.anchors}
                )
            )
            self.assertTrue(
                {
                    ("defines", "EF_USING_ENV", "src/config.h"),
                    ("direct_call", "main", "flash_init"),
                    ("includes", "main", "config.h"),
                }.issubset(
                    {
                        (relation.kind, relation.source_name, relation.target_name)
                        for relation in snapshot.relations
                    }
                )
            )

    def test_scan_service_persists_anchor_snapshot(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            repo = build_scope_first_repo(Path(tmpdir))

            scan_snapshot = ScanService().scan(repo)
            anchor_snapshot = AnchorStore.for_repo(repo).load(scan_snapshot.scan_id)

            self.assertEqual(anchor_snapshot.scan_id, scan_snapshot.scan_id)
            self.assertIn("main", {anchor.name for anchor in anchor_snapshot.anchors})

    def test_describe_anchor_for_easyflash_includes_direct_call_relation(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            repo = materialize_easyflash_repo(Path(tmpdir))
            scan_snapshot = ScanService().scan(repo)

            description = AnchorService().describe_anchor(repo, "easyflash_init", scan_snapshot.scan_id)

            self.assertEqual(description.anchor.name, "easyflash_init")
            self.assertIn("easyflash/src/easyflash.c", description.description)
            self.assertIn(
                "ef_port_init",
                {
                    relation.target_name
                    for relation in description.relations
                    if relation.kind == "direct_call"
                },
            )
