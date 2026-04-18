from repo_analysis_tools.mcp.app import mcp
from repo_analysis_tools.mcp.tools.shared import stub_payload


@mcp.tool()
def impact_from_paths(target_repo: str, paths: list[str], scan_id: str | None = None) -> dict[str, object]:
    extra = {"scan_id": scan_id} if scan_id is not None else {}
    return stub_payload(
        "impact_from_paths",
        target_repo=target_repo,
        impact_summary="M1 path impact stub",
        **extra,
    )


@mcp.tool()
def impact_from_anchor(target_repo: str, anchor_name: str, scan_id: str | None = None) -> dict[str, object]:
    extra = {"scan_id": scan_id} if scan_id is not None else {}
    return stub_payload(
        "impact_from_anchor",
        target_repo=target_repo,
        impact_summary="M1 anchor impact stub",
        **extra,
    )


@mcp.tool()
def summarize_impact(target_repo: str, focus: str, scan_id: str | None = None) -> dict[str, object]:
    extra = {"scan_id": scan_id} if scan_id is not None else {}
    return stub_payload(
        "summarize_impact",
        target_repo=target_repo,
        risks=["M1 stub risk"],
        **extra,
    )
