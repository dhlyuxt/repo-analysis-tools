from pathlib import Path

from repo_analysis_tools.core.errors import ErrorCode, error_response, ok_response
from repo_analysis_tools.core.paths import runtime_root
from repo_analysis_tools.mcp.app import mcp
from repo_analysis_tools.report.service import ReportService


@mcp.tool()
def render_focus_report(
    target_repo: str,
    evidence_pack_id: str,
    document_type: str = "review-report",
) -> dict[str, object]:
    try:
        artifact = ReportService().render_focus_report(target_repo, evidence_pack_id, document_type)
    except ValueError as exc:
        return error_response(ErrorCode.INVALID_INPUT, str(exc))
    except FileNotFoundError as exc:
        return error_response(ErrorCode.NOT_FOUND, str(exc))
    return ok_response(
        data={
            "target_repo": target_repo,
            "runtime_root": runtime_root(Path(target_repo)).as_posix(),
            "evidence_pack_id": evidence_pack_id,
            "report_id": artifact.report_id,
            "document_type": artifact.document_type,
            "title": artifact.title,
            "markdown_path": artifact.markdown_path,
        },
        messages=["focus report rendered"],
        recommended_next_tools=["render_module_summary", "export_analysis_bundle"],
    )


@mcp.tool()
def render_module_summary(target_repo: str, evidence_pack_id: str, module_name: str) -> dict[str, object]:
    try:
        artifact = ReportService().render_module_summary(target_repo, evidence_pack_id, module_name)
    except ValueError as exc:
        return error_response(ErrorCode.INVALID_INPUT, str(exc))
    except FileNotFoundError as exc:
        return error_response(ErrorCode.NOT_FOUND, str(exc))
    return ok_response(
        data={
            "target_repo": target_repo,
            "runtime_root": runtime_root(Path(target_repo)).as_posix(),
            "evidence_pack_id": evidence_pack_id,
            "report_id": artifact.report_id,
            "document_type": artifact.document_type,
            "title": artifact.title,
            "markdown_path": artifact.markdown_path,
        },
        messages=["module summary rendered"],
        recommended_next_tools=["render_analysis_outline", "export_analysis_bundle"],
    )


@mcp.tool()
def render_analysis_outline(target_repo: str, focus: str) -> dict[str, object]:
    try:
        artifact = ReportService().render_analysis_outline(target_repo, focus)
    except ValueError as exc:
        return error_response(ErrorCode.INVALID_INPUT, str(exc))
    except FileNotFoundError as exc:
        return error_response(ErrorCode.NOT_FOUND, str(exc))
    return ok_response(
        data={
            "target_repo": target_repo,
            "runtime_root": runtime_root(Path(target_repo)).as_posix(),
            "report_id": artifact.report_id,
            "document_type": artifact.document_type,
            "title": artifact.title,
            "markdown_path": artifact.markdown_path,
            "sections": artifact.section_titles,
        },
        messages=["analysis outline rendered"],
        recommended_next_tools=["export_analysis_bundle", "export_scope_snapshot"],
    )
