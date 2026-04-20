from repo_analysis_tools.anchors.store import AnchorStore
from repo_analysis_tools.core.errors import ErrorCode, error_response, ok_response
from repo_analysis_tools.mcp.app import mcp
from repo_analysis_tools.mcp.scan_registry import remember_scan
from repo_analysis_tools.scan.service import ScanService


@mcp.tool()
def rebuild_repo_snapshot(target_repo: str) -> dict[str, object]:
    try:
        snapshot = ScanService().scan(target_repo)
        anchor_snapshot = AnchorStore.for_repo(target_repo).load(scan_id=snapshot.scan_id)
        remember_scan(snapshot.scan_id, snapshot.repo_root)
    except ValueError as exc:
        return error_response(ErrorCode.INVALID_INPUT, str(exc))
    except FileNotFoundError as exc:
        return error_response(ErrorCode.NOT_FOUND, str(exc))
    data = {
        "scan_id": snapshot.scan_id,
        "file_count": snapshot.file_count,
        "symbol_count": len(anchor_snapshot.anchors),
        "function_count": sum(1 for anchor in anchor_snapshot.anchors if anchor.kind == "function_definition"),
        "call_edge_count": sum(1 for relation in anchor_snapshot.relations if relation.kind == "direct_call"),
    }
    return ok_response(
        data=data,
        messages=["repo snapshot rebuilt"],
        recommended_next_tools=["list_priority_files", "get_file_info"],
    )
