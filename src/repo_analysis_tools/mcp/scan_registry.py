from __future__ import annotations

import re


_SCAN_ID_PATTERN = re.compile(r"^scan_[0-9a-f]{12}$")
_SCAN_REPO_ROOTS: dict[str, str] = {}


def _validated_scan_id(scan_id: str) -> str:
    if not _SCAN_ID_PATTERN.fullmatch(scan_id):
        raise ValueError(f"invalid scan_id: {scan_id}")
    return scan_id


def remember_scan(scan_id: str, repo_root: str) -> None:
    _SCAN_REPO_ROOTS[_validated_scan_id(scan_id)] = repo_root


def repo_root_for_scan(scan_id: str) -> str:
    validated_scan_id = _validated_scan_id(scan_id)
    try:
        return _SCAN_REPO_ROOTS[validated_scan_id]
    except KeyError as exc:
        raise FileNotFoundError(f"scan {validated_scan_id} is not known to this MCP session") from exc
