from repo_analysis_tools.core.errors import ErrorCode
from repo_analysis_tools.core.ids import StableIdKind
from repo_analysis_tools.mcp.contracts.common import ToolContract


SCOPE_CONTRACTS = (
    ToolContract(
        name="show_scope",
        domain="scope",
        input_schema={"target_repo": "string", "scan_id": "scan_<12-hex>|null"},
        output_schema={
            "target_repo": "string",
            "runtime_root": "string",
            "scan_id": "scan_<12-hex>",
            "scope_summary": "string",
        },
        stable_ids=(StableIdKind.SCAN,),
        failure_modes=(ErrorCode.INVALID_INPUT, ErrorCode.NOT_FOUND, ErrorCode.INTERNAL),
        recommended_next_tools=("list_scope_nodes", "list_anchors"),
    ),
    ToolContract(
        name="list_scope_nodes",
        domain="scope",
        input_schema={"target_repo": "string", "scan_id": "scan_<12-hex>|null"},
        output_schema={
            "target_repo": "string",
            "runtime_root": "string",
            "scan_id": "scan_<12-hex>",
            "nodes": "list",
        },
        stable_ids=(StableIdKind.SCAN,),
        failure_modes=(ErrorCode.INVALID_INPUT, ErrorCode.NOT_FOUND, ErrorCode.INTERNAL),
        recommended_next_tools=("explain_scope_node", "list_anchors"),
    ),
    ToolContract(
        name="explain_scope_node",
        domain="scope",
        input_schema={
            "target_repo": "string",
            "scan_id": "scan_<12-hex>|null",
            "node_id": "string",
        },
        output_schema={
            "target_repo": "string",
            "runtime_root": "string",
            "scan_id": "scan_<12-hex>",
            "node_id": "string",
            "summary": "string",
        },
        stable_ids=(StableIdKind.SCAN,),
        failure_modes=(ErrorCode.INVALID_INPUT, ErrorCode.NOT_FOUND, ErrorCode.INTERNAL),
        recommended_next_tools=("list_anchors", "plan_slice"),
    ),
)
