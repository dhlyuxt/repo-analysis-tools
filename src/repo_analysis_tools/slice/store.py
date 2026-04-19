from __future__ import annotations

from pathlib import Path
import re

from repo_analysis_tools.slice.models import SliceManifest
from repo_analysis_tools.storage.json_assets import JsonAssetStore


_SLICE_ID_PATTERN = re.compile(r"^slice_[0-9a-f]{12}$")


def _validated_slice_id(slice_id: str) -> str:
    if not _SLICE_ID_PATTERN.fullmatch(slice_id):
        raise ValueError(f"invalid slice_id: {slice_id}")
    return slice_id


class SliceStore:
    def __init__(self, target_repo: Path | str) -> None:
        self.assets = JsonAssetStore(target_repo, "slice")

    @classmethod
    def for_repo(cls, target_repo: Path | str) -> "SliceStore":
        return cls(target_repo)

    def save(self, manifest: SliceManifest) -> None:
        slice_id = _validated_slice_id(manifest.slice_id)
        self.assets.write_json(f"manifests/{slice_id}.json", manifest.to_dict())
        self.assets.write_json("latest.json", {"slice_id": slice_id})

    def load_latest(self) -> SliceManifest:
        try:
            payload = self.assets.read_json("latest.json")
        except FileNotFoundError as exc:
            raise FileNotFoundError("no slice manifests were found") from exc
        return self.load(str(payload["slice_id"]))

    def load(self, slice_id: str | None = None) -> SliceManifest:
        if slice_id is None:
            return self.load_latest()
        resolved_slice_id = _validated_slice_id(slice_id)
        try:
            payload = self.assets.read_json(f"manifests/{resolved_slice_id}.json")
        except FileNotFoundError as exc:
            raise FileNotFoundError(f"slice {resolved_slice_id} was not found") from exc
        return SliceManifest.from_dict(payload)
