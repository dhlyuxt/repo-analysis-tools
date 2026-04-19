from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class ImpactTarget:
    path: str
    anchor_id: str | None = None
    anchor_name: str | None = None
    kind: str | None = None
    reason: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "path": self.path,
            "anchor_id": self.anchor_id,
            "anchor_name": self.anchor_name,
            "kind": self.kind,
            "reason": self.reason,
        }

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "ImpactTarget":
        return cls(
            path=str(payload["path"]),
            anchor_id=payload.get("anchor_id"),
            anchor_name=payload.get("anchor_name"),
            kind=payload.get("kind"),
            reason=str(payload.get("reason", "")),
        )


@dataclass(frozen=True)
class RiskFinding:
    title: str
    severity: str
    detail: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "title": self.title,
            "severity": self.severity,
            "detail": self.detail,
        }

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "RiskFinding":
        return cls(
            title=str(payload["title"]),
            severity=str(payload["severity"]),
            detail=str(payload["detail"]),
        )


@dataclass(frozen=True)
class ImpactRecord:
    impact_id: str
    scan_id: str
    repo_root: str
    seed_kind: str
    seed: ImpactTarget
    confirmed_targets: list[ImpactTarget]
    likely_propagation: list[ImpactTarget]
    regression_focus: list[str]
    blind_spots: list[str]
    risks: list[RiskFinding]
    notes: list[str]

    def to_dict(self) -> dict[str, Any]:
        return {
            "impact_id": self.impact_id,
            "scan_id": self.scan_id,
            "repo_root": self.repo_root,
            "seed_kind": self.seed_kind,
            "seed": self.seed.to_dict(),
            "confirmed_targets": [target.to_dict() for target in self.confirmed_targets],
            "likely_propagation": [target.to_dict() for target in self.likely_propagation],
            "regression_focus": list(self.regression_focus),
            "blind_spots": list(self.blind_spots),
            "risks": [risk.to_dict() for risk in self.risks],
            "notes": list(self.notes),
        }

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "ImpactRecord":
        return cls(
            impact_id=str(payload["impact_id"]),
            scan_id=str(payload["scan_id"]),
            repo_root=str(payload["repo_root"]),
            seed_kind=str(payload["seed_kind"]),
            seed=ImpactTarget.from_dict(payload["seed"]),
            confirmed_targets=[
                ImpactTarget.from_dict(item) for item in payload.get("confirmed_targets", [])
            ],
            likely_propagation=[
                ImpactTarget.from_dict(item) for item in payload.get("likely_propagation", [])
            ],
            regression_focus=[str(item) for item in payload.get("regression_focus", [])],
            blind_spots=[str(item) for item in payload.get("blind_spots", [])],
            risks=[RiskFinding.from_dict(item) for item in payload.get("risks", [])],
            notes=[str(item) for item in payload.get("notes", [])],
        )


@dataclass(frozen=True)
class ImpactSummary:
    impact_id: str
    confirmed_impact: list[ImpactTarget]
    likely_propagation: list[ImpactTarget]
    regression_focus: list[str]
    blind_spots: list[str]
    risks: list[RiskFinding]

    def to_dict(self) -> dict[str, Any]:
        return {
            "impact_id": self.impact_id,
            "confirmed_impact": [target.to_dict() for target in self.confirmed_impact],
            "likely_propagation": [target.to_dict() for target in self.likely_propagation],
            "regression_focus": list(self.regression_focus),
            "blind_spots": list(self.blind_spots),
            "risks": [risk.to_dict() for risk in self.risks],
        }

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "ImpactSummary":
        return cls(
            impact_id=str(payload["impact_id"]),
            confirmed_impact=[
                ImpactTarget.from_dict(item) for item in payload.get("confirmed_impact", [])
            ],
            likely_propagation=[
                ImpactTarget.from_dict(item) for item in payload.get("likely_propagation", [])
            ],
            regression_focus=[str(item) for item in payload.get("regression_focus", [])],
            blind_spots=[str(item) for item in payload.get("blind_spots", [])],
            risks=[RiskFinding.from_dict(item) for item in payload.get("risks", [])],
        )
