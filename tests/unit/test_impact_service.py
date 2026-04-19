import tempfile
import unittest
from pathlib import Path

from repo_analysis_tools.impact.service import ImpactService
from repo_analysis_tools.impact.store import ImpactStore
from repo_analysis_tools.scan.service import ScanService
from tests.fixtures.scope_first_repo import build_scope_first_repo


class ImpactServiceTest(unittest.TestCase):
    def test_from_paths_persists_changed_path_and_reverse_callers(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            repo = build_scope_first_repo(Path(tmpdir))
            scan_snapshot = ScanService().scan(repo)

            result = ImpactService().from_paths(repo, ["src/flash.c"], scan_snapshot.scan_id)
            stored = ImpactStore.for_repo(repo).load(result.impact_id)
            latest = ImpactStore.for_repo(repo).load_latest()

            self.assertRegex(result.impact_id, r"^impact_[0-9a-f]{12}$")
            self.assertEqual(latest.impact_id, result.impact_id)
            self.assertEqual(stored.scan_id, scan_snapshot.scan_id)
            self.assertEqual(stored.seed_kind, "path")
            self.assertEqual([target.path for target in stored.confirmed_targets], ["src/flash.c"])
            self.assertEqual(
                [(target.anchor_name, target.path) for target in stored.likely_propagation],
                [("demo_main", "demo/demo_main.c"), ("main", "src/main.c")],
            )
            self.assertTrue(
                any("bounded by available anchor relations" in note for note in stored.blind_spots)
            )

    def test_from_anchor_uses_anchor_seed_and_caller_propagation(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            repo = build_scope_first_repo(Path(tmpdir))
            scan_snapshot = ScanService().scan(repo)

            result = ImpactService().from_anchor(repo, "flash_init", scan_snapshot.scan_id)
            stored = ImpactStore.for_repo(repo).load(result.impact_id)

            self.assertEqual(result.seed.anchor_name, "flash_init")
            self.assertEqual(stored.seed_kind, "anchor")
            self.assertEqual(
                [(target.anchor_name, target.path) for target in stored.confirmed_targets],
                [("flash_init", "src/flash.c")],
            )
            self.assertEqual(
                [(target.anchor_name, target.path) for target in stored.likely_propagation],
                [("demo_main", "demo/demo_main.c"), ("main", "src/main.c")],
            )

    def test_summarize_returns_structured_impact_sections(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            repo = build_scope_first_repo(Path(tmpdir))
            scan_snapshot = ScanService().scan(repo)
            created = ImpactService().from_paths(repo, ["src/flash.c"], scan_snapshot.scan_id)

            summary = ImpactService().summarize(repo, created.impact_id)

            self.assertEqual(summary.impact_id, created.impact_id)
            self.assertEqual(
                [(target.anchor_name, target.path) for target in summary.confirmed_impact],
                [(None, "src/flash.c")],
            )
            self.assertEqual(
                [(target.anchor_name, target.path) for target in summary.likely_propagation],
                [("demo_main", "demo/demo_main.c"), ("main", "src/main.c")],
            )
            self.assertTrue(any("demo/demo_main.c" in item for item in summary.regression_focus))
            self.assertTrue(any("anchor relations" in item for item in summary.blind_spots))
            self.assertEqual([risk.title for risk in summary.risks], ["Reverse callers may regress"])
