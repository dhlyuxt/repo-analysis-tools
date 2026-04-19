from pathlib import Path

from repo_analysis_tools.core.errors import ErrorCode, error_response, ok_response
from repo_analysis_tools.core.paths import runtime_root
from repo_analysis_tools.export.service import ExportService
from repo_analysis_tools.mcp.app import mcp

@mcp.tool()
def export_analysis_bundle(target_repo: str, report_id: str) -> dict[str, object]:
    try:
        artifact = ExportService().export_analysis_bundle(target_repo, report_id)
    except ValueError as exc:
        return error_response(ErrorCode.INVALID_INPUT, str(exc))
    except FileNotFoundError as exc:
        return error_response(ErrorCode.NOT_FOUND, str(exc))
    return ok_response(
        data={
            "target_repo": target_repo,
            "runtime_root": runtime_root(Path(target_repo)).as_posix(),
            "report_id": artifact.report_id,
            "export_id": artifact.export_id,
            "export_kind": artifact.export_kind,
            "manifest_path": artifact.manifest_path,
            "payload_path": artifact.payload_path,
            "copied_markdown_path": artifact.copied_markdown_path,
            "freshness_state": artifact.freshness.state,
        },
        messages=["analysis bundle exported", artifact.freshness.summary],
        recommended_next_tools=["export_scope_snapshot", "export_evidence_bundle"],
    )


@mcp.tool()
def export_scope_snapshot(target_repo: str, scan_id: str | None = None) -> dict[str, object]:
    try:
        artifact = ExportService().export_scope_snapshot(target_repo, scan_id)
    except ValueError as exc:
        return error_response(ErrorCode.INVALID_INPUT, str(exc))
    except FileNotFoundError as exc:
        return error_response(ErrorCode.NOT_FOUND, str(exc))
    return ok_response(
        data={
            "target_repo": target_repo,
            "runtime_root": runtime_root(Path(target_repo)).as_posix(),
            "scan_id": artifact.scan_id,
            "export_id": artifact.export_id,
            "export_kind": artifact.export_kind,
            "manifest_path": artifact.manifest_path,
            "payload_path": artifact.payload_path,
            "freshness_state": artifact.freshness.state,
        },
        messages=["scope snapshot exported", artifact.freshness.summary],
        recommended_next_tools=["export_evidence_bundle"],
    )


@mcp.tool()
def export_evidence_bundle(target_repo: str, evidence_pack_id: str) -> dict[str, object]:
    try:
        artifact = ExportService().export_evidence_bundle(target_repo, evidence_pack_id)
    except ValueError as exc:
        return error_response(ErrorCode.INVALID_INPUT, str(exc))
    except FileNotFoundError as exc:
        return error_response(ErrorCode.NOT_FOUND, str(exc))
    return ok_response(
        data={
            "target_repo": target_repo,
            "runtime_root": runtime_root(Path(target_repo)).as_posix(),
            "evidence_pack_id": artifact.evidence_pack_id,
            "scan_id": artifact.scan_id,
            "export_id": artifact.export_id,
            "export_kind": artifact.export_kind,
            "manifest_path": artifact.manifest_path,
            "payload_path": artifact.payload_path,
            "freshness_state": artifact.freshness.state,
        },
        messages=["evidence bundle exported", artifact.freshness.summary],
        recommended_next_tools=[],
    )
