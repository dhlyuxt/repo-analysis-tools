from repo_analysis_tools.core.errors import ErrorCode
from repo_analysis_tools.core.ids import StableIdKind
from repo_analysis_tools.mcp.contracts.common import ToolContract


EVIDENCE_CONTRACTS = (
    ToolContract(
        name="build_evidence_pack",
        domain="evidence",
        input_schema={"target_repo": "string", "slice_id": "slice_<12-hex>"},
        output_schema={
            "target_repo": "string",
            "runtime_root": "string",
            "slice_id": "slice_<12-hex>",
            "evidence_pack_id": "evidence_pack_<12-hex>",
            "citation_count": "int",
            "summary": "string",
        },
        stable_ids=(StableIdKind.SLICE, StableIdKind.EVIDENCE_PACK),
        failure_modes=(ErrorCode.INVALID_INPUT, ErrorCode.NOT_FOUND, ErrorCode.INTERNAL),
        recommended_next_tools=("read_evidence_pack", "open_span"),
    ),
    ToolContract(
        name="read_evidence_pack",
        domain="evidence",
        input_schema={"target_repo": "string", "evidence_pack_id": "evidence_pack_<12-hex>"},
        output_schema={
            "target_repo": "string",
            "runtime_root": "string",
            "evidence_pack_id": "evidence_pack_<12-hex>",
            "summary": "string",
            "citations": "list",
        },
        stable_ids=(StableIdKind.EVIDENCE_PACK,),
        failure_modes=(ErrorCode.INVALID_INPUT, ErrorCode.NOT_FOUND, ErrorCode.INTERNAL),
        recommended_next_tools=("open_span", "describe_anchor"),
    ),
    ToolContract(
        name="open_span",
        domain="evidence",
        input_schema={
            "target_repo": "string",
            "evidence_pack_id": "evidence_pack_<12-hex>",
            "path": "string",
            "line_start": "int",
            "line_end": "int",
        },
        output_schema={
            "target_repo": "string",
            "runtime_root": "string",
            "evidence_pack_id": "evidence_pack_<12-hex>",
            "path": "string",
            "line_start": "int",
            "line_end": "int",
            "lines": "list",
        },
        stable_ids=(StableIdKind.EVIDENCE_PACK,),
        failure_modes=(ErrorCode.INVALID_INPUT, ErrorCode.NOT_FOUND, ErrorCode.INTERNAL),
        recommended_next_tools=("read_evidence_pack", "describe_anchor"),
    ),
)
