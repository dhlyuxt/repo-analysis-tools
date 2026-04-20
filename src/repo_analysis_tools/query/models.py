from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class PriorityFileRow:
    path: str
    priority_score: int


@dataclass(frozen=True)
class FileInfoRow:
    path: str
    role: str
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


@dataclass(frozen=True)
class SymbolRow:
    symbol_id: str
    name: str
    kind: str
    path: str
    line_start: int
    line_end: int
    is_definition: bool
    storage: str


@dataclass(frozen=True)
class FileSymbolsRow:
    path: str
    symbols: tuple[SymbolRow, ...]


@dataclass(frozen=True)
class SymbolMatchResult:
    match_count: int
    matches: tuple[SymbolRow, ...]


@dataclass(frozen=True)
class SymbolContextRow:
    symbol_id: str
    name: str
    kind: str
    path: str
    definition_line_start: int
    definition_line_end: int
    context_line_start: int
    context_line_end: int
    lines: tuple[str, ...]
