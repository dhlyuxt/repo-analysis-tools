import tempfile
import unittest
import subprocess
from pathlib import Path

from tests.fixtures.easyflash_repo import materialize_easyflash_repo
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
        self.assertTrue((fixture_root / "easyflash" / "src" / "ef_env.c").is_file())
        self.assertTrue((fixture_root / "easyflash" / "src" / "ef_log.c").is_file())
        self.assertTrue((fixture_root / "easyflash" / "src" / "ef_iap.c").is_file())
        self.assertTrue((fixture_root / "easyflash" / "inc" / "ef_def.h").is_file())
        self.assertTrue((fixture_root / "easyflash" / "plugins" / "types" / "ef_types.c").is_file())
        self.assertTrue((fixture_root / "demo" / "iap" / "ymodem+rtt.c").is_file())
        self.assertTrue((fixture_root / "demo" / "log" / "easylogger.c").is_file())
        self.assertTrue((fixture_root / "docs" / "readme.md").is_file())

    def test_materialize_easyflash_repo_copies_fixture_and_can_initialize_git(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            repo = materialize_easyflash_repo(Path(tmpdir))
            self.assertTrue((repo / "easyflash" / "src" / "easyflash.c").is_file())
            self.assertTrue((repo / "easyflash" / "src" / "ef_env.c").is_file())
            self.assertTrue((repo / "easyflash" / "src" / "ef_log.c").is_file())
            self.assertTrue((repo / "easyflash" / "inc" / "ef_def.h").is_file())
            self.assertTrue((repo / "easyflash" / "plugins" / "types" / "ef_types.c").is_file())
            self.assertTrue((repo / "demo" / "iap" / "README.md").is_file())
            self.assertTrue((repo / "FIXTURE_INFO.md").is_file())
            self.assertFalse((repo / ".git").exists())

        with tempfile.TemporaryDirectory() as tmpdir:
            repo = materialize_easyflash_repo(Path(tmpdir), initialize_git=True)
            self.assertTrue((repo / ".git").is_dir())
            head = subprocess.run(
                ["git", "rev-parse", "HEAD"],
                cwd=repo,
                capture_output=True,
                text=True,
                check=True,
            ).stdout.strip()
            self.assertRegex(head, r"^[0-9a-f]{40}$")
