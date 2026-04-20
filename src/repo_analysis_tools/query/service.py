from __future__ import annotations

from pathlib import Path, PurePosixPath
import re

from repo_analysis_tools.anchors.models import AnchorRecord
from repo_analysis_tools.anchors.store import AnchorStore
from repo_analysis_tools.query.models import (
    FileInfoRow,
    FileSymbolsRow,
    PriorityFileRow,
    SymbolContextRow,
    SymbolMatchResult,
    SymbolRow,
)
from repo_analysis_tools.scope.models import ScopedFile
from repo_analysis_tools.scope.store import ScopeStore


_STORAGE_RE = re.compile(r"\b(static|extern)\b")


class QueryService:
    def list_priority_files(self, target_repo: Path | str, scan_id: str) -> tuple[PriorityFileRow, ...]:
        scope_snapshot = self._load_scope_snapshot(target_repo, scan_id)
        rows = [
            PriorityFileRow(path=scoped_file.path, priority_score=scoped_file.priority_score)
            for scoped_file in sorted(
                scope_snapshot.files,
                key=lambda item: (-item.priority_score, item.path),
            )
        ]
        return tuple(rows)

    def get_file_info(self, target_repo: Path | str, scan_id: str, path: str) -> FileInfoRow:
        scope_snapshot = self._load_scope_snapshot(target_repo, scan_id)
        scoped_file = self._find_scoped_file(scope_snapshot.files, path)
        return self._file_info_from_scoped_file(scoped_file)

    def list_file_symbols(
        self,
        target_repo: Path | str,
        scan_id: str,
        paths: list[str] | tuple[str, ...],
    ) -> tuple[FileSymbolsRow, ...]:
        anchor_snapshot = self._load_anchor_snapshot(target_repo, scan_id)
        normalized_paths = sorted({self._normalize_repo_path(path) for path in paths})
        rows = []
        for path in normalized_paths:
            symbols = [
                self._symbol_row_from_anchor(anchor, target_repo)
                for anchor in self._anchors_for_path(anchor_snapshot.anchors, path)
            ]
            rows.append(FileSymbolsRow(path=path, symbols=tuple(symbols)))
        return tuple(rows)

    def resolve_symbols(
        self,
        target_repo: Path | str,
        scan_id: str,
        symbol_name: str,
    ) -> SymbolMatchResult:
        normalized_name = self._validated_symbol_name(symbol_name)
        anchor_snapshot = self._load_anchor_snapshot(target_repo, scan_id)
        anchors = [anchor for anchor in anchor_snapshot.anchors if anchor.name == normalized_name]
        rows = tuple(
            self._symbol_row_from_anchor(anchor, target_repo)
            for anchor in sorted(anchors, key=self._symbol_sort_key)
        )
        return SymbolMatchResult(match_count=len(rows), matches=rows)

    def open_symbol_context(
        self,
        target_repo: Path | str,
        scan_id: str,
        symbol_id: str,
        context_lines: int,
    ) -> SymbolContextRow:
        if context_lines < 0:
            raise ValueError("context_lines must not be negative")
        anchor_snapshot = self._load_anchor_snapshot(target_repo, scan_id)
        anchor = self._find_anchor(anchor_snapshot.anchors, symbol_id)
        anchor = self._preferred_definition_anchor(anchor_snapshot.anchors, anchor)
        repo = Path(target_repo).expanduser().resolve()
        source_lines = (repo / anchor.path).read_text(encoding="utf-8", errors="ignore").splitlines()
        definition_end = self._definition_end_line(anchor, source_lines)
        definition_start = anchor.start_line
        context_start = max(1, definition_start - context_lines)
        context_end = min(len(source_lines), definition_end + context_lines)
        return SymbolContextRow(
            symbol_id=anchor.anchor_id,
            name=anchor.name,
            kind=self._normalized_symbol_kind(anchor),
            path=anchor.path,
            definition_line_start=definition_start,
            definition_line_end=definition_end,
            context_line_start=context_start,
            context_line_end=context_end,
            lines=tuple(source_lines[context_start - 1 : context_end]),
        )

    def _load_scope_snapshot(self, target_repo: Path | str, scan_id: str):
        return ScopeStore.for_repo(target_repo).load(scan_id)

    def _load_anchor_snapshot(self, target_repo: Path | str, scan_id: str):
        return AnchorStore.for_repo(target_repo).load(scan_id)

    def _find_scoped_file(self, scoped_files: list[ScopedFile], path: str) -> ScopedFile:
        normalized_path = self._normalize_repo_path(path)
        for scoped_file in scoped_files:
            if scoped_file.path == normalized_path:
                return scoped_file
        raise FileNotFoundError(f"file {normalized_path} was not found")

    def _file_info_from_scoped_file(self, scoped_file: ScopedFile) -> FileInfoRow:
        return FileInfoRow(
            path=scoped_file.path,
            role=scoped_file.role,
            priority_score=scoped_file.priority_score,
            line_count=scoped_file.line_count,
            symbol_count=scoped_file.symbol_count,
            function_count=scoped_file.function_count,
            type_count=scoped_file.type_count,
            macro_count=scoped_file.macro_count,
            include_count=scoped_file.include_count,
            incoming_call_count=scoped_file.incoming_call_count,
            outgoing_call_count=scoped_file.outgoing_call_count,
            root_function_count=scoped_file.root_function_count,
            has_main_definition=scoped_file.has_main_definition,
        )

    def _anchors_for_path(self, anchors: list[AnchorRecord], path: str) -> list[AnchorRecord]:
        return sorted(
            [anchor for anchor in anchors if anchor.path == path],
            key=self._symbol_sort_key,
        )

    def _symbol_row_from_anchor(self, anchor: AnchorRecord, target_repo: Path | str) -> SymbolRow:
        source_lines = self._source_lines_for_anchor(target_repo, anchor)
        storage = self._infer_storage(anchor, source_lines)
        return SymbolRow(
            symbol_id=anchor.anchor_id,
            name=anchor.name,
            kind=self._normalized_symbol_kind(anchor),
            path=anchor.path,
            line_start=anchor.start_line,
            line_end=anchor.end_line,
            is_definition=anchor.kind != "function_declaration",
            storage=storage,
        )

    def _source_lines_for_anchor(self, target_repo: Path | str, anchor: AnchorRecord) -> list[str]:
        repo = Path(target_repo).expanduser().resolve()
        return (repo / anchor.path).read_text(encoding="utf-8", errors="ignore").splitlines()

    def _infer_storage(self, anchor: AnchorRecord, source_lines: list[str]) -> str:
        if anchor.start_line <= 0 or anchor.start_line > len(source_lines):
            return "unknown"
        line = source_lines[anchor.start_line - 1]
        match = _STORAGE_RE.search(line)
        if match is not None:
            return match.group(1)
        return "global"

    def _symbol_sort_key(self, anchor: AnchorRecord) -> tuple[int, str, int, int, str]:
        return (
            0 if anchor.kind != "function_declaration" else 1,
            anchor.path,
            anchor.start_line,
            anchor.end_line,
            anchor.kind,
        )

    def _find_anchor(self, anchors: list[AnchorRecord], symbol_id: str) -> AnchorRecord:
        for anchor in anchors:
            if anchor.anchor_id == symbol_id:
                return anchor
        raise FileNotFoundError(f"symbol {symbol_id} was not found")

    def _preferred_definition_anchor(self, anchors: list[AnchorRecord], anchor: AnchorRecord) -> AnchorRecord:
        if anchor.kind != "function_declaration":
            return anchor
        definitions = [
            candidate
            for candidate in anchors
            if candidate.kind == "function_definition" and candidate.name == anchor.name
        ]
        if len(definitions) == 1:
            return definitions[0]
        return anchor

    def _definition_end_line(self, anchor: AnchorRecord, source_lines: list[str]) -> int:
        if anchor.kind != "function_definition":
            return anchor.end_line
        if anchor.start_line <= 0 or anchor.start_line > len(source_lines):
            return anchor.end_line

        brace_depth = 0
        saw_open_brace = False
        state = "normal"
        escape = False
        for line_index in range(anchor.start_line - 1, len(source_lines)):
            line = source_lines[line_index]
            column = 0
            while column < len(line):
                character = line[column]
                next_character = line[column + 1] if column + 1 < len(line) else ""

                if state == "line_comment":
                    break
                if state == "block_comment":
                    if character == "*" and next_character == "/":
                        state = "normal"
                        column += 2
                        continue
                    column += 1
                    continue
                if state == "string":
                    if escape:
                        escape = False
                    elif character == "\\":
                        escape = True
                    elif character == '"':
                        state = "normal"
                    column += 1
                    continue
                if state == "char":
                    if escape:
                        escape = False
                    elif character == "\\":
                        escape = True
                    elif character == "'":
                        state = "normal"
                    column += 1
                    continue

                if character == "/" and next_character == "/":
                    state = "line_comment"
                    break
                if character == "/" and next_character == "*":
                    state = "block_comment"
                    column += 2
                    continue
                if character == '"':
                    state = "string"
                    escape = False
                    column += 1
                    continue
                if character == "'":
                    state = "char"
                    escape = False
                    column += 1
                    continue
                if character == "{":
                    brace_depth += 1
                    saw_open_brace = True
                elif character == "}" and saw_open_brace:
                    brace_depth -= 1
                    if brace_depth == 0:
                        return line_index + 1
                column += 1
            if state == "line_comment":
                state = "normal"
        return anchor.end_line

    def _normalized_symbol_kind(self, anchor: AnchorRecord) -> str:
        if anchor.kind in {"function_definition", "function_declaration"}:
            return "function"
        if anchor.kind == "type_definition":
            return "type"
        if anchor.kind == "macro_definition":
            return "macro"
        return "variable"

    def _normalize_repo_path(self, path: str) -> str:
        raw_path = PurePosixPath(path)
        if raw_path.is_absolute():
            raise ValueError("path must be repository-relative")
        if any(part == ".." for part in raw_path.parts):
            raise ValueError("path must be repository-relative")
        normalized = PurePosixPath(*[part for part in raw_path.parts if part != "."]).as_posix()
        if not normalized or normalized == ".":
            raise ValueError("path must not be empty")
        return normalized

    def _validated_symbol_name(self, symbol_name: str) -> str:
        normalized = symbol_name.strip()
        if not normalized:
            raise ValueError("symbol_name must not be empty")
        return normalized
