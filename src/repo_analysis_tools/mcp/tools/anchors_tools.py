from repo_analysis_tools.mcp.app import mcp
from repo_analysis_tools.mcp.tools.shared import stub_payload


@mcp.tool()
def list_anchors(target_repo: str, scan_id: str | None = None) -> dict[str, object]:
    extra = {"scan_id": scan_id} if scan_id is not None else {}
    return stub_payload(
        "list_anchors",
        target_repo=target_repo,
        anchors=[{"name": "main", "kind": "function"}],
        **extra,
    )


@mcp.tool()
def find_anchor(target_repo: str, anchor_name: str, scan_id: str | None = None) -> dict[str, object]:
    extra = {"scan_id": scan_id} if scan_id is not None else {}
    return stub_payload(
        "find_anchor",
        target_repo=target_repo,
        anchor_name=anchor_name,
        matches=[{"path": "src/main.c", "line": 1}],
        **extra,
    )


@mcp.tool()
def describe_anchor(target_repo: str, anchor_name: str, scan_id: str | None = None) -> dict[str, object]:
    extra = {"scan_id": scan_id} if scan_id is not None else {}
    return stub_payload(
        "describe_anchor",
        target_repo=target_repo,
        anchor_name=anchor_name,
        description="M1 anchor description stub",
        **extra,
    )
