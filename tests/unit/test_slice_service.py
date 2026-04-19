import tempfile
import unittest
from pathlib import Path

from repo_analysis_tools.scan.service import ScanService
from repo_analysis_tools.slice.query_classifier import QueryClassifier
from repo_analysis_tools.slice.service import SliceService
from repo_analysis_tools.slice.store import SliceStore
from tests.fixtures.scope_first_repo import build_scope_first_repo


class SliceServiceTest(unittest.TestCase):
    def test_classifier_accepts_common_quoted_symbol_forms(self) -> None:
        classifier = QueryClassifier()

        for question in (
            "Where is 'flash_init' defined?",
            'Where is "flash_init" defined?',
            "Where is `flash_init` defined?",
        ):
            with self.subTest(question=question):
                classification = classifier.classify(question)
                self.assertEqual(classification.query_kind, "locate_symbol")
                self.assertEqual(classification.symbol_name, "flash_init")

    def test_classifier_prioritizes_file_role_over_startup_substrings(self) -> None:
        classification = QueryClassifier().classify("What is the role of startup.c?")

        self.assertEqual(classification.query_kind, "file_role")
        self.assertEqual(classification.subject, "startup.c")

    def test_plan_locate_symbol_selects_definition_and_persists_manifest(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            repo = build_scope_first_repo(Path(tmpdir))
            scan_snapshot = ScanService().scan(repo)

            manifest = SliceService().plan(repo, "Where is flash_init defined?", scan_snapshot.scan_id)
            stored = SliceStore.for_repo(repo).load(manifest.slice_id)

            self.assertEqual(manifest.query_kind, "locate_symbol")
            self.assertEqual(manifest.status, "complete")
            self.assertEqual(manifest.selected_files, ["src/flash.c"])
            self.assertEqual(manifest.selected_anchor_names, ["flash_init"])
            self.assertEqual(manifest.notes, ["Located definition candidates for flash_init."])
            self.assertEqual(stored.slice_id, manifest.slice_id)
            self.assertEqual(stored.scan_id, scan_snapshot.scan_id)
            self.assertEqual(stored.selected_files, ["src/flash.c"])
            self.assertEqual(stored.notes, ["Located definition candidates for flash_init."])

    def test_plan_init_flow_selects_startup_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            repo = build_scope_first_repo(Path(tmpdir))
            scan_snapshot = ScanService().scan(repo)

            manifest = SliceService().plan(repo, "Explain startup flow", scan_snapshot.scan_id)

            self.assertEqual(manifest.query_kind, "init_flow")
            self.assertEqual(manifest.status, "complete")
            self.assertEqual(manifest.selected_files, ["src/flash.c", "src/main.c"])
            self.assertEqual(
                manifest.notes,
                ["Selected entrypoint and init routines for startup flow inspection."],
            )

    def test_plan_symbol_no_match_surfaces_close_match_notes(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            repo = build_scope_first_repo(Path(tmpdir))
            scan_snapshot = ScanService().scan(repo)

            manifest = SliceService().plan(repo, "Where is flash_int defined?", scan_snapshot.scan_id)

            self.assertEqual(manifest.query_kind, "locate_symbol")
            self.assertEqual(manifest.status, "no_match")
            self.assertEqual(manifest.selected_files, [])
            self.assertEqual(manifest.selected_anchor_names, [])
            self.assertEqual(len(manifest.notes), 1)
            self.assertIn("flash_init", manifest.notes[0])

    def test_inspect_and_expand_load_members_from_persisted_manifest(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            repo = build_scope_first_repo(Path(tmpdir))
            scan_snapshot = ScanService().scan(repo)
            service = SliceService()

            manifest = service.plan(repo, "Where is flash_init defined?", scan_snapshot.scan_id)
            inspected = service.inspect(repo, manifest.slice_id)
            expanded = service.expand(repo, manifest.slice_id)

            self.assertEqual(inspected.target_repo, str(Path(repo).resolve()))
            self.assertEqual(inspected.members, ["src/flash.c"])
            self.assertEqual(expanded.slice_id, manifest.slice_id)
            self.assertFalse(expanded.expanded)

    def test_plan_locate_symbol_supports_quoted_symbol_questions(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            repo = build_scope_first_repo(Path(tmpdir))
            scan_snapshot = ScanService().scan(repo)

            manifest = SliceService().plan(repo, "Where is `flash_init` defined?", scan_snapshot.scan_id)

            self.assertEqual(manifest.query_kind, "locate_symbol")
            self.assertEqual(manifest.selected_files, ["src/flash.c"])
