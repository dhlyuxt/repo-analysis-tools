from __future__ import annotations

from pathlib import Path

from repo_analysis_tools.scan.models import ScanSnapshot
from repo_analysis_tools.storage.json_assets import JsonAssetStore


class ScanStore:
    def __init__(self, target_repo: Path | str) -> None:
        self.assets = JsonAssetStore(target_repo, "scan")

    @classmethod
    def for_repo(cls, target_repo: Path | str) -> "ScanStore":
        return cls(target_repo)

    def save(self, snapshot: ScanSnapshot) -> None:
        self.assets.write_json(f"snapshots/{snapshot.scan_id}.json", snapshot.to_dict())
        self.assets.write_json("latest.json", {"scan_id": snapshot.scan_id})

    def load_latest(self) -> ScanSnapshot:
        return self.load()

    def load(self, scan_id: str | None = None) -> ScanSnapshot:
        resolved_scan_id = scan_id or str(self.assets.read_json("latest.json")["scan_id"])
        payload = self.assets.read_json(f"snapshots/{resolved_scan_id}.json")
        return ScanSnapshot.from_dict(payload)
