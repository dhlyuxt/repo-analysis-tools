import tempfile
import unittest
from pathlib import Path

from repo_analysis_tools.impact.service import ImpactService
from repo_analysis_tools.impact.store import ImpactStore
from repo_analysis_tools.scan.service import ScanService


def build_proven_call_repo(tmp_path: Path) -> Path:
    repo = tmp_path / "proven-call-repo"
    (repo / "src").mkdir(parents=True, exist_ok=True)
    (repo / "src" / "impact.c").write_text(
        "int flash_init(void) { return 0; }\n"
        "int main(void) { return flash_init(); }\n"
        "int demo_main(void) { return flash_init(); }\n",
        encoding="utf-8",
    )
    return repo


def build_ambiguous_anchor_repo(tmp_path: Path) -> Path:
    repo = tmp_path / "ambiguous-anchor-repo"
    (repo / "src").mkdir(parents=True, exist_ok=True)
    (repo / "demo").mkdir(parents=True, exist_ok=True)
    (repo / "src" / "flash.c").write_text(
        "int flash_init(void) { return 0; }\n",
        encoding="utf-8",
    )
    (repo / "demo" / "flash.c").write_text(
        "int flash_init(void) { return 1; }\n",
        encoding="utf-8",
    )
    return repo


class ImpactServiceTest(unittest.TestCase):
    def test_from_paths_persists_changed_path_and_reverse_callers(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            repo = build_proven_call_repo(Path(tmpdir))
            scan_snapshot = ScanService().scan(repo)

            result = ImpactService().from_paths(repo, ["src/impact.c"], scan_snapshot.scan_id)
            stored = ImpactStore.for_repo(repo).load(result.impact_id)
            latest = ImpactStore.for_repo(repo).load_latest()

            self.assertRegex(result.impact_id, r"^impact_[0-9a-f]{12}$")
            self.assertEqual(latest.impact_id, result.impact_id)
            self.assertEqual(stored.scan_id, scan_snapshot.scan_id)
            self.assertEqual(stored.seed_kind, "path")
            self.assertEqual([target.path for target in stored.confirmed_targets], ["src/impact.c"])
            self.assertEqual(
                [(target.anchor_name, target.path) for target in stored.likely_propagation],
                [("demo_main", "src/impact.c"), ("main", "src/impact.c")],
            )
            self.assertTrue(
                any("bounded by available anchor relations" in note for note in stored.blind_spots)
            )

    def test_from_anchor_uses_anchor_seed_and_caller_propagation(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            repo = build_proven_call_repo(Path(tmpdir))
            scan_snapshot = ScanService().scan(repo)

            result = ImpactService().from_anchor(repo, "flash_init", scan_snapshot.scan_id)
            stored = ImpactStore.for_repo(repo).load(result.impact_id)

            self.assertEqual(result.seed.anchor_name, "flash_init")
            self.assertEqual(stored.seed_kind, "anchor")
            self.assertEqual(
                [(target.anchor_name, target.path) for target in stored.confirmed_targets],
                [("flash_init", "src/impact.c")],
            )
            self.assertEqual(
                [(target.anchor_name, target.path) for target in stored.likely_propagation],
                [("demo_main", "src/impact.c"), ("main", "src/impact.c")],
            )

    def test_summarize_returns_structured_impact_sections(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            repo = build_proven_call_repo(Path(tmpdir))
            scan_snapshot = ScanService().scan(repo)
            created = ImpactService().from_paths(repo, ["src/impact.c"], scan_snapshot.scan_id)

            summary = ImpactService().summarize(repo, created.impact_id)

            self.assertEqual(summary.impact_id, created.impact_id)
            self.assertEqual(
                [(target.anchor_name, target.path) for target in summary.confirmed_impact],
                [(None, "src/impact.c")],
            )
            self.assertEqual(
                [(target.anchor_name, target.path) for target in summary.likely_propagation],
                [("demo_main", "src/impact.c"), ("main", "src/impact.c")],
            )
            self.assertTrue(any("src/impact.c" in item for item in summary.regression_focus))
            self.assertTrue(any("anchor relations" in item for item in summary.blind_spots))
            self.assertEqual([risk.title for risk in summary.risks], ["Reverse callers may regress"])

    def test_from_anchor_rejects_ambiguous_function_definition_seed(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            repo = build_ambiguous_anchor_repo(Path(tmpdir))
            scan_snapshot = ScanService().scan(repo)

            with self.assertRaisesRegex(
                ValueError,
                "anchor flash_init is ambiguous; disambiguate the requested anchor first",
            ):
                ImpactService().from_anchor(repo, "flash_init", scan_snapshot.scan_id)
