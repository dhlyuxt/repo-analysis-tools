from __future__ import annotations

import json
from contextlib import contextmanager
import fcntl
import shutil
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from repo_analysis_tools.mcp.tools.query_tools import (
    find_call_paths,
    find_root_functions,
    get_file_info,
    list_file_symbols,
    list_priority_files,
    open_symbol_context,
    query_call_relations,
    resolve_symbols,
)
from repo_analysis_tools.mcp.tools.scan_tools import rebuild_repo_snapshot
from tests.fixtures.easyflash_repo import FIXTURE_ROOT


DEMO_REPO_ROOT = Path(tempfile.gettempdir()) / "repo-analysis-tools-self-use-demo" / "easyflash"
DEMO_LOCK_PATH = Path(tempfile.gettempdir()) / "repo-analysis-tools-self-use-demo.lock"


@contextmanager
def _demo_lock() -> None:
    DEMO_LOCK_PATH.parent.mkdir(parents=True, exist_ok=True)
    with DEMO_LOCK_PATH.open("w", encoding="utf-8") as lock_file:
        fcntl.flock(lock_file, fcntl.LOCK_EX)
        try:
            yield
        finally:
            fcntl.flock(lock_file, fcntl.LOCK_UN)


def _require_ok(tool_name: str, payload: dict[str, object]) -> dict[str, object]:
    status = payload.get("status")
    if status == "ok":
        data = payload.get("data")
        if not isinstance(data, dict):
            raise RuntimeError(f"{tool_name} returned an ok payload without a data object: {payload!r}")
        return data

    error = payload.get("data", {})
    if isinstance(error, dict):
        error_data = error.get("error", {})
        if isinstance(error_data, dict):
            code = error_data.get("code", "unknown")
            message = error_data.get("message", "unknown error")
            raise RuntimeError(f"{tool_name} failed with {code}: {message}")

    raise RuntimeError(f"{tool_name} returned an unexpected payload: {payload!r}")


def _materialize_demo_repo() -> Path:
    if DEMO_REPO_ROOT.exists():
        shutil.rmtree(DEMO_REPO_ROOT)
    DEMO_REPO_ROOT.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(FIXTURE_ROOT, DEMO_REPO_ROOT)
    return DEMO_REPO_ROOT


def run_demo() -> dict[str, object]:
    with _demo_lock():
        repo = _materialize_demo_repo()
        rebuild_data = _require_ok("rebuild_repo_snapshot", rebuild_repo_snapshot(str(repo)))
        scan_id = str(rebuild_data["scan_id"])
        priority_data = _require_ok("list_priority_files", list_priority_files(scan_id))
        file_info_data = _require_ok("get_file_info", get_file_info(scan_id, "easyflash/src/easyflash.c"))
        file_symbols_data = _require_ok(
            "list_file_symbols",
            list_file_symbols(scan_id, ["easyflash/src/easyflash.c", "easyflash/port/ef_port.c"]),
        )
        symbol_data = _require_ok("resolve_symbols", resolve_symbols(scan_id, "easyflash_init"))
        matches = symbol_data.get("matches", [])
        if not matches:
            raise RuntimeError("resolve_symbols returned no matches for easyflash_init")
        symbol_row = matches[0]
        context_data = _require_ok("open_symbol_context", open_symbol_context(scan_id, symbol_row["symbol_id"], 2))
        relations_data = _require_ok("query_call_relations", query_call_relations(scan_id, symbol_row["symbol_id"]))
        roots_data = _require_ok(
            "find_root_functions",
            find_root_functions(scan_id, ["easyflash/src/easyflash.c", "easyflash/port/ef_port.c"]),
        )
        call_path_status = "no_path"
        call_path_count = 0
        roots = roots_data.get("roots", [])
        if roots:
            path_data = _require_ok(
                "find_call_paths",
                find_call_paths(scan_id, roots[0]["symbol_id"], symbol_row["symbol_id"]),
            )
            call_path_status = str(path_data["status"])
            call_path_count = int(path_data["returned_path_count"])

        file_symbols_summary = {
            row["path"]: {
                "symbol_count": len(row["symbols"]),
                "symbol_names": [symbol["name"] for symbol in row["symbols"][:5]],
            }
            for row in file_symbols_data["files"]
        }

        return {
            "repo_root": str(repo),
            "scan_id": scan_id,
            "symbol_name": symbol_row["name"],
            "symbol_path": symbol_row["path"],
            "priority_files": priority_data["files"][:5],
            "file_info": file_info_data,
            "file_symbols": file_symbols_summary,
            "context_line_start": context_data["context_line_start"],
            "context_line_end": context_data["context_line_end"],
            "caller_count": len(relations_data["callers"]),
            "callee_count": len(relations_data["callees"]),
            "root_names": [row["name"] for row in roots],
            "call_path_status": call_path_status,
            "call_path_count": call_path_count,
        }


def main() -> int:
    print(json.dumps(run_demo(), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
