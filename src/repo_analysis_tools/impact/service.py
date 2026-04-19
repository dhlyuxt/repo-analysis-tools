from __future__ import annotations

from pathlib import Path

from repo_analysis_tools.anchors.models import AnchorRecord
from repo_analysis_tools.anchors.service import AnchorService
from repo_analysis_tools.core.ids import StableIdKind, make_stable_id
from repo_analysis_tools.core.paths import normalize_repo_relative_path
from repo_analysis_tools.impact.models import ImpactRecord, ImpactSummary, ImpactTarget, RiskFinding
from repo_analysis_tools.impact.propagation import reverse_callers_for_anchor, reverse_callers_for_paths
from repo_analysis_tools.impact.store import ImpactStore


class ImpactService:
    def __init__(self, anchor_service: AnchorService | None = None) -> None:
        self.anchor_service = anchor_service or AnchorService()

    def from_paths(
        self,
        target_repo: Path | str,
        changed_paths: list[str],
        scan_id: str | None = None,
    ) -> ImpactRecord:
        repo = Path(target_repo).expanduser().resolve()
        normalized_paths = self._normalized_paths(repo, changed_paths)
        if not normalized_paths:
            raise ValueError("changed_paths must not be empty")

        snapshot = self.anchor_service.load_snapshot(repo, scan_id=scan_id)
        propagation = reverse_callers_for_paths(snapshot, normalized_paths)
        record = ImpactRecord(
            impact_id=make_stable_id(StableIdKind.IMPACT),
            scan_id=snapshot.scan_id,
            repo_root=repo.as_posix(),
            seed_kind="path",
            seed=ImpactTarget(path=normalized_paths[0], kind="path", reason="Path-seeded impact analysis"),
            confirmed_targets=[
                ImpactTarget(path=path, kind="path", reason="Changed path supplied as direct impact seed")
                for path in normalized_paths
            ],
            likely_propagation=propagation.targets,
            regression_focus=self._regression_focus(normalized_paths, propagation.targets),
            blind_spots=self._blind_spots(propagation.notes),
            risks=self._risks(normalized_paths, propagation.targets),
            notes=[f"Impact derived from {len(normalized_paths)} changed path(s).", *propagation.notes],
        )
        ImpactStore.for_repo(repo).save(record)
        return record

    def from_anchor(
        self,
        target_repo: Path | str,
        anchor_name: str,
        scan_id: str | None = None,
    ) -> ImpactRecord:
        repo = Path(target_repo).expanduser().resolve()
        snapshot = self.anchor_service.load_snapshot(repo, scan_id=scan_id)
        anchor = self._resolve_anchor(repo, anchor_name, snapshot.scan_id)
        propagation = reverse_callers_for_anchor(snapshot, anchor)
        record = ImpactRecord(
            impact_id=make_stable_id(StableIdKind.IMPACT),
            scan_id=snapshot.scan_id,
            repo_root=repo.as_posix(),
            seed_kind="anchor",
            seed=self._target_from_anchor(anchor, "Anchor supplied as direct impact seed"),
            confirmed_targets=[self._target_from_anchor(anchor, "Resolved anchor impact seed")],
            likely_propagation=propagation.targets,
            regression_focus=self._regression_focus([anchor.path], propagation.targets),
            blind_spots=self._blind_spots(propagation.notes),
            risks=self._risks([anchor.path], propagation.targets),
            notes=[f"Impact derived from anchor {anchor.name}.", *propagation.notes],
        )
        ImpactStore.for_repo(repo).save(record)
        return record

    def summarize(self, target_repo: Path | str, impact_id: str) -> ImpactSummary:
        repo = Path(target_repo).expanduser().resolve()
        record = ImpactStore.for_repo(repo).load(impact_id)
        return ImpactSummary(
            impact_id=record.impact_id,
            confirmed_impact=record.confirmed_targets,
            likely_propagation=record.likely_propagation,
            regression_focus=list(record.regression_focus),
            blind_spots=list(record.blind_spots),
            risks=list(record.risks),
        )

    def _resolve_anchor(self, target_repo: Path, anchor_name: str, scan_id: str) -> AnchorRecord:
        matches = self.anchor_service.find_anchor_matches(target_repo, anchor_name, scan_id=scan_id)
        if not matches:
            raise FileNotFoundError(f"anchor {anchor_name.strip()} was not found")
        return matches[0]

    def _normalized_paths(self, target_repo: Path, changed_paths: list[str]) -> list[str]:
        normalized: list[str] = []
        seen: set[str] = set()
        for candidate in changed_paths:
            path = normalize_repo_relative_path(target_repo, candidate)
            if path in seen:
                continue
            seen.add(path)
            normalized.append(path)
        return sorted(normalized)

    def _target_from_anchor(self, anchor: AnchorRecord, reason: str) -> ImpactTarget:
        return ImpactTarget(
            path=anchor.path,
            anchor_id=anchor.anchor_id,
            anchor_name=anchor.name,
            kind=anchor.kind,
            reason=reason,
        )

    def _regression_focus(
        self,
        confirmed_paths: list[str],
        propagation_targets: list[ImpactTarget],
    ) -> list[str]:
        focus: list[str] = [f"Re-verify changed file {path}." for path in sorted(set(confirmed_paths))]
        for target in propagation_targets:
            if target.anchor_name is None:
                focus.append(f"Inspect callers in {target.path}.")
                continue
            focus.append(f"Re-test caller {target.anchor_name} in {target.path}.")
        return focus

    def _blind_spots(self, propagation_notes: list[str]) -> list[str]:
        return [
            "Analysis is bounded by available anchor relations and cannot prove effects outside parsed anchors.",
            *propagation_notes,
        ]

    def _risks(
        self,
        confirmed_paths: list[str],
        propagation_targets: list[ImpactTarget],
    ) -> list[RiskFinding]:
        confirmed_list = ", ".join(sorted(set(confirmed_paths)))
        if propagation_targets:
            callers_list = ", ".join(
                sorted(
                    {
                        target.anchor_name or target.path
                        for target in propagation_targets
                    }
                )
            )
            detail = f"Changes in {confirmed_list} may break observed reverse callers: {callers_list}."
        else:
            detail = f"Changes in {confirmed_list} have no proven reverse callers in current anchor relations."
        return [
            RiskFinding(
                title="Reverse callers may regress",
                severity="medium",
                detail=detail,
            )
        ]
