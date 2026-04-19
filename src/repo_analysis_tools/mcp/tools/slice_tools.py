from pathlib import Path

from repo_analysis_tools.core.errors import ErrorCode, error_response, ok_response
from repo_analysis_tools.core.paths import runtime_root
from repo_analysis_tools.mcp.app import mcp
from repo_analysis_tools.slice.service import SliceService


def _slice_base_payload(target_repo: str, slice_id: str) -> dict[str, object]:
    return {
        "target_repo": target_repo,
        "runtime_root": runtime_root(Path(target_repo)).as_posix(),
        "slice_id": slice_id,
    }


@mcp.tool()
def plan_slice(target_repo: str, question: str) -> dict[str, object]:
    try:
        manifest = SliceService().plan(target_repo, question)
    except ValueError as exc:
        return error_response(ErrorCode.INVALID_INPUT, str(exc))
    except FileNotFoundError as exc:
        return error_response(ErrorCode.NOT_FOUND, str(exc))
    return ok_response(
        data={
            **_slice_base_payload(target_repo, manifest.slice_id),
            "scan_id": manifest.scan_id,
            "query_kind": manifest.query_kind,
            "status": manifest.status,
            "selected_files": manifest.selected_files,
            "selected_anchor_names": manifest.selected_anchor_names,
            "notes": manifest.notes,
        },
        messages=["slice manifest planned"],
        recommended_next_tools=["inspect_slice", "build_evidence_pack"],
    )


@mcp.tool()
def expand_slice(target_repo: str, slice_id: str) -> dict[str, object]:
    try:
        expansion = SliceService().expand(target_repo, slice_id)
    except ValueError as exc:
        return error_response(ErrorCode.INVALID_INPUT, str(exc))
    except FileNotFoundError as exc:
        return error_response(ErrorCode.NOT_FOUND, str(exc))
    return ok_response(
        data={
            **_slice_base_payload(target_repo, expansion.slice_id),
            "expanded": expansion.expanded,
        },
        messages=["slice expansion evaluated"],
        recommended_next_tools=["inspect_slice", "build_evidence_pack"],
    )


@mcp.tool()
def inspect_slice(target_repo: str, slice_id: str) -> dict[str, object]:
    try:
        inspection = SliceService().inspect(target_repo, slice_id)
    except ValueError as exc:
        return error_response(ErrorCode.INVALID_INPUT, str(exc))
    except FileNotFoundError as exc:
        return error_response(ErrorCode.NOT_FOUND, str(exc))
    return ok_response(
        data={
            **_slice_base_payload(target_repo, inspection.slice_id),
            "members": inspection.members,
        },
        messages=["slice manifest loaded"],
        recommended_next_tools=["build_evidence_pack", "render_focus_report"],
    )
