from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from repo_analysis_tools.core.paths import domain_storage_root


class JsonAssetStore:
    def __init__(self, target_repo: Path | str, domain_name: str) -> None:
        self.root = domain_storage_root(target_repo, domain_name)
        self.root.mkdir(parents=True, exist_ok=True)

    def write_json(self, relative_path: str, payload: dict[str, Any]) -> Path:
        path = self.root / relative_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
        return path

    def read_json(self, relative_path: str) -> dict[str, Any]:
        path = self.root / relative_path
        return json.loads(path.read_text(encoding="utf-8"))
