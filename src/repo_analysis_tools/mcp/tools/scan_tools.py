from pathlib import Path

from repo_analysis_tools.core.errors import ok_response
from repo_analysis_tools.core.paths import runtime_root
from repo_analysis_tools.mcp.app import mcp
from repo_analysis_tools.scan.service import ScanService
from repo_analysis_tools.scan.store import ScanStore


@mcp.tool()
def scan_repo(target_repo: str) -> dict[str, object]:
    snapshot = ScanService().scan(target_repo)
    return ok_response(
        data={
            "target_repo": target_repo,
            "runtime_root": runtime_root(Path(target_repo)).as_posix(),
            "scan_id": snapshot.scan_id,
            "repo_root": snapshot.repo_root,
            "file_count": snapshot.file_count,
            "latest_completed_at": snapshot.completed_at,
            "git_head": snapshot.git_head,
            "workspace_dirty": snapshot.workspace_dirty,
        },
        messages=["scan completed"],
        recommended_next_tools=["get_scan_status", "show_scope"],
    )


@mcp.tool()
def refresh_scan(target_repo: str, scan_id: str) -> dict[str, object]:
    snapshot = ScanService().scan(target_repo)
    return ok_response(
        data={
            "target_repo": target_repo,
            "runtime_root": runtime_root(Path(target_repo)).as_posix(),
            "scan_id": snapshot.scan_id,
            "repo_root": snapshot.repo_root,
            "file_count": snapshot.file_count,
            "latest_completed_at": snapshot.completed_at,
            "git_head": snapshot.git_head,
            "workspace_dirty": snapshot.workspace_dirty,
        },
        messages=[f"scan {scan_id} refreshed"],
        recommended_next_tools=["get_scan_status", "show_scope"],
    )


@mcp.tool()
def get_scan_status(target_repo: str, scan_id: str | None = None) -> dict[str, object]:
    snapshot = ScanStore.for_repo(target_repo).load(scan_id=scan_id)
    return ok_response(
        data={
            "target_repo": target_repo,
            "runtime_root": runtime_root(Path(target_repo)).as_posix(),
            "scan_id": snapshot.scan_id,
            "repo_root": snapshot.repo_root,
            "file_count": snapshot.file_count,
            "latest_completed_at": snapshot.completed_at,
            "git_head": snapshot.git_head,
            "workspace_dirty": snapshot.workspace_dirty,
        },
        messages=["latest scan loaded"],
        recommended_next_tools=["show_scope", "list_anchors"],
    )
