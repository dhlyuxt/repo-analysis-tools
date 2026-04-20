from repo_analysis_tools.core.errors import ErrorCode
from repo_analysis_tools.core.ids import StableIdKind
from repo_analysis_tools.mcp.contracts.common import ToolContract


SCAN_CONTRACTS = (
    ToolContract(
        name="rebuild_repo_snapshot",
        domain="scan",
        input_schema={"target_repo": "string"},
        output_schema={
            "scan_id": "scan_<12-hex>",
            "file_count": "int",
            "symbol_count": "int",
            "function_count": "int",
            "call_edge_count": "int",
        },
        stable_ids=(StableIdKind.SCAN,),
        failure_modes=(ErrorCode.INVALID_INPUT, ErrorCode.RUNTIME_STATE, ErrorCode.INTERNAL),
        recommended_next_tools=("list_priority_files", "get_file_info"),
    ),
)
