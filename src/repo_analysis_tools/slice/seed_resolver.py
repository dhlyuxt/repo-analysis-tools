from __future__ import annotations

from difflib import get_close_matches
from pathlib import Path

from repo_analysis_tools.anchors.store import AnchorStore
from repo_analysis_tools.slice.models import SymbolResolution


class SeedResolver:
    def resolve_symbol(self, target_repo: Path | str, scan_id: str, symbol_name: str) -> SymbolResolution:
        normalized_name = symbol_name.strip()
        if not normalized_name:
            raise ValueError("symbol_name must not be empty")

        snapshot = AnchorStore.for_repo(target_repo).load(scan_id=scan_id)
        exact_matches = sorted(
            [anchor for anchor in snapshot.anchors if anchor.name == normalized_name],
            key=lambda anchor: (anchor.path, anchor.start_line, anchor.end_line, anchor.anchor_id),
        )
        if exact_matches:
            return SymbolResolution(exact_matches=exact_matches, close_matches=[])

        known_symbols = sorted({anchor.name for anchor in snapshot.anchors})
        return SymbolResolution(
            exact_matches=[],
            close_matches=get_close_matches(normalized_name, known_symbols, n=3, cutoff=0.6),
        )
