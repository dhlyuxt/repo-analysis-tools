from repo_analysis_tools.core.errors import ErrorCode
from repo_analysis_tools.core.ids import StableIdKind
from repo_analysis_tools.mcp.contracts.common import ToolContract


IMPACT_CONTRACTS = (
    ToolContract(
        name="impact_from_paths",
        domain="impact",
        input_schema={"target_repo": "string", "scan_id": "scan_<12-hex>|null", "paths": "list"},
        output_schema={
            "target_repo": "string",
            "runtime_root": "string",
            "scan_id": "scan_<12-hex>",
            "impact_summary": "string",
        },
        stable_ids=(StableIdKind.SCAN,),
        failure_modes=(ErrorCode.INVALID_INPUT, ErrorCode.NOT_FOUND, ErrorCode.INTERNAL),
        recommended_next_tools=("summarize_impact", "build_evidence_pack"),
    ),
    ToolContract(
        name="impact_from_anchor",
        domain="impact",
        input_schema={
            "target_repo": "string",
            "scan_id": "scan_<12-hex>|null",
            "anchor_name": "string",
        },
        output_schema={
            "target_repo": "string",
            "runtime_root": "string",
            "scan_id": "scan_<12-hex>",
            "impact_summary": "string",
        },
        stable_ids=(StableIdKind.SCAN,),
        failure_modes=(ErrorCode.INVALID_INPUT, ErrorCode.NOT_FOUND, ErrorCode.INTERNAL),
        recommended_next_tools=("summarize_impact", "build_evidence_pack"),
    ),
    ToolContract(
        name="summarize_impact",
        domain="impact",
        input_schema={"target_repo": "string", "scan_id": "scan_<12-hex>|null", "focus": "string"},
        output_schema={
            "target_repo": "string",
            "runtime_root": "string",
            "scan_id": "scan_<12-hex>",
            "risks": "list",
        },
        stable_ids=(StableIdKind.SCAN,),
        failure_modes=(ErrorCode.INVALID_INPUT, ErrorCode.NOT_FOUND, ErrorCode.INTERNAL),
        recommended_next_tools=("render_analysis_outline", "render_focus_report"),
    ),
)
