from __future__ import annotations

from repo_analysis_tools.core.errors import ErrorCode, error_response, ok_response
from repo_analysis_tools.mcp.app import mcp
from repo_analysis_tools.mcp.scan_registry import repo_root_for_scan
from repo_analysis_tools.query.service import QueryService


def _query_service(scan_id: str) -> tuple[QueryService, str]:
    return QueryService(), repo_root_for_scan(scan_id)


def _symbol_rows(rows) -> list[dict[str, object]]:
    return [dict(row.__dict__) for row in rows]


def _call_relation_rows(rows) -> list[dict[str, object]]:
    return [
        {
            **dict(row.__dict__),
            "call_lines": list(row.call_lines),
        }
        for row in rows
    ]


def _internal_error(exc: Exception) -> dict[str, object]:
    return error_response(ErrorCode.INTERNAL, str(exc))


@mcp.tool()
def list_priority_files(scan_id: str) -> dict[str, object]:
    try:
        service, repo_root = _query_service(scan_id)
        rows = service.list_priority_files(repo_root, scan_id)
    except ValueError as exc:
        return error_response(ErrorCode.INVALID_INPUT, str(exc))
    except FileNotFoundError as exc:
        return error_response(ErrorCode.NOT_FOUND, str(exc))
    except Exception as exc:
        return _internal_error(exc)
    return ok_response(
        data={"files": [{"path": row.path, "priority_score": row.priority_score} for row in rows]},
        messages=[],
        recommended_next_tools=["get_file_info", "list_file_symbols"],
    )


@mcp.tool()
def get_file_info(scan_id: str, path: str) -> dict[str, object]:
    try:
        service, repo_root = _query_service(scan_id)
        row = service.get_file_info(repo_root, scan_id, path)
    except ValueError as exc:
        return error_response(ErrorCode.INVALID_INPUT, str(exc))
    except FileNotFoundError as exc:
        return error_response(ErrorCode.NOT_FOUND, str(exc))
    except Exception as exc:
        return _internal_error(exc)
    return ok_response(
        data=dict(row.__dict__),
        messages=[],
        recommended_next_tools=["list_file_symbols", "find_root_functions"],
    )


@mcp.tool()
def list_file_symbols(scan_id: str, paths: list[str]) -> dict[str, object]:
    try:
        service, repo_root = _query_service(scan_id)
        rows = service.list_file_symbols(repo_root, scan_id, paths)
    except ValueError as exc:
        return error_response(ErrorCode.INVALID_INPUT, str(exc))
    except FileNotFoundError as exc:
        return error_response(ErrorCode.NOT_FOUND, str(exc))
    except Exception as exc:
        return _internal_error(exc)
    return ok_response(
        data={
            "files": [
                {
                    "path": row.path,
                    "symbols": _symbol_rows(row.symbols),
                }
                for row in rows
            ]
        },
        messages=[],
        recommended_next_tools=["open_symbol_context", "resolve_symbols"],
    )


@mcp.tool()
def resolve_symbols(scan_id: str, symbol_name: str) -> dict[str, object]:
    try:
        service, repo_root = _query_service(scan_id)
        result = service.resolve_symbols(repo_root, scan_id, symbol_name)
    except ValueError as exc:
        return error_response(ErrorCode.INVALID_INPUT, str(exc))
    except FileNotFoundError as exc:
        return error_response(ErrorCode.NOT_FOUND, str(exc))
    except Exception as exc:
        return _internal_error(exc)
    return ok_response(
        data={
            "match_count": result.match_count,
            "matches": _symbol_rows(result.matches),
        },
        messages=[],
        recommended_next_tools=["open_symbol_context", "query_call_relations"],
    )


@mcp.tool()
def open_symbol_context(scan_id: str, symbol_id: str, context_lines: int) -> dict[str, object]:
    try:
        service, repo_root = _query_service(scan_id)
        row = service.open_symbol_context(repo_root, scan_id, symbol_id, context_lines)
    except ValueError as exc:
        return error_response(ErrorCode.INVALID_INPUT, str(exc))
    except FileNotFoundError as exc:
        return error_response(ErrorCode.NOT_FOUND, str(exc))
    except Exception as exc:
        return _internal_error(exc)
    return ok_response(
        data={
            **dict(row.__dict__),
            "lines": list(row.lines),
        },
        messages=[],
        recommended_next_tools=["query_call_relations", "find_call_paths"],
    )


@mcp.tool()
def query_call_relations(scan_id: str, function_id: str) -> dict[str, object]:
    try:
        service, repo_root = _query_service(scan_id)
        result = service.query_call_relations(repo_root, scan_id, function_id)
    except ValueError as exc:
        return error_response(ErrorCode.INVALID_INPUT, str(exc))
    except FileNotFoundError as exc:
        return error_response(ErrorCode.NOT_FOUND, str(exc))
    except Exception as exc:
        return _internal_error(exc)
    return ok_response(
        data={
            "callers": _call_relation_rows(result.callers),
            "callees": _call_relation_rows(result.callees),
            "non_resolved_callees": _call_relation_rows(result.non_resolved_callees),
        },
        messages=[],
        recommended_next_tools=["find_call_paths", "find_root_functions"],
    )


@mcp.tool()
def find_root_functions(scan_id: str, paths: list[str]) -> dict[str, object]:
    try:
        service, repo_root = _query_service(scan_id)
        rows = service.find_root_functions(repo_root, scan_id, paths)
    except ValueError as exc:
        return error_response(ErrorCode.INVALID_INPUT, str(exc))
    except FileNotFoundError as exc:
        return error_response(ErrorCode.NOT_FOUND, str(exc))
    except Exception as exc:
        return _internal_error(exc)
    return ok_response(
        data={"roots": _symbol_rows(rows)},
        messages=[],
        recommended_next_tools=["find_call_paths", "open_symbol_context"],
    )


@mcp.tool()
def find_call_paths(scan_id: str, from_function_id: str, to_function_id: str) -> dict[str, object]:
    try:
        service, repo_root = _query_service(scan_id)
        result = service.find_call_paths(repo_root, scan_id, from_function_id, to_function_id)
    except ValueError as exc:
        return error_response(ErrorCode.INVALID_INPUT, str(exc))
    except FileNotFoundError as exc:
        return error_response(ErrorCode.NOT_FOUND, str(exc))
    except Exception as exc:
        return _internal_error(exc)
    return ok_response(
        data={
            "status": result.status,
            "returned_path_count": result.returned_path_count,
            "truncated": result.truncated,
            "paths": [
                {
                    "hop_count": path.hop_count,
                    "nodes": _symbol_rows(path.nodes),
                    "call_lines": list(path.call_lines),
                }
                for path in result.paths
            ],
        },
        messages=[],
        recommended_next_tools=["open_symbol_context", "query_call_relations"],
    )
