from pathlib import Path

from repo_analysis_tools.core.errors import ErrorCode, error_response, ok_response
from repo_analysis_tools.core.paths import runtime_root
from repo_analysis_tools.impact.service import ImpactService
from repo_analysis_tools.impact.store import ImpactStore
from repo_analysis_tools.mcp.app import mcp


def _impact_base_payload(target_repo: str, scan_id: str, impact_id: str) -> dict[str, object]:
    return {
        "target_repo": target_repo,
        "runtime_root": runtime_root(Path(target_repo)).as_posix(),
        "scan_id": scan_id,
        "impact_id": impact_id,
    }


def _impact_record_summary(notes: list[str], risks: list[dict[str, object]] | None = None) -> str:
    if notes:
        return notes[0]
    if risks:
        first_risk = risks[0].get("detail")
        if isinstance(first_risk, str) and first_risk:
            return first_risk
    return "Impact summary unavailable."


@mcp.tool()
def impact_from_paths(target_repo: str, paths: list[str], scan_id: str | None = None) -> dict[str, object]:
    try:
        record = ImpactService().from_paths(target_repo, paths, scan_id)
    except ValueError as exc:
        return error_response(ErrorCode.INVALID_INPUT, str(exc))
    except FileNotFoundError as exc:
        return error_response(ErrorCode.NOT_FOUND, str(exc))
    return ok_response(
        data={
            **_impact_base_payload(target_repo, record.scan_id, record.impact_id),
            "seed_kind": record.seed_kind,
            "changed_paths": list(record.changed_paths),
            "direct_impacts": [target.to_dict() for target in record.confirmed_targets],
            "likely_propagation": [target.to_dict() for target in record.likely_propagation],
            "uncertainty_notes": list(record.blind_spots),
            "recommended_regression_focus": list(record.regression_focus),
            "summary": _impact_record_summary(record.notes),
        },
        messages=["impact analysis loaded from changed paths"],
        recommended_next_tools=["summarize_impact", "plan_slice"],
    )


@mcp.tool()
def impact_from_anchor(target_repo: str, anchor_name: str, scan_id: str | None = None) -> dict[str, object]:
    try:
        record = ImpactService().from_anchor(target_repo, anchor_name, scan_id)
    except ValueError as exc:
        return error_response(ErrorCode.INVALID_INPUT, str(exc))
    except FileNotFoundError as exc:
        return error_response(ErrorCode.NOT_FOUND, str(exc))
    return ok_response(
        data={
            **_impact_base_payload(target_repo, record.scan_id, record.impact_id),
            "seed_kind": record.seed_kind,
            "anchor_name": record.seed.anchor_name or anchor_name,
            "direct_impacts": [target.to_dict() for target in record.confirmed_targets],
            "likely_propagation": [target.to_dict() for target in record.likely_propagation],
            "uncertainty_notes": list(record.blind_spots),
            "recommended_regression_focus": list(record.regression_focus),
            "summary": _impact_record_summary(record.notes),
        },
        messages=["impact analysis loaded from anchor"],
        recommended_next_tools=["summarize_impact", "plan_slice"],
    )


@mcp.tool()
def summarize_impact(target_repo: str, impact_id: str) -> dict[str, object]:
    service = ImpactService()
    try:
        summary = service.summarize(target_repo, impact_id)
        record = ImpactStore.for_repo(target_repo).load(impact_id)
    except ValueError as exc:
        return error_response(ErrorCode.INVALID_INPUT, str(exc))
    except FileNotFoundError as exc:
        return error_response(ErrorCode.NOT_FOUND, str(exc))
    return ok_response(
        data={
            **_impact_base_payload(target_repo, record.scan_id, summary.impact_id),
            "confirmed_impact": [target.to_dict() for target in summary.confirmed_impact],
            "likely_propagation": [target.to_dict() for target in summary.likely_propagation],
            "regression_focus": list(summary.regression_focus),
            "blind_spots": list(summary.blind_spots),
            "risks": [risk.to_dict() for risk in summary.risks],
            "summary": _impact_record_summary(
                record.notes,
                [risk.to_dict() for risk in summary.risks],
            ),
        },
        messages=["impact summary loaded"],
        recommended_next_tools=["plan_slice", "build_evidence_pack"],
    )
