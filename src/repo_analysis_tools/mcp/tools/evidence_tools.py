from repo_analysis_tools.mcp.app import mcp
from repo_analysis_tools.mcp.tools.shared import stub_payload


@mcp.tool()
def build_evidence_pack(target_repo: str, slice_id: str) -> dict[str, object]:
    return stub_payload("build_evidence_pack", target_repo=target_repo, slice_id=slice_id)


@mcp.tool()
def read_evidence_pack(target_repo: str, evidence_pack_id: str) -> dict[str, object]:
    return stub_payload(
        "read_evidence_pack",
        target_repo=target_repo,
        evidence_pack_id=evidence_pack_id,
        summary="M1 evidence pack stub",
    )


@mcp.tool()
def open_span(target_repo: str, evidence_pack_id: str, path: str, line_start: int, line_end: int) -> dict[str, object]:
    return stub_payload(
        "open_span",
        target_repo=target_repo,
        evidence_pack_id=evidence_pack_id,
        path=path,
        lines=["/* M1 span stub */"],
    )
