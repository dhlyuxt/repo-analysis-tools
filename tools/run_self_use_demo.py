from __future__ import annotations

import json
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


def _materialize_demo_repo() -> Path:
    if DEMO_REPO_ROOT.exists():
        shutil.rmtree(DEMO_REPO_ROOT)
    DEMO_REPO_ROOT.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(FIXTURE_ROOT, DEMO_REPO_ROOT)
    return DEMO_REPO_ROOT


def run_demo() -> dict[str, object]:
    repo = _materialize_demo_repo()
    rebuild_payload = rebuild_repo_snapshot(str(repo))
    scan_id = rebuild_payload["data"]["scan_id"]
    priority_payload = list_priority_files(scan_id)
    file_info_payload = get_file_info(scan_id, "easyflash/src/easyflash.c")
    file_symbols_payload = list_file_symbols(scan_id, ["easyflash/src/easyflash.c", "easyflash/port/ef_port.c"])
    symbol_payload = resolve_symbols(scan_id, "easyflash_init")
    symbol_row = symbol_payload["data"]["matches"][0]
    context_payload = open_symbol_context(scan_id, symbol_row["symbol_id"], 2)
    relations_payload = query_call_relations(scan_id, symbol_row["symbol_id"])
    roots_payload = find_root_functions(scan_id, ["easyflash/src/easyflash.c", "easyflash/port/ef_port.c"])
    call_path_status = "no_path"
    call_path_count = 0
    if roots_payload["data"]["roots"]:
        path_payload = find_call_paths(
            scan_id,
            roots_payload["data"]["roots"][0]["symbol_id"],
            symbol_row["symbol_id"],
        )
        call_path_status = path_payload["data"]["status"]
        call_path_count = path_payload["data"]["returned_path_count"]

    file_symbols_summary = {
        row["path"]: {
            "symbol_count": len(row["symbols"]),
            "symbol_names": [symbol["name"] for symbol in row["symbols"][:5]],
        }
        for row in file_symbols_payload["data"]["files"]
    }

    return {
        "repo_root": str(repo),
        "scan_id": scan_id,
        "symbol_name": symbol_row["name"],
        "symbol_path": symbol_row["path"],
        "priority_files": priority_payload["data"]["files"][:5],
        "file_info": file_info_payload["data"],
        "file_symbols": file_symbols_summary,
        "context_line_start": context_payload["data"]["context_line_start"],
        "context_line_end": context_payload["data"]["context_line_end"],
        "caller_count": len(relations_payload["data"]["callers"]),
        "callee_count": len(relations_payload["data"]["callees"]),
        "root_names": [row["name"] for row in roots_payload["data"]["roots"]],
        "call_path_status": call_path_status,
        "call_path_count": call_path_count,
    }


def main() -> int:
    print(json.dumps(run_demo(), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
