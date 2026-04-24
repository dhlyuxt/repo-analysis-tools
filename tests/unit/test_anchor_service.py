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


def build_ambiguous_call_target_repo(tmp_path: Path) -> Path:
    repo = tmp_path / "ambiguous-call-target-repo"
    (repo / "src").mkdir(parents=True, exist_ok=True)
    (repo / "demo").mkdir(parents=True, exist_ok=True)
    (repo / "src" / "main.c").write_text(
        "int flash_init(void);\n"
        "int main(void) { return flash_init(); }\n",
        encoding="utf-8",
    )
    (repo / "src" / "flash.c").write_text(
        "int flash_init(void) { return 0; }\n",
        encoding="utf-8",
    )
    (repo / "demo" / "flash.c").write_text(
        "int flash_init(void) { return 1; }\n",
        encoding="utf-8",
    )
    return repo


def build_static_helper_repo(tmp_path: Path) -> Path:
    repo = tmp_path / "static-helper-repo"
    (repo / "src").mkdir(parents=True, exist_ok=True)
    (repo / "src" / "a.c").write_text(
        "static int helper(void) { return 1; }\n"
        "int a(void) { return helper(); }\n",
        encoding="utf-8",
    )
    (repo / "src" / "b.c").write_text(
        "int b(void) { return helper(); }\n",
        encoding="utf-8",
    )
    return repo


def build_long_static_helper_repo(tmp_path: Path) -> Path:
    repo = tmp_path / "long-static-helper-repo"
    (repo / "src").mkdir(parents=True, exist_ok=True)
    (repo / "src" / "a.c").write_text(
        "static\n"
        "inline\n"
        "const\n"
        "volatile\n"
        "long\n"
        "int\n"
        "helper\n"
        "(\n"
        "    void\n"
        ")\n"
        "{\n"
        "    return 1;\n"
        "}\n"
        "int a(void) { return helper(); }\n",
        encoding="utf-8",
    )
    (repo / "src" / "b.c").write_text(
        "int b(void) { return helper(); }\n",
        encoding="utf-8",
    )
    return repo


def build_comment_static_global_helper_repo(tmp_path: Path) -> Path:
    repo = tmp_path / "comment-static-global-helper-repo"
    (repo / "src").mkdir(parents=True, exist_ok=True)
    (repo / "src" / "a.c").write_text(
        "/* static helper used to live here */\n"
        "int helper(void) { return 1; }\n",
        encoding="utf-8",
    )
    (repo / "src" / "b.c").write_text(
        "int b(void) { return helper(); }\n",
        encoding="utf-8",
    )
    return repo


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
        self.assertEqual(
            [
                (relation.kind, relation.source_name, relation.target_name, relation.line, relation.target_path)
                for relation in parsed.relations
                if relation.kind == "includes"
            ],
            [("includes", "main", "config.h", 1, "config.h")],
        )

    def test_regex_fallback_keeps_extracting_top_level_anchors_after_first_function(self) -> None:
        parser = CAnchorParser()
        source_text = (
            '#include "a.h"\n'
            "int one(void){ return 0; }\n"
            "int two(void){ return one(); }\n"
        )

        with patch("repo_analysis_tools.anchors.parser._try_build_tree_sitter_parser", return_value=None):
            parsed = parser.parse_file("src/demo.c", source_text)

        self.assertEqual(parsed.backend, "regex-compat")
        self.assertTrue({"one", "two"}.issubset({anchor.name for anchor in parsed.anchors}))
        self.assertEqual(
            [
                (relation.kind, relation.source_name, relation.target_name, relation.line, relation.target_path)
                for relation in parsed.relations
                if relation.kind == "includes"
            ],
            [("includes", "one", "a.h", 1, "a.h"), ("includes", "two", "a.h", 1, "a.h")],
        )

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
                    ("defines", "EF_USING_ENV", "src/config.h", 1, "src/config.h"),
                    ("direct_call", "main", "flash_init", 3, "src/flash.c"),
                    ("includes", "main", "config.h", 1, "src/config.h"),
                }.issubset(
                    {
                        (
                            relation.kind,
                            relation.source_name,
                            relation.target_name,
                            relation.line,
                            relation.target_path,
                        )
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

    def test_build_snapshot_relinks_cross_file_direct_calls_to_repo_wide_definition(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            repo = build_scope_first_repo(Path(tmpdir))
            scan_snapshot = ScanService().scan(repo)

            snapshot = AnchorService().build_snapshot(repo, scan_snapshot.scan_id)
            flash_definition = next(
                anchor
                for anchor in snapshot.anchors
                if anchor.name == "flash_init" and anchor.kind == "function_definition"
            )

            self.assertEqual(
                sorted(
                    (
                        relation.source_name,
                        relation.target_anchor_id,
                        relation.target_path,
                    )
                    for relation in snapshot.relations
                    if relation.kind == "direct_call" and relation.target_name == "flash_init"
                ),
                [
                    ("demo_main", flash_definition.anchor_id, "src/flash.c"),
                    ("main", flash_definition.anchor_id, "src/flash.c"),
                ],
            )

    def test_build_snapshot_keeps_ambiguous_repo_wide_direct_call_targets_unresolved(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            repo = build_ambiguous_call_target_repo(Path(tmpdir))
            scan_snapshot = ScanService().scan(repo)

            snapshot = AnchorService().build_snapshot(repo, scan_snapshot.scan_id)
            ambiguous_definition_ids = {
                anchor.anchor_id
                for anchor in snapshot.anchors
                if anchor.name == "flash_init" and anchor.kind == "function_definition"
            }

            matching_relations = [
                relation
                for relation in snapshot.relations
                if relation.kind == "direct_call" and relation.source_name == "main"
            ]

            self.assertEqual(len(matching_relations), 1)
            self.assertNotIn(matching_relations[0].target_anchor_id, ambiguous_definition_ids)

    def test_build_snapshot_does_not_resolve_cross_file_calls_to_static_definitions(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            repo = build_static_helper_repo(Path(tmpdir))
            scan_snapshot = ScanService().scan(repo)

            snapshot = AnchorService().build_snapshot(repo, scan_snapshot.scan_id)
            helper_definition = next(
                anchor
                for anchor in snapshot.anchors
                if anchor.name == "helper" and anchor.kind == "function_definition"
            )
            helper_relations = {
                relation.source_name: relation
                for relation in snapshot.relations
                if relation.kind == "direct_call" and relation.target_name == "helper"
            }

            self.assertEqual(helper_relations["a"].target_anchor_id, helper_definition.anchor_id)
            self.assertEqual(helper_relations["a"].target_path, "src/a.c")
            self.assertIsNone(helper_relations["b"].target_anchor_id)
            self.assertIsNone(helper_relations["b"].target_path)

    def test_build_snapshot_does_not_resolve_cross_file_calls_to_long_static_definitions(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            repo = build_long_static_helper_repo(Path(tmpdir))
            scan_snapshot = ScanService().scan(repo)

            snapshot = AnchorService().build_snapshot(repo, scan_snapshot.scan_id)
            helper_definition = next(
                anchor
                for anchor in snapshot.anchors
                if anchor.name == "helper" and anchor.kind == "function_definition"
            )
            helper_relations = {
                relation.source_name: relation
                for relation in snapshot.relations
                if relation.kind == "direct_call" and relation.target_name == "helper"
            }

            self.assertEqual(helper_relations["a"].target_anchor_id, helper_definition.anchor_id)
            self.assertEqual(helper_relations["a"].target_path, "src/a.c")
            self.assertIsNone(helper_relations["b"].target_anchor_id)
            self.assertIsNone(helper_relations["b"].target_path)

    def test_build_snapshot_ignores_static_in_comments_when_resolving_global_definitions(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            repo = build_comment_static_global_helper_repo(Path(tmpdir))
            scan_snapshot = ScanService().scan(repo)

            snapshot = AnchorService().build_snapshot(repo, scan_snapshot.scan_id)
            helper_definition = next(
                anchor
                for anchor in snapshot.anchors
                if anchor.name == "helper" and anchor.kind == "function_definition"
            )
            matching_relations = [
                relation
                for relation in snapshot.relations
                if relation.kind == "direct_call" and relation.source_name == "b"
            ]

            self.assertEqual(len(matching_relations), 1)
            self.assertEqual(matching_relations[0].target_anchor_id, helper_definition.anchor_id)
            self.assertEqual(matching_relations[0].target_path, "src/a.c")

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

    def test_service_rejects_empty_anchor_name_queries(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            repo = build_scope_first_repo(Path(tmpdir))
            scan_snapshot = ScanService().scan(repo)
            service = AnchorService()

            with self.assertRaisesRegex(ValueError, "anchor_name must not be empty"):
                service.find_anchor_matches(repo, "", scan_snapshot.scan_id)

            with self.assertRaisesRegex(ValueError, "anchor_name must not be empty"):
                service.describe_anchor(repo, "   ", scan_snapshot.scan_id)
