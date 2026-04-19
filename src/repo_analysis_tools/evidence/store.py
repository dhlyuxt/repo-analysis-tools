from __future__ import annotations

from pathlib import Path
import re

from repo_analysis_tools.evidence.models import EvidencePack
from repo_analysis_tools.storage.json_assets import JsonAssetStore


_EVIDENCE_PACK_ID_PATTERN = re.compile(r"^evidence_pack_[0-9a-f]{12}$")


def _validated_evidence_pack_id(evidence_pack_id: str) -> str:
    if not _EVIDENCE_PACK_ID_PATTERN.fullmatch(evidence_pack_id):
        raise ValueError(f"invalid evidence_pack_id: {evidence_pack_id}")
    return evidence_pack_id


class EvidenceStore:
    def __init__(self, target_repo: Path | str) -> None:
        self.assets = JsonAssetStore(target_repo, "evidence")

    @classmethod
    def for_repo(cls, target_repo: Path | str) -> "EvidenceStore":
        return cls(target_repo)

    def save(self, evidence_pack: EvidencePack) -> None:
        evidence_pack_id = _validated_evidence_pack_id(evidence_pack.evidence_pack_id)
        self.assets.write_json(f"packs/{evidence_pack_id}.json", evidence_pack.to_dict())
        self.assets.write_json("latest.json", {"evidence_pack_id": evidence_pack_id})

    def load_latest(self) -> EvidencePack:
        try:
            payload = self.assets.read_json("latest.json")
        except FileNotFoundError as exc:
            raise FileNotFoundError("no evidence packs were found") from exc
        return self.load(str(payload["evidence_pack_id"]))

    def load(self, evidence_pack_id: str | None = None) -> EvidencePack:
        if evidence_pack_id is None:
            return self.load_latest()
        resolved_evidence_pack_id = _validated_evidence_pack_id(evidence_pack_id)
        try:
            payload = self.assets.read_json(f"packs/{resolved_evidence_pack_id}.json")
        except FileNotFoundError as exc:
            raise FileNotFoundError(f"evidence pack {resolved_evidence_pack_id} was not found") from exc
        return EvidencePack.from_dict(payload)
