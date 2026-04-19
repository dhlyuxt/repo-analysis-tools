from repo_analysis_tools.core.errors import ErrorCode
from repo_analysis_tools.core.ids import StableIdKind
from repo_analysis_tools.mcp.contracts.common import ToolContract


SLICE_CONTRACTS = (
    ToolContract(
        name="plan_slice",
        domain="slice",
        input_schema={"target_repo": "string", "question": "string"},
        output_schema={
            "target_repo": "string",
            "runtime_root": "string",
            "slice_id": "slice_<12-hex>",
            "scan_id": "scan_<12-hex>",
            "query_kind": "string",
            "status": "string",
            "selected_files": "list",
            "selected_anchor_names": "list",
            "notes": "list",
        },
        stable_ids=(StableIdKind.SLICE,),
        failure_modes=(ErrorCode.INVALID_INPUT, ErrorCode.NOT_FOUND, ErrorCode.INTERNAL),
        recommended_next_tools=("inspect_slice", "build_evidence_pack"),
    ),
    ToolContract(
        name="expand_slice",
        domain="slice",
        input_schema={"target_repo": "string", "slice_id": "slice_<12-hex>"},
        output_schema={
            "target_repo": "string",
            "runtime_root": "string",
            "slice_id": "slice_<12-hex>",
            "expanded": "bool",
        },
        stable_ids=(StableIdKind.SLICE,),
        failure_modes=(ErrorCode.INVALID_INPUT, ErrorCode.NOT_FOUND, ErrorCode.INTERNAL),
        recommended_next_tools=("inspect_slice", "build_evidence_pack"),
    ),
    ToolContract(
        name="inspect_slice",
        domain="slice",
        input_schema={"target_repo": "string", "slice_id": "slice_<12-hex>"},
        output_schema={
            "target_repo": "string",
            "runtime_root": "string",
            "slice_id": "slice_<12-hex>",
            "members": "list",
        },
        stable_ids=(StableIdKind.SLICE,),
        failure_modes=(ErrorCode.INVALID_INPUT, ErrorCode.NOT_FOUND, ErrorCode.INTERNAL),
        recommended_next_tools=("build_evidence_pack", "render_focus_report"),
    ),
)
