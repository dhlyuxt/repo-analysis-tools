from __future__ import annotations

from pathlib import Path
import re

from repo_analysis_tools.scan.models import ScanSnapshot
from repo_analysis_tools.storage.json_assets import JsonAssetStore


_SCAN_ID_PATTERN = re.compile(r"^scan_[0-9a-f]{12}$")


def _validated_scan_id(scan_id: str) -> str:
    if not _SCAN_ID_PATTERN.fullmatch(scan_id):
        raise ValueError(f"invalid scan_id: {scan_id}")
    return scan_id


class ScanStore:
    def __init__(self, target_repo: Path | str) -> None:
        self.assets = JsonAssetStore(target_repo, "scan")

    @classmethod
    def for_repo(cls, target_repo: Path | str) -> "ScanStore":
        return cls(target_repo)

    def save(self, snapshot: ScanSnapshot) -> None:
        scan_id = _validated_scan_id(snapshot.scan_id)
        self.assets.write_json(f"snapshots/{scan_id}.json", snapshot.to_dict())
        self.assets.write_json("latest.json", {"scan_id": snapshot.scan_id})

    def load_latest(self) -> ScanSnapshot:
        return self.load()

    def exists(self, scan_id: str) -> bool:
        validated_scan_id = _validated_scan_id(scan_id)
        return (self.assets.root / f"snapshots/{validated_scan_id}.json").is_file()

    def load(self, scan_id: str | None = None) -> ScanSnapshot:
        if scan_id is None:
            resolved_scan_id = _validated_scan_id(str(self.assets.read_json("latest.json")["scan_id"]))
        else:
            resolved_scan_id = _validated_scan_id(scan_id)
        payload = self.assets.read_json(f"snapshots/{resolved_scan_id}.json")
        return ScanSnapshot.from_dict(payload)
