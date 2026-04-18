from pathlib import Path
from typing import Any

from repo_analysis_tools.core.errors import ok_response
from repo_analysis_tools.core.ids import StableIdKind, make_stable_id
from repo_analysis_tools.core.paths import runtime_root
from repo_analysis_tools.mcp.contracts import CONTRACT_BY_NAME


ID_FIELDS = {
    StableIdKind.SCAN: "scan_id",
    StableIdKind.SLICE: "slice_id",
    StableIdKind.EVIDENCE_PACK: "evidence_pack_id",
    StableIdKind.REPORT: "report_id",
    StableIdKind.EXPORT: "export_id",
}


def stub_payload(tool_name: str, *, target_repo: str, **extra: Any) -> dict[str, Any]:
    contract = CONTRACT_BY_NAME[tool_name]
    declared_output_fields = set(contract.output_schema)
    unexpected_fields = sorted(set(extra) - declared_output_fields)
    if unexpected_fields:
        unexpected_list = ", ".join(unexpected_fields)
        raise ValueError(f"{tool_name} emitted undeclared output fields: {unexpected_list}")
    payload = {
        "target_repo": target_repo,
        "runtime_root": runtime_root(Path(target_repo)).as_posix(),
    }
    for field_name, value in extra.items():
        if field_name in declared_output_fields:
            payload[field_name] = value
    for kind in contract.stable_ids:
        field_name = ID_FIELDS[kind]
        payload.setdefault(field_name, make_stable_id(kind))
    return ok_response(
        data=payload,
        messages=[f"{tool_name} is an M1 contract stub."],
        recommended_next_tools=list(contract.recommended_next_tools),
    )
