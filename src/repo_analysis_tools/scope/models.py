from __future__ import annotations

from dataclasses import dataclass
from typing import Any


ROLE_WEIGHT = {
    "primary": 40,
    "support": 20,
    "external": 5,
    "generated": 0,
}


def compute_priority_score(
    *,
    role: str,
    has_main_definition: bool,
    root_function_count: int,
    function_count: int,
    incoming_call_count: int,
    outgoing_call_count: int,
) -> int:
    score = ROLE_WEIGHT[role]
    if has_main_definition:
        score += 50
    score += min(root_function_count * 15, 30)
    score += min(function_count * 2, 20)
    score += min(incoming_call_count, 20)
    score += min(outgoing_call_count, 20)
    return score


@dataclass(frozen=True)
class ScopedFile:
    path: str
    role: str
    node_id: str
    priority_score: int
    line_count: int
    symbol_count: int
    function_count: int
    type_count: int
    macro_count: int
    include_count: int
    incoming_call_count: int
    outgoing_call_count: int
    root_function_count: int
    has_main_definition: bool

    def to_dict(self) -> dict[str, Any]:
        return {
            "path": self.path,
            "role": self.role,
            "node_id": self.node_id,
            "priority_score": self.priority_score,
            "line_count": self.line_count,
            "symbol_count": self.symbol_count,
            "function_count": self.function_count,
            "type_count": self.type_count,
            "macro_count": self.macro_count,
            "include_count": self.include_count,
            "incoming_call_count": self.incoming_call_count,
            "outgoing_call_count": self.outgoing_call_count,
            "root_function_count": self.root_function_count,
            "has_main_definition": self.has_main_definition,
        }

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "ScopedFile":
        return cls(
            path=str(payload["path"]),
            role=str(payload["role"]),
            node_id=str(payload["node_id"]),
            priority_score=int(payload["priority_score"]),
            line_count=int(payload["line_count"]),
            symbol_count=int(payload["symbol_count"]),
            function_count=int(payload["function_count"]),
            type_count=int(payload["type_count"]),
            macro_count=int(payload["macro_count"]),
            include_count=int(payload["include_count"]),
            incoming_call_count=int(payload["incoming_call_count"]),
            outgoing_call_count=int(payload["outgoing_call_count"]),
            root_function_count=int(payload["root_function_count"]),
            has_main_definition=bool(payload["has_main_definition"]),
        )


@dataclass(frozen=True)
class ScopeNode:
    node_id: str
    label: str
    role: str
    file_count: int
    related_files: list[str]

    def to_dict(self) -> dict[str, Any]:
        return {
            "node_id": self.node_id,
            "label": self.label,
            "role": self.role,
            "file_count": self.file_count,
            "related_files": list(self.related_files),
        }

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "ScopeNode":
        return cls(
            node_id=str(payload["node_id"]),
            label=str(payload["label"]),
            role=str(payload["role"]),
            file_count=int(payload["file_count"]),
            related_files=[str(path) for path in payload.get("related_files", [])],
        )


@dataclass(frozen=True)
class ScopeSnapshot:
    scan_id: str
    repo_root: str
    scope_summary: str
    role_counts: dict[str, int]
    nodes: list[ScopeNode]
    files: list[ScopedFile]

    def to_dict(self) -> dict[str, Any]:
        return {
            "scan_id": self.scan_id,
            "repo_root": self.repo_root,
            "scope_summary": self.scope_summary,
            "role_counts": dict(self.role_counts),
            "nodes": [node.to_dict() for node in self.nodes],
            "files": [scoped_file.to_dict() for scoped_file in self.files],
        }

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "ScopeSnapshot":
        return cls(
            scan_id=str(payload["scan_id"]),
            repo_root=str(payload["repo_root"]),
            scope_summary=str(payload["scope_summary"]),
            role_counts={
                str(role): int(count)
                for role, count in payload.get("role_counts", {}).items()
            },
            nodes=[ScopeNode.from_dict(item) for item in payload.get("nodes", [])],
            files=[ScopedFile.from_dict(item) for item in payload.get("files", [])],
        )
