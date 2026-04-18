from repo_analysis_tools.mcp.app import mcp
from repo_analysis_tools.mcp.tools.shared import stub_payload


@mcp.tool()
def render_focus_report(target_repo: str, evidence_pack_id: str) -> dict[str, object]:
    return stub_payload("render_focus_report", target_repo=target_repo, evidence_pack_id=evidence_pack_id)


@mcp.tool()
def render_module_summary(target_repo: str, evidence_pack_id: str, module_name: str) -> dict[str, object]:
    return stub_payload(
        "render_module_summary",
        target_repo=target_repo,
        evidence_pack_id=evidence_pack_id,
        module_name=module_name,
    )


@mcp.tool()
def render_analysis_outline(target_repo: str, focus: str) -> dict[str, object]:
    return stub_payload(
        "render_analysis_outline",
        target_repo=target_repo,
        focus=focus,
        sections=["summary", "evidence", "risks"],
    )
