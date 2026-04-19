from pathlib import Path

from repo_analysis_tools.core.errors import ErrorCode, error_response, ok_response
from repo_analysis_tools.core.paths import runtime_root
from repo_analysis_tools.mcp.app import mcp
from repo_analysis_tools.scope.service import ScopeService


def _scope_base_payload(target_repo: str, scan_id: str) -> dict[str, object]:
    return {
        "target_repo": target_repo,
        "runtime_root": runtime_root(Path(target_repo)).as_posix(),
        "scan_id": scan_id,
    }


@mcp.tool()
def show_scope(target_repo: str, scan_id: str | None = None) -> dict[str, object]:
    try:
        snapshot = ScopeService().load_snapshot(target_repo, scan_id=scan_id)
    except ValueError as exc:
        return error_response(ErrorCode.INVALID_INPUT, str(exc))
    except FileNotFoundError:
        message = (
            f"scope snapshot for scan {scan_id} was not found"
            if scan_id is not None
            else f"no scope snapshots were found for {target_repo}"
        )
        return error_response(ErrorCode.NOT_FOUND, message)
    return ok_response(
        data={
            **_scope_base_payload(target_repo, snapshot.scan_id),
            "scope_summary": snapshot.scope_summary,
            "role_counts": dict(snapshot.role_counts),
        },
        messages=["scope snapshot loaded"],
        recommended_next_tools=["list_scope_nodes", "list_anchors"],
    )


@mcp.tool()
def list_scope_nodes(target_repo: str, scan_id: str | None = None) -> dict[str, object]:
    try:
        snapshot = ScopeService().load_snapshot(target_repo, scan_id=scan_id)
    except ValueError as exc:
        return error_response(ErrorCode.INVALID_INPUT, str(exc))
    except FileNotFoundError:
        message = (
            f"scope snapshot for scan {scan_id} was not found"
            if scan_id is not None
            else f"no scope snapshots were found for {target_repo}"
        )
        return error_response(ErrorCode.NOT_FOUND, message)
    return ok_response(
        data={
            **_scope_base_payload(target_repo, snapshot.scan_id),
            "nodes": [
                {
                    "node_id": node.node_id,
                    "label": node.label,
                    "role": node.role,
                    "file_count": node.file_count,
                }
                for node in snapshot.nodes
            ],
        },
        messages=["scope nodes loaded"],
        recommended_next_tools=["explain_scope_node", "list_anchors"],
    )


@mcp.tool()
def explain_scope_node(target_repo: str, node_id: str, scan_id: str | None = None) -> dict[str, object]:
    service = ScopeService()
    try:
        node = service.explain_node(target_repo, node_id=node_id, scan_id=scan_id)
        snapshot = service.load_snapshot(target_repo, scan_id=scan_id)
    except ValueError as exc:
        return error_response(ErrorCode.INVALID_INPUT, str(exc))
    except FileNotFoundError as exc:
        message = str(exc)
        if scan_id is None and message.startswith("[Errno 2]"):
            message = f"no scope snapshots were found for {target_repo}"
        return error_response(ErrorCode.NOT_FOUND, message)
    return ok_response(
        data={
            **_scope_base_payload(target_repo, snapshot.scan_id),
            "node_id": node.node_id,
            "summary": f"{node.label} is a {node.role} scope node with {node.file_count} related files.",
            "related_files": list(node.related_files),
        },
        messages=["scope node loaded"],
        recommended_next_tools=["list_anchors", "plan_slice"],
    )
