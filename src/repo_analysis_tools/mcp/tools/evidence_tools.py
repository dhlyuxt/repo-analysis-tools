from pathlib import Path

from repo_analysis_tools.core.errors import ErrorCode, error_response, ok_response
from repo_analysis_tools.core.paths import runtime_root
from repo_analysis_tools.evidence.service import EvidenceService
from repo_analysis_tools.mcp.app import mcp


def _evidence_base_payload(target_repo: str, evidence_pack_id: str) -> dict[str, object]:
    return {
        "target_repo": target_repo,
        "runtime_root": runtime_root(Path(target_repo)).as_posix(),
        "evidence_pack_id": evidence_pack_id,
    }


@mcp.tool()
def build_evidence_pack(target_repo: str, slice_id: str) -> dict[str, object]:
    try:
        evidence_pack = EvidenceService().build(target_repo, slice_id)
    except ValueError as exc:
        return error_response(ErrorCode.INVALID_INPUT, str(exc))
    except FileNotFoundError as exc:
        return error_response(ErrorCode.NOT_FOUND, str(exc))
    return ok_response(
        data={
            **_evidence_base_payload(target_repo, evidence_pack.evidence_pack_id),
            "slice_id": evidence_pack.slice_id,
            "citation_count": evidence_pack.citation_count,
            "summary": evidence_pack.summary,
        },
        messages=["evidence pack built"],
        recommended_next_tools=["read_evidence_pack", "open_span"],
    )


@mcp.tool()
def read_evidence_pack(target_repo: str, evidence_pack_id: str) -> dict[str, object]:
    try:
        evidence_pack = EvidenceService().read(target_repo, evidence_pack_id)
    except ValueError as exc:
        return error_response(ErrorCode.INVALID_INPUT, str(exc))
    except FileNotFoundError as exc:
        return error_response(ErrorCode.NOT_FOUND, str(exc))
    return ok_response(
        data={
            **_evidence_base_payload(target_repo, evidence_pack.evidence_pack_id),
            "summary": evidence_pack.summary,
            "citations": [citation.to_dict() for citation in evidence_pack.citations],
        },
        messages=["evidence pack loaded"],
        recommended_next_tools=["open_span"],
    )


@mcp.tool()
def open_span(target_repo: str, evidence_pack_id: str, path: str, line_start: int, line_end: int) -> dict[str, object]:
    try:
        result = EvidenceService().open_span(target_repo, evidence_pack_id, path, line_start, line_end)
    except ValueError as exc:
        return error_response(ErrorCode.INVALID_INPUT, str(exc))
    except FileNotFoundError as exc:
        return error_response(ErrorCode.NOT_FOUND, str(exc))
    return ok_response(
        data={
            **_evidence_base_payload(target_repo, result.evidence_pack_id),
            "path": result.path,
            "line_start": result.line_start,
            "line_end": result.line_end,
            "lines": result.lines,
        },
        messages=["evidence span opened"],
        recommended_next_tools=["read_evidence_pack"],
    )
