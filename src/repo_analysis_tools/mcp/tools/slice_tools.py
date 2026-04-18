from repo_analysis_tools.mcp.app import mcp
from repo_analysis_tools.mcp.tools.shared import stub_payload


@mcp.tool()
def plan_slice(target_repo: str, question: str) -> dict[str, object]:
    return stub_payload(
        "plan_slice",
        target_repo=target_repo,
        seed_summary="M1 slice planning stub",
    )


@mcp.tool()
def expand_slice(target_repo: str, slice_id: str) -> dict[str, object]:
    return stub_payload("expand_slice", target_repo=target_repo, slice_id=slice_id, expanded=True)


@mcp.tool()
def inspect_slice(target_repo: str, slice_id: str) -> dict[str, object]:
    return stub_payload(
        "inspect_slice",
        target_repo=target_repo,
        slice_id=slice_id,
        members=[{"path": "src/main.c", "reason": "seed"}],
    )
