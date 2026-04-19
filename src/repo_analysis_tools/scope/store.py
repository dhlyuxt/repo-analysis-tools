from __future__ import annotations

from pathlib import Path
import re

from repo_analysis_tools.scope.models import ScopeSnapshot
from repo_analysis_tools.storage.json_assets import JsonAssetStore


_SCAN_ID_PATTERN = re.compile(r"^scan_[0-9a-f]{12}$")


def _validated_scan_id(scan_id: str) -> str:
    if not _SCAN_ID_PATTERN.fullmatch(scan_id):
        raise ValueError(f"invalid scan_id: {scan_id}")
    return scan_id


class ScopeStore:
    def __init__(self, target_repo: Path | str) -> None:
        self.assets = JsonAssetStore(target_repo, "scope")

    @classmethod
    def for_repo(cls, target_repo: Path | str) -> "ScopeStore":
        return cls(target_repo)

    def save(self, snapshot: ScopeSnapshot) -> None:
        scan_id = _validated_scan_id(snapshot.scan_id)
        self.assets.write_json(f"snapshots/{scan_id}.json", snapshot.to_dict())
        self.assets.write_json("latest.json", {"scan_id": scan_id})

    def load_latest(self) -> ScopeSnapshot:
        return self.load()

    def load(self, scan_id: str | None = None) -> ScopeSnapshot:
        if scan_id is None:
            resolved_scan_id = _validated_scan_id(str(self.assets.read_json("latest.json")["scan_id"]))
        else:
            resolved_scan_id = _validated_scan_id(scan_id)
        payload = self.assets.read_json(f"snapshots/{resolved_scan_id}.json")
        return ScopeSnapshot.from_dict(payload)
