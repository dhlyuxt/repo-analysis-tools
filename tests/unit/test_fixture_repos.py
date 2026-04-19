import tempfile
import unittest
from pathlib import Path

from tests.fixtures.scope_first_repo import build_scope_first_repo


ROOT = Path(__file__).resolve().parents[2]


class FixtureReposTest(unittest.TestCase):
    def test_scope_first_repo_builder_creates_expected_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            repo = build_scope_first_repo(Path(tmpdir))
            expected = {
                "src/main.c",
                "src/flash.c",
                "src/config.h",
                "ports/board_port.c",
                "demo/demo_main.c",
                "generated/autoconf.h",
            }
            actual = {
                path.relative_to(repo).as_posix()
                for path in repo.rglob("*")
                if path.is_file()
            }
            self.assertEqual(actual, expected)

    def test_easyflash_fixture_contains_real_entrypoints(self) -> None:
        fixture_root = ROOT / "tests" / "fixtures" / "repos" / "easyflash"
        self.assertTrue((fixture_root / "easyflash" / "src" / "easyflash.c").is_file())
        self.assertTrue((fixture_root / "easyflash" / "inc" / "easyflash.h").is_file())
        self.assertTrue((fixture_root / "easyflash" / "port" / "ef_port.c").is_file())
