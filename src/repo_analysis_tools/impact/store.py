from __future__ import annotations

from pathlib import Path
import re

from repo_analysis_tools.impact.models import ImpactRecord
from repo_analysis_tools.storage.json_assets import JsonAssetStore


_IMPACT_ID_PATTERN = re.compile(r"^impact_[0-9a-f]{12}$")


def _validated_impact_id(impact_id: str) -> str:
    if not _IMPACT_ID_PATTERN.fullmatch(impact_id):
        raise ValueError(f"invalid impact_id: {impact_id}")
    return impact_id


class ImpactStore:
    def __init__(self, target_repo: Path | str) -> None:
        self.assets = JsonAssetStore(target_repo, "impact")

    @classmethod
    def for_repo(cls, target_repo: Path | str) -> "ImpactStore":
        return cls(target_repo)

    def save(self, record: ImpactRecord) -> None:
        impact_id = _validated_impact_id(record.impact_id)
        self.assets.write_json(f"results/{impact_id}.json", record.to_dict())
        self.assets.write_json("latest.json", {"impact_id": impact_id})

    def load_latest(self) -> ImpactRecord:
        try:
            payload = self.assets.read_json("latest.json")
        except FileNotFoundError as exc:
            raise FileNotFoundError("no impact results were found") from exc
        return self.load(str(payload["impact_id"]))

    def load(self, impact_id: str | None = None) -> ImpactRecord:
        if impact_id is None:
            return self.load_latest()
        resolved_impact_id = _validated_impact_id(impact_id)
        try:
            payload = self.assets.read_json(f"results/{resolved_impact_id}.json")
        except FileNotFoundError as exc:
            raise FileNotFoundError(f"impact {resolved_impact_id} was not found") from exc
        return ImpactRecord.from_dict(payload)
