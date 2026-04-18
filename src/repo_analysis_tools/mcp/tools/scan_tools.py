from repo_analysis_tools.mcp.app import mcp
from repo_analysis_tools.mcp.tools.shared import stub_payload


@mcp.tool()
def scan_repo(target_repo: str) -> dict[str, object]:
    return stub_payload("scan_repo", target_repo=target_repo)


@mcp.tool()
def refresh_scan(target_repo: str, scan_id: str) -> dict[str, object]:
    return stub_payload("refresh_scan", target_repo=target_repo, scan_id=scan_id, refreshed=True)


@mcp.tool()
def get_scan_status(target_repo: str, scan_id: str | None = None) -> dict[str, object]:
    return stub_payload(
        "get_scan_status",
        target_repo=target_repo,
        scan_id=scan_id or "scan_stub_status",
        status_detail="stub",
    )
