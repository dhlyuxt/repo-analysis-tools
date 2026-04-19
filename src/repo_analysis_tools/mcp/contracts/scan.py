from repo_analysis_tools.core.errors import ErrorCode
from repo_analysis_tools.core.ids import StableIdKind
from repo_analysis_tools.mcp.contracts.common import ToolContract


SCAN_CONTRACTS = (
    ToolContract(
        name="scan_repo",
        domain="scan",
        input_schema={"target_repo": "string"},
        output_schema={
            "target_repo": "string",
            "runtime_root": "string",
            "scan_id": "scan_<12-hex>",
            "repo_root": "string",
            "file_count": "int",
            "latest_completed_at": "iso8601",
            "git_head": "string|null",
            "workspace_dirty": "bool|null",
        },
        stable_ids=(StableIdKind.SCAN,),
        failure_modes=(ErrorCode.INVALID_INPUT, ErrorCode.RUNTIME_STATE, ErrorCode.INTERNAL),
        recommended_next_tools=("get_scan_status", "show_scope"),
    ),
    ToolContract(
        name="refresh_scan",
        domain="scan",
        input_schema={"target_repo": "string", "scan_id": "scan_<12-hex>"},
        output_schema={
            "target_repo": "string",
            "runtime_root": "string",
            "scan_id": "scan_<12-hex>",
            "repo_root": "string",
            "file_count": "int",
            "latest_completed_at": "iso8601",
            "git_head": "string|null",
            "workspace_dirty": "bool|null",
        },
        stable_ids=(StableIdKind.SCAN,),
        failure_modes=(ErrorCode.INVALID_INPUT, ErrorCode.NOT_FOUND, ErrorCode.INTERNAL),
        recommended_next_tools=("get_scan_status", "show_scope"),
    ),
    ToolContract(
        name="get_scan_status",
        domain="scan",
        input_schema={"target_repo": "string", "scan_id": "scan_<12-hex>|null"},
        output_schema={
            "target_repo": "string",
            "runtime_root": "string",
            "scan_id": "scan_<12-hex>",
            "repo_root": "string",
            "file_count": "int",
            "latest_completed_at": "iso8601",
            "git_head": "string|null",
            "workspace_dirty": "bool|null",
        },
        stable_ids=(StableIdKind.SCAN,),
        failure_modes=(ErrorCode.INVALID_INPUT, ErrorCode.NOT_FOUND, ErrorCode.INTERNAL),
        recommended_next_tools=("show_scope", "list_anchors"),
    ),
)
