from __future__ import annotations

import json
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
    list_priority_files,
    query_call_relations,
    resolve_symbols,
)
from repo_analysis_tools.mcp.tools.scan_tools import rebuild_repo_snapshot
from tests.fixtures.easyflash_repo import materialize_easyflash_repo


def run_demo() -> dict[str, object]:
    repo = materialize_easyflash_repo(Path(tempfile.mkdtemp(prefix="self-use-demo-")))
    rebuild_payload = rebuild_repo_snapshot(str(repo))
    scan_id = rebuild_payload["data"]["scan_id"]
    priority_payload = list_priority_files(scan_id)
    symbol_payload = resolve_symbols(scan_id, "easyflash_init")
    symbol_row = symbol_payload["data"]["matches"][0]
    relations_payload = query_call_relations(scan_id, symbol_row["symbol_id"])
    roots_payload = find_root_functions(scan_id, ["easyflash/src/easyflash.c", "easyflash/port/ef_port.c"])
    call_path_status = "no_path"
    if roots_payload["data"]["roots"]:
        path_payload = find_call_paths(
            scan_id,
            roots_payload["data"]["roots"][0]["symbol_id"],
            symbol_row["symbol_id"],
        )
        call_path_status = path_payload["data"]["status"]

    return {
        "scan_id": scan_id,
        "symbol_name": symbol_row["name"],
        "priority_files": priority_payload["data"]["files"][:5],
        "caller_count": len(relations_payload["data"]["callers"]),
        "call_path_status": call_path_status,
    }


def main() -> int:
    print(json.dumps(run_demo(), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
