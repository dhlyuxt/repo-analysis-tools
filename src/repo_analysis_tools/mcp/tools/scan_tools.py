from pathlib import Path

from repo_analysis_tools.core.errors import ErrorCode, error_response, ok_response
from repo_analysis_tools.core.paths import runtime_root
from repo_analysis_tools.mcp.app import mcp
from repo_analysis_tools.scan.service import ScanService
from repo_analysis_tools.scan.store import ScanStore


def _scan_snapshot_payload(target_repo: str, snapshot: object) -> dict[str, object]:
    return {
        "target_repo": target_repo,
        "runtime_root": runtime_root(Path(target_repo)).as_posix(),
        "scan_id": snapshot.scan_id,
        "repo_root": snapshot.repo_root,
        "file_count": snapshot.file_count,
        "latest_completed_at": snapshot.completed_at,
        "git_head": snapshot.git_head,
        "workspace_dirty": snapshot.workspace_dirty,
    }


@mcp.tool()
def scan_repo(target_repo: str) -> dict[str, object]:
    snapshot = ScanService().scan(target_repo)
    return ok_response(
        data=_scan_snapshot_payload(target_repo, snapshot),
        messages=["scan completed"],
        recommended_next_tools=["get_scan_status", "show_scope"],
    )


@mcp.tool()
def refresh_scan(target_repo: str, scan_id: str) -> dict[str, object]:
    store = ScanStore.for_repo(target_repo)
    try:
        scan_exists = store.exists(scan_id)
    except ValueError as exc:
        return error_response(ErrorCode.INVALID_INPUT, str(exc))
    if not scan_exists:
        return error_response(
            ErrorCode.NOT_FOUND,
            f"scan {scan_id} was not found",
        )
    snapshot = ScanService().scan(target_repo)
    return ok_response(
        data=_scan_snapshot_payload(target_repo, snapshot),
        messages=[f"scan {scan_id} refreshed"],
        recommended_next_tools=["get_scan_status", "show_scope"],
    )


@mcp.tool()
def get_scan_status(target_repo: str, scan_id: str | None = None) -> dict[str, object]:
    try:
        snapshot = ScanStore.for_repo(target_repo).load(scan_id=scan_id)
    except ValueError as exc:
        return error_response(ErrorCode.INVALID_INPUT, str(exc))
    except FileNotFoundError:
        message = (
            f"scan {scan_id} was not found"
            if scan_id is not None
            else f"no scans were found for {target_repo}"
        )
        return error_response(ErrorCode.NOT_FOUND, message)
    return ok_response(
        data=_scan_snapshot_payload(target_repo, snapshot),
        messages=["latest scan loaded"],
        recommended_next_tools=["show_scope", "list_anchors"],
    )
