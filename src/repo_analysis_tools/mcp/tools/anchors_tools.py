from pathlib import Path

from repo_analysis_tools.anchors.service import AnchorService
from repo_analysis_tools.core.errors import ErrorCode, error_response, ok_response
from repo_analysis_tools.core.paths import runtime_root
from repo_analysis_tools.mcp.app import mcp


def _anchor_base_payload(target_repo: str, scan_id: str) -> dict[str, object]:
    return {
        "target_repo": target_repo,
        "runtime_root": runtime_root(Path(target_repo)).as_posix(),
        "scan_id": scan_id,
    }


@mcp.tool()
def list_anchors(target_repo: str, scan_id: str | None = None) -> dict[str, object]:
    try:
        snapshot = AnchorService().load_snapshot(target_repo, scan_id=scan_id)
    except ValueError as exc:
        return error_response(ErrorCode.INVALID_INPUT, str(exc))
    except FileNotFoundError:
        message = (
            f"anchor snapshot for scan {scan_id} was not found"
            if scan_id is not None
            else f"no anchor snapshots were found for {target_repo}"
        )
        return error_response(ErrorCode.NOT_FOUND, message)
    return ok_response(
        data={
            **_anchor_base_payload(target_repo, snapshot.scan_id),
            "anchors": [
                {
                    "anchor_id": anchor.anchor_id,
                    "scope_node_id": anchor.scope_node_id,
                    "kind": anchor.kind,
                    "name": anchor.name,
                    "path": anchor.path,
                    "start_line": anchor.start_line,
                    "end_line": anchor.end_line,
                }
                for anchor in snapshot.anchors
            ],
        },
        messages=["anchor snapshot loaded"],
        recommended_next_tools=["find_anchor", "plan_slice"],
    )


@mcp.tool()
def find_anchor(target_repo: str, anchor_name: str, scan_id: str | None = None) -> dict[str, object]:
    service = AnchorService()
    try:
        snapshot = service.load_snapshot(target_repo, scan_id=scan_id)
        matches = service.find_anchor_matches(target_repo, anchor_name, scan_id=scan_id)
    except ValueError as exc:
        return error_response(ErrorCode.INVALID_INPUT, str(exc))
    except FileNotFoundError:
        message = (
            f"anchor snapshot for scan {scan_id} was not found"
            if scan_id is not None
            else f"no anchor snapshots were found for {target_repo}"
        )
        return error_response(ErrorCode.NOT_FOUND, message)
    return ok_response(
        data={
            **_anchor_base_payload(target_repo, snapshot.scan_id),
            "anchor_name": anchor_name,
            "matches": [
                {
                    "anchor_id": anchor.anchor_id,
                    "scope_node_id": anchor.scope_node_id,
                    "kind": anchor.kind,
                    "name": anchor.name,
                    "path": anchor.path,
                    "start_line": anchor.start_line,
                    "end_line": anchor.end_line,
                }
                for anchor in matches
            ],
        },
        messages=["anchor matches loaded"],
        recommended_next_tools=["describe_anchor", "plan_slice"],
    )


@mcp.tool()
def describe_anchor(target_repo: str, anchor_name: str, scan_id: str | None = None) -> dict[str, object]:
    service = AnchorService()
    try:
        snapshot = service.load_snapshot(target_repo, scan_id=scan_id)
        description = service.describe_anchor(target_repo, anchor_name, scan_id=scan_id)
    except ValueError as exc:
        return error_response(ErrorCode.INVALID_INPUT, str(exc))
    except FileNotFoundError as exc:
        return error_response(ErrorCode.NOT_FOUND, str(exc))
    return ok_response(
        data={
            **_anchor_base_payload(target_repo, snapshot.scan_id),
            "anchor_name": anchor_name,
            "description": description.description,
            "relations": [
                {
                    "kind": relation.kind,
                    "source_name": relation.source_name,
                    "target_name": relation.target_name,
                    "target_anchor_id": relation.target_anchor_id,
                    "target_path": relation.target_path,
                    "line": relation.line,
                }
                for relation in description.relations
            ],
        },
        messages=["anchor description loaded"],
        recommended_next_tools=["plan_slice", "impact_from_anchor"],
    )
