from repo_analysis_tools.mcp.app import mcp
from repo_analysis_tools.mcp.tools.shared import stub_payload


@mcp.tool()
def export_analysis_bundle(target_repo: str, report_id: str) -> dict[str, object]:
    return stub_payload("export_analysis_bundle", target_repo=target_repo, report_id=report_id)


@mcp.tool()
def export_scope_snapshot(target_repo: str, scan_id: str | None = None) -> dict[str, object]:
    extra = {"scan_id": scan_id} if scan_id is not None else {}
    return stub_payload("export_scope_snapshot", target_repo=target_repo, **extra)


@mcp.tool()
def export_evidence_bundle(target_repo: str, evidence_pack_id: str) -> dict[str, object]:
    return stub_payload("export_evidence_bundle", target_repo=target_repo, evidence_pack_id=evidence_pack_id)
