from repo_analysis_tools.mcp.app import mcp
from repo_analysis_tools.mcp.tools.shared import stub_payload


@mcp.tool()
def show_scope(target_repo: str, scan_id: str | None = None) -> dict[str, object]:
    return stub_payload(
        "show_scope",
        target_repo=target_repo,
        scan_id=scan_id or "scan_stub_scope",
        scope_summary="M1 scope contract stub",
    )


@mcp.tool()
def list_scope_nodes(target_repo: str, scan_id: str | None = None) -> dict[str, object]:
    return stub_payload(
        "list_scope_nodes",
        target_repo=target_repo,
        scan_id=scan_id or "scan_stub_scope",
        nodes=[{"node_id": "src", "kind": "directory"}],
    )


@mcp.tool()
def explain_scope_node(target_repo: str, node_id: str, scan_id: str | None = None) -> dict[str, object]:
    return stub_payload(
        "explain_scope_node",
        target_repo=target_repo,
        scan_id=scan_id or "scan_stub_scope",
        node_id=node_id,
        summary="M1 scope node explanation stub",
    )
