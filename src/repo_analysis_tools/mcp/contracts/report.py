from repo_analysis_tools.core.errors import ErrorCode
from repo_analysis_tools.core.ids import StableIdKind
from repo_analysis_tools.mcp.contracts.common import ToolContract


REPORT_CONTRACTS = (
    ToolContract(
        name="render_focus_report",
        domain="report",
        input_schema={
            "target_repo": "string",
            "evidence_pack_id": "evidence_pack_<12-hex>",
            "document_type": "issue-analysis|review-report",
        },
        output_schema={
            "target_repo": "string",
            "runtime_root": "string",
            "evidence_pack_id": "evidence_pack_<12-hex>",
            "report_id": "report_<12-hex>",
            "document_type": "issue-analysis|review-report",
            "title": "string",
            "markdown_path": "string",
        },
        stable_ids=(StableIdKind.EVIDENCE_PACK, StableIdKind.REPORT),
        failure_modes=(ErrorCode.INVALID_INPUT, ErrorCode.NOT_FOUND, ErrorCode.INTERNAL),
        recommended_next_tools=("render_module_summary", "export_analysis_bundle"),
    ),
    ToolContract(
        name="render_module_summary",
        domain="report",
        input_schema={
            "target_repo": "string",
            "evidence_pack_id": "evidence_pack_<12-hex>",
            "module_name": "string",
        },
        output_schema={
            "target_repo": "string",
            "runtime_root": "string",
            "evidence_pack_id": "evidence_pack_<12-hex>",
            "report_id": "report_<12-hex>",
            "document_type": "module-summary",
            "title": "string",
            "markdown_path": "string",
        },
        stable_ids=(StableIdKind.EVIDENCE_PACK, StableIdKind.REPORT),
        failure_modes=(ErrorCode.INVALID_INPUT, ErrorCode.NOT_FOUND, ErrorCode.INTERNAL),
        recommended_next_tools=("render_analysis_outline", "export_analysis_bundle"),
    ),
    ToolContract(
        name="render_analysis_outline",
        domain="report",
        input_schema={"target_repo": "string", "focus": "string"},
        output_schema={
            "target_repo": "string",
            "runtime_root": "string",
            "report_id": "report_<12-hex>",
            "document_type": "design-note",
            "title": "string",
            "markdown_path": "string",
            "sections": "list",
        },
        stable_ids=(StableIdKind.REPORT,),
        failure_modes=(ErrorCode.INVALID_INPUT, ErrorCode.NOT_FOUND, ErrorCode.INTERNAL),
        recommended_next_tools=("export_analysis_bundle", "export_scope_snapshot"),
    ),
)
