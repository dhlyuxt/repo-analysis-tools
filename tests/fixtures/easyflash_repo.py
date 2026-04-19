import shutil
from pathlib import Path

from tests.fixtures.git_helpers import init_git_fixture


FIXTURE_ROOT = Path(__file__).resolve().parent / "repos" / "easyflash"


def materialize_easyflash_repo(tmp_path: Path, *, initialize_git: bool = False) -> Path:
    repo = tmp_path / "easyflash"
    shutil.copytree(FIXTURE_ROOT, repo)
    if initialize_git:
        init_git_fixture(repo)
    return repo
