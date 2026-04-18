from dataclasses import dataclass


@dataclass(frozen=True)
class StorageBoundary:
    domain: str
    directory_name: str
    owner_description: str


STORAGE_BOUNDARIES = {
    "scan": StorageBoundary("scan", "scan", "scan metadata and scan handles"),
    "scope": StorageBoundary("scope", "scope", "scope snapshots derived from scans"),
    "anchors": StorageBoundary("anchors", "anchors", "anchor extraction outputs"),
    "slice": StorageBoundary("slice", "slice", "slice manifests and expansions"),
    "evidence": StorageBoundary("evidence", "evidence", "evidence packs and citations"),
    "impact": StorageBoundary("impact", "impact", "impact analysis artifacts"),
    "report": StorageBoundary("report", "report", "report payloads before export"),
    "export": StorageBoundary("export", "export", "exported analysis bundles"),
}
