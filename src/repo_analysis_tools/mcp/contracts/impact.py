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
            "impact_id": "impact_<12-hex>",
            "seed_kind": "string",
            "changed_paths": "list",
            "direct_impacts": "list",
            "likely_propagation": "list",
            "uncertainty_notes": "list",
            "recommended_regression_focus": "list",
            "summary": "string",
        },
        stable_ids=(StableIdKind.SCAN, StableIdKind.IMPACT),
        failure_modes=(ErrorCode.INVALID_INPUT, ErrorCode.NOT_FOUND, ErrorCode.INTERNAL),
        recommended_next_tools=("summarize_impact", "plan_slice"),
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
            "impact_id": "impact_<12-hex>",
            "seed_kind": "string",
            "anchor_name": "string",
            "direct_impacts": "list",
            "likely_propagation": "list",
            "uncertainty_notes": "list",
            "recommended_regression_focus": "list",
            "summary": "string",
        },
        stable_ids=(StableIdKind.SCAN, StableIdKind.IMPACT),
        failure_modes=(ErrorCode.INVALID_INPUT, ErrorCode.NOT_FOUND, ErrorCode.INTERNAL),
        recommended_next_tools=("summarize_impact", "plan_slice"),
    ),
    ToolContract(
        name="summarize_impact",
        domain="impact",
        input_schema={"target_repo": "string", "impact_id": "impact_<12-hex>"},
        output_schema={
            "target_repo": "string",
            "runtime_root": "string",
            "impact_id": "impact_<12-hex>",
            "scan_id": "scan_<12-hex>",
            "confirmed_impact": "list",
            "likely_propagation": "list",
            "regression_focus": "list",
            "blind_spots": "list",
            "risks": "list",
            "summary": "string",
        },
        stable_ids=(StableIdKind.SCAN, StableIdKind.IMPACT),
        failure_modes=(ErrorCode.INVALID_INPUT, ErrorCode.NOT_FOUND, ErrorCode.INTERNAL),
        recommended_next_tools=("plan_slice", "build_evidence_pack"),
    ),
)
