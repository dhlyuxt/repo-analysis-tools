from repo_analysis_tools.core.errors import ErrorCode
from repo_analysis_tools.core.ids import StableIdKind
from repo_analysis_tools.mcp.contracts.common import ToolContract


ANCHOR_CONTRACTS = (
    ToolContract(
        name="list_anchors",
        domain="anchors",
        input_schema={"target_repo": "string", "scan_id": "scan_<12-hex>|null"},
        output_schema={
            "target_repo": "string",
            "runtime_root": "string",
            "scan_id": "scan_<12-hex>",
            "anchors": "list",
        },
        stable_ids=(StableIdKind.SCAN,),
        failure_modes=(ErrorCode.INVALID_INPUT, ErrorCode.NOT_FOUND, ErrorCode.INTERNAL),
        recommended_next_tools=("find_anchor", "plan_slice"),
    ),
    ToolContract(
        name="find_anchor",
        domain="anchors",
        input_schema={
            "target_repo": "string",
            "scan_id": "scan_<12-hex>|null",
            "anchor_name": "string",
        },
        output_schema={
            "target_repo": "string",
            "runtime_root": "string",
            "scan_id": "scan_<12-hex>",
            "anchor_name": "string",
            "matches": "list",
        },
        stable_ids=(StableIdKind.SCAN,),
        failure_modes=(ErrorCode.INVALID_INPUT, ErrorCode.NOT_FOUND, ErrorCode.INTERNAL),
        recommended_next_tools=("describe_anchor", "plan_slice"),
    ),
    ToolContract(
        name="describe_anchor",
        domain="anchors",
        input_schema={
            "target_repo": "string",
            "scan_id": "scan_<12-hex>|null",
            "anchor_name": "string",
        },
        output_schema={
            "target_repo": "string",
            "runtime_root": "string",
            "scan_id": "scan_<12-hex>",
            "anchor_name": "string",
            "description": "string",
        },
        stable_ids=(StableIdKind.SCAN,),
        failure_modes=(ErrorCode.INVALID_INPUT, ErrorCode.NOT_FOUND, ErrorCode.INTERNAL),
        recommended_next_tools=("plan_slice", "impact_from_anchor"),
    ),
)
