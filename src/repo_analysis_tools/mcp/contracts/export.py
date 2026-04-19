from repo_analysis_tools.core.errors import ErrorCode
from repo_analysis_tools.core.ids import StableIdKind
from repo_analysis_tools.mcp.contracts.common import ToolContract


EXPORT_CONTRACTS = (
    ToolContract(
        name="export_analysis_bundle",
        domain="export",
        input_schema={"target_repo": "string", "report_id": "report_<12-hex>"},
        output_schema={
            "target_repo": "string",
            "runtime_root": "string",
            "report_id": "report_<12-hex>",
            "export_id": "export_<12-hex>",
            "export_kind": "analysis-bundle",
            "manifest_path": "string",
            "payload_path": "string",
            "copied_markdown_path": "string",
            "freshness_state": "fresh|stale|unknown",
        },
        stable_ids=(StableIdKind.REPORT, StableIdKind.EXPORT),
        failure_modes=(ErrorCode.INVALID_INPUT, ErrorCode.NOT_FOUND, ErrorCode.INTERNAL),
        recommended_next_tools=("export_scope_snapshot", "export_evidence_bundle"),
    ),
    ToolContract(
        name="export_scope_snapshot",
        domain="export",
        input_schema={"target_repo": "string", "scan_id": "scan_<12-hex>|null"},
        output_schema={
            "target_repo": "string",
            "runtime_root": "string",
            "scan_id": "scan_<12-hex>",
            "export_id": "export_<12-hex>",
            "export_kind": "scope-snapshot",
            "manifest_path": "string",
            "payload_path": "string",
            "freshness_state": "fresh|stale|unknown",
        },
        stable_ids=(StableIdKind.SCAN, StableIdKind.EXPORT),
        failure_modes=(ErrorCode.INVALID_INPUT, ErrorCode.NOT_FOUND, ErrorCode.INTERNAL),
        recommended_next_tools=("export_evidence_bundle",),
    ),
    ToolContract(
        name="export_evidence_bundle",
        domain="export",
        input_schema={"target_repo": "string", "evidence_pack_id": "evidence_pack_<12-hex>"},
        output_schema={
            "target_repo": "string",
            "runtime_root": "string",
            "evidence_pack_id": "evidence_pack_<12-hex>",
            "scan_id": "scan_<12-hex>",
            "export_id": "export_<12-hex>",
            "export_kind": "evidence-bundle",
            "manifest_path": "string",
            "payload_path": "string",
            "freshness_state": "fresh|stale|unknown",
        },
        stable_ids=(StableIdKind.EVIDENCE_PACK, StableIdKind.EXPORT),
        failure_modes=(ErrorCode.INVALID_INPUT, ErrorCode.NOT_FOUND, ErrorCode.INTERNAL),
        recommended_next_tools=(),
    ),
)
