#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def _ensure_src_on_path() -> None:
    project_root = Path(__file__).resolve().parents[1]
    src_path = str(project_root / "src")
    if src_path not in sys.path:
        sys.path.insert(0, src_path)


def main(argv: list[str] | None = None) -> int:
    _ensure_src_on_path()
    from repo_analysis_tools.report.repo_design_models import RepositoryFindingsPackage
    from repo_analysis_tools.report.repo_design_service import RepositoryDesignWriter

    parser = argparse.ArgumentParser(description="Write repository design documents.")
    parser.add_argument("--input", required=True, help="Path to a findings package JSON file.")
    args = parser.parse_args(argv)

    payload = json.loads(Path(args.input).read_text(encoding="utf-8"))
    package = RepositoryFindingsPackage.from_dict(payload)
    manifest = RepositoryDesignWriter().write_document_set(package)
    print(json.dumps(manifest.to_dict(), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
