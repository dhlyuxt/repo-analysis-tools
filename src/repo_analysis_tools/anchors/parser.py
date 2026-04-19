from __future__ import annotations

from bisect import bisect_right
from dataclasses import dataclass
from functools import lru_cache
from pathlib import PurePosixPath
import re

from repo_analysis_tools.anchors.models import AnchorRecord, AnchorRelation
from repo_analysis_tools.core.ids import make_anchor_id, make_scope_node_id


_INCLUDE_RE = re.compile(r'^\s*#\s*include\s+[<"]([^>"]+)[>"]', re.MULTILINE)
_MACRO_RE = re.compile(r"^\s*#\s*define\s+([A-Za-z_]\w*)", re.MULTILINE)
_CALL_RE = re.compile(r"\b([A-Za-z_]\w*)\s*\(")
_TYPEDEF_ALIAS_RE = re.compile(r"\btypedef\b.*?\b([A-Za-z_]\w*)\s*$", re.DOTALL)
_NAMED_TYPE_RE = re.compile(r"\b(struct|union|enum)\s+([A-Za-z_]\w*)\s*$")
_FUNCTION_NAME_RE = re.compile(r"([A-Za-z_]\w*)\s*\(")
_DECLARATION_EXCLUDE_RE = re.compile(r"^\s*(return|if|for|while|switch|sizeof)\b")
_CONTROL_CALLS = {
    "if",
    "for",
    "while",
    "switch",
    "return",
    "sizeof",
}
_TREE_SITTER_FUNCTION_DEFINITION_QUERY = """
(function_definition
  declarator: (function_declarator declarator: (_) @function.name)
) @function.node
"""
_TREE_SITTER_FUNCTION_DECLARATION_QUERY = """
(declaration
  declarator: (function_declarator declarator: (_) @function.name)
) @function.node
"""
_TREE_SITTER_TYPE_DEFINITION_QUERY = """
(type_definition declarator: (_) @type.name) @type.node
"""
_TREE_SITTER_MACRO_QUERY = """
[
  (preproc_def name: (identifier) @macro.name)
  (preproc_function_def name: (identifier) @macro.name)
] @macro.node
"""
_TREE_SITTER_INCLUDE_QUERY = """
(preproc_include path: [(string_literal) (system_lib_string)] @include.path) @include.node
"""


@dataclass(frozen=True)
class ParsedAnchors:
    backend: str
    anchors: list[AnchorRecord]
    relations: list[AnchorRelation]


class CAnchorParser:
    SUPPORTED_SUFFIXES = {".c", ".h"}

    def parse_file(self, relative_path: str, source_text: str) -> ParsedAnchors:
        parser = _try_build_tree_sitter_parser()
        if parser is not None:
            try:
                return _extract_with_tree_sitter(parser, relative_path, source_text)
            except Exception:
                pass
        return _extract_with_regex(relative_path, source_text)


def _extract_with_tree_sitter(parser: object, relative_path: str, source_text: str) -> ParsedAnchors:
    source_bytes = source_text.encode("utf-8")
    tree = parser.parse(source_bytes)
    root = tree.root_node
    language = parser.language
    scope_node_id = make_scope_node_id(_scope_label(relative_path))

    anchors: list[AnchorRecord] = []
    relations: list[AnchorRelation] = []
    function_anchors: list[tuple[AnchorRecord, object]] = []

    include_targets = [
        (
            _clean_include_target(_node_text(path_node, source_bytes)),
            path_node.start_point.row + 1,
        )
        for path_node in _captured_nodes(language, root, _TREE_SITTER_INCLUDE_QUERY, "include.path")
        if _is_file_level(path_node)
    ]

    for macro_node in _captured_nodes(language, root, _TREE_SITTER_MACRO_QUERY, "macro.node"):
        if not _is_file_level(macro_node):
            continue
        name_node = macro_node.child_by_field_name("name")
        if name_node is None:
            continue
        name = _node_text(name_node, source_bytes)
        anchor = AnchorRecord(
            anchor_id=make_anchor_id(
                relative_path,
                "macro_definition",
                name,
                macro_node.start_point.row + 1,
                macro_node.end_point.row,
            ),
            scope_node_id=scope_node_id,
            kind="macro_definition",
            name=name,
            path=relative_path,
            start_line=macro_node.start_point.row + 1,
            end_line=max(macro_node.start_point.row + 1, macro_node.end_point.row),
        )
        anchors.append(anchor)
        relations.append(
            AnchorRelation(
                kind="defines",
                source_anchor_id=anchor.anchor_id,
                source_name=anchor.name,
                target_name=relative_path,
                target_path=relative_path,
                line=anchor.start_line,
            )
        )

    for function_node in _captured_nodes(language, root, _TREE_SITTER_FUNCTION_DEFINITION_QUERY, "function.node"):
        if not _is_file_level(function_node):
            continue
        anchor = _function_anchor_from_node(
            node=function_node,
            kind="function_definition",
            relative_path=relative_path,
            scope_node_id=scope_node_id,
            source_bytes=source_bytes,
        )
        if anchor is None:
            continue
        anchors.append(anchor)
        function_anchors.append((anchor, function_node))

    for declaration_node in _captured_nodes(language, root, _TREE_SITTER_FUNCTION_DECLARATION_QUERY, "function.node"):
        if not _is_file_level(declaration_node):
            continue
        anchor = _function_anchor_from_node(
            node=declaration_node,
            kind="function_declaration",
            relative_path=relative_path,
            scope_node_id=scope_node_id,
            source_bytes=source_bytes,
        )
        if anchor is None:
            continue
        anchors.append(anchor)

    for type_node in _captured_nodes(language, root, _TREE_SITTER_TYPE_DEFINITION_QUERY, "type.node"):
        if not _is_file_level(type_node):
            continue
        declarator = type_node.child_by_field_name("declarator")
        type_name = _declarator_identifier(declarator, source_bytes)
        if type_name is None:
            continue
        anchors.append(
            AnchorRecord(
                anchor_id=make_anchor_id(
                    relative_path,
                    "type_definition",
                    type_name,
                    type_node.start_point.row + 1,
                    max(type_node.start_point.row + 1, type_node.end_point.row),
                ),
                scope_node_id=scope_node_id,
                kind="type_definition",
                name=type_name,
                path=relative_path,
                start_line=type_node.start_point.row + 1,
                end_line=max(type_node.start_point.row + 1, type_node.end_point.row),
            )
        )

    for anchor, function_node in function_anchors:
        relations.extend(
            AnchorRelation(
                kind="includes",
                source_anchor_id=anchor.anchor_id,
                source_name=anchor.name,
                target_name=include_target,
                target_path=include_target,
                line=include_line,
            )
            for include_target, include_line in include_targets
        )
        relations.extend(
            _tree_sitter_direct_calls(
                anchor=anchor,
                function_node=function_node,
                source_bytes=source_bytes,
            )
        )

    anchors_by_name: dict[str, list[AnchorRecord]] = {}
    for anchor in anchors:
        anchors_by_name.setdefault(anchor.name, []).append(anchor)

    resolved_relations: list[AnchorRelation] = []
    for relation in relations:
        target_anchor = _resolve_target_anchor(anchors_by_name, relation.target_name)
        resolved_relations.append(
            AnchorRelation(
                kind=relation.kind,
                source_anchor_id=relation.source_anchor_id,
                source_name=relation.source_name,
                target_name=relation.target_name,
                target_anchor_id=target_anchor.anchor_id if target_anchor is not None else relation.target_anchor_id,
                target_path=target_anchor.path if target_anchor is not None else relation.target_path,
                line=relation.line,
            )
        )
    return ParsedAnchors(
        backend="tree-sitter-c",
        anchors=sorted(anchors, key=lambda item: (item.path, item.start_line, item.name, item.kind)),
        relations=sorted(
            resolved_relations,
            key=lambda item: (item.source_name, item.kind, item.target_name, item.line or 0),
        ),
    )


def _try_build_tree_sitter_parser() -> object | None:
    language = _try_build_tree_sitter_language()
    if language is None:
        return None
    try:
        from tree_sitter import Parser
    except ImportError:
        return None
    parser = Parser()
    parser.language = language
    return parser


@lru_cache(maxsize=1)
def _try_build_tree_sitter_language() -> object | None:
    try:
        from tree_sitter import Language
        import tree_sitter_c
    except ImportError:
        return None
    try:
        return Language(tree_sitter_c.language())
    except ValueError:
        return None
    return None


def _captured_nodes(language: object, root: object, query_source: str, capture_name: str) -> list[object]:
    captures = language.query(query_source).captures(root)
    return sorted(captures.get(capture_name, []), key=lambda node: (node.start_byte, node.end_byte))


def _function_anchor_from_node(
    *,
    node: object,
    kind: str,
    relative_path: str,
    scope_node_id: str,
    source_bytes: bytes,
) -> AnchorRecord | None:
    declarator = node.child_by_field_name("declarator")
    function_name = _declarator_identifier(declarator, source_bytes)
    if function_name is None:
        return None
    start_line = node.start_point.row + 1
    end_line = max(start_line, node.end_point.row)
    return AnchorRecord(
        anchor_id=make_anchor_id(relative_path, kind, function_name, start_line, end_line),
        scope_node_id=scope_node_id,
        kind=kind,
        name=function_name,
        path=relative_path,
        start_line=start_line,
        end_line=end_line,
    )


def _declarator_identifier(node: object | None, source_bytes: bytes) -> str | None:
    if node is None:
        return None
    if node.type in {"identifier", "type_identifier"}:
        return _node_text(node, source_bytes)
    for child in node.named_children:
        child_name = _declarator_identifier(child, source_bytes)
        if child_name is not None:
            return child_name
    return None


def _tree_sitter_direct_calls(
    *,
    anchor: AnchorRecord,
    function_node: object,
    source_bytes: bytes,
) -> list[AnchorRelation]:
    body = function_node.child_by_field_name("body")
    if body is None:
        return []
    relations: list[AnchorRelation] = []
    seen: set[tuple[str, int]] = set()
    for node in _iter_named_descendants(body):
        if node.type != "call_expression":
            continue
        callee = node.child_by_field_name("function")
        if callee is None or callee.type != "identifier":
            continue
        callee_name = _node_text(callee, source_bytes)
        if callee_name == anchor.name or callee_name in _CONTROL_CALLS:
            continue
        if callee_name.upper() == callee_name:
            continue
        line = node.start_point.row + 1
        relation_key = (callee_name, line)
        if relation_key in seen:
            continue
        seen.add(relation_key)
        relations.append(
            AnchorRelation(
                kind="direct_call",
                source_anchor_id=anchor.anchor_id,
                source_name=anchor.name,
                target_name=callee_name,
                line=line,
            )
        )
    return relations


def _iter_named_descendants(node: object) -> list[object]:
    descendants: list[object] = []
    stack = list(reversed(node.named_children))
    while stack:
        current = stack.pop()
        descendants.append(current)
        stack.extend(reversed(current.named_children))
    return descendants


def _node_text(node: object, source_bytes: bytes) -> str:
    return source_bytes[node.start_byte:node.end_byte].decode("utf-8", "ignore")


def _clean_include_target(raw: str) -> str:
    if raw.startswith('"') and raw.endswith('"'):
        return raw[1:-1]
    if raw.startswith("<") and raw.endswith(">"):
        return raw[1:-1]
    return raw


def _is_file_level(node: object) -> bool:
    current = node.parent
    while current is not None:
        if current.type in {
            "function_definition",
            "compound_statement",
            "declaration",
            "expression_statement",
            "parameter_list",
            "field_declaration_list",
            "initializer_list",
        }:
            return False
        current = current.parent
    return True


def _extract_with_regex(relative_path: str, source_text: str, *, backend: str = "regex-compat") -> ParsedAnchors:
    cleaned = _strip_comments_and_strings(source_text)
    line_starts = _line_starts(source_text)
    file_scope_node_id = make_scope_node_id(_scope_label(relative_path))

    anchors: list[AnchorRecord] = []
    relations: list[AnchorRelation] = []
    macro_anchors = _extract_macros(relative_path, source_text, file_scope_node_id)
    anchors.extend(macro_anchors)
    relations.extend(
        AnchorRelation(
            kind="defines",
            source_anchor_id=anchor.anchor_id,
            source_name=anchor.name,
            target_name=relative_path,
            target_path=relative_path,
            line=anchor.start_line,
        )
        for anchor in macro_anchors
    )
    top_level_items = _scan_top_level_items(relative_path, source_text, cleaned, file_scope_node_id, line_starts)
    anchors.extend(top_level_items.anchors)
    relations.extend(top_level_items.relations)

    anchors_by_name: dict[str, list[AnchorRecord]] = {}
    for anchor in anchors:
        anchors_by_name.setdefault(anchor.name, []).append(anchor)

    resolved_relations: list[AnchorRelation] = []
    for relation in relations:
        target_anchor = _resolve_target_anchor(anchors_by_name, relation.target_name)
        resolved_relations.append(
            AnchorRelation(
                kind=relation.kind,
                source_anchor_id=relation.source_anchor_id,
                source_name=relation.source_name,
                target_name=relation.target_name,
                target_anchor_id=target_anchor.anchor_id if target_anchor is not None else relation.target_anchor_id,
                target_path=target_anchor.path if target_anchor is not None else relation.target_path,
                line=relation.line,
            )
        )
    return ParsedAnchors(
        backend=backend,
        anchors=sorted(anchors, key=lambda item: (item.path, item.start_line, item.name, item.kind)),
        relations=sorted(
            resolved_relations,
            key=lambda item: (item.source_name, item.kind, item.target_name, item.line or 0),
        ),
    )


@dataclass(frozen=True)
class _TopLevelExtraction:
    anchors: list[AnchorRecord]
    relations: list[AnchorRelation]


def _scan_top_level_items(
    relative_path: str,
    source_text: str,
    cleaned_text: str,
    scope_node_id: str,
    line_starts: list[int],
) -> _TopLevelExtraction:
    anchors: list[AnchorRecord] = []
    relations: list[AnchorRelation] = []
    statement_start = 0
    index = 0
    length = len(cleaned_text)
    depth = 0
    while index < length:
        character = cleaned_text[index]
        if character == "{":
            if depth == 0:
                header = cleaned_text[statement_start:index]
                function_name = _extract_function_name(header)
                if function_name is not None:
                    body_end = _matching_brace(cleaned_text, index)
                    start_offset = statement_start + _first_meaningful_offset(header)
                    start_line = _line_number(line_starts, start_offset)
                    end_line = _line_number(line_starts, body_end)
                    anchor = AnchorRecord(
                        anchor_id=make_anchor_id(
                            relative_path,
                            "function_definition",
                            function_name,
                            start_line,
                            end_line,
                        ),
                        scope_node_id=scope_node_id,
                        kind="function_definition",
                        name=function_name,
                        path=relative_path,
                        start_line=start_line,
                        end_line=end_line,
                    )
                    anchors.append(anchor)
                    relations.extend(_build_include_relations(anchor, relative_path, source_text))
                    relations.extend(
                        _extract_direct_calls(
                            anchor=anchor,
                            function_name=function_name,
                            body_text=cleaned_text[index + 1:body_end],
                            body_start_offset=index + 1,
                            line_starts=line_starts,
                        )
                    )
                    index = body_end
                    statement_start = index + 1
                    continue
            depth += 1
        elif character == "}":
            depth = max(0, depth - 1)
            if depth == 0:
                statement_start = index + 1
        elif character == ";" and depth == 0:
            statement = cleaned_text[statement_start:index]
            start_offset = statement_start + _first_meaningful_offset(statement)
            start_line = _line_number(line_starts, start_offset)
            end_line = _line_number(line_starts, index)
            anchor = _parse_top_level_statement(relative_path, scope_node_id, statement, start_line, end_line)
            if anchor is not None:
                anchors.append(anchor)
            statement_start = index + 1
        index += 1
    return _TopLevelExtraction(anchors=anchors, relations=relations)


def _parse_top_level_statement(
    relative_path: str,
    scope_node_id: str,
    statement: str,
    start_line: int,
    end_line: int,
) -> AnchorRecord | None:
    normalized = " ".join(_strip_preprocessor_lines(statement).split())
    if not normalized:
        return None
    if normalized.startswith("#"):
        return None
    if _DECLARATION_EXCLUDE_RE.match(normalized):
        return None
    if normalized.startswith("typedef"):
        name = _extract_type_name(normalized)
        if name is None:
            return None
        return AnchorRecord(
            anchor_id=make_anchor_id(relative_path, "type_definition", name, start_line, end_line),
            scope_node_id=scope_node_id,
            kind="type_definition",
            name=name,
            path=relative_path,
            start_line=start_line,
            end_line=end_line,
        )
    if "(" in normalized and ")" in normalized:
        name = _extract_function_name(normalized)
        if name is None:
            return None
        return AnchorRecord(
            anchor_id=make_anchor_id(relative_path, "function_declaration", name, start_line, end_line),
            scope_node_id=scope_node_id,
            kind="function_declaration",
            name=name,
            path=relative_path,
            start_line=start_line,
            end_line=end_line,
        )
    named_type = _extract_named_type(normalized)
    if named_type is None:
        return None
    return AnchorRecord(
        anchor_id=make_anchor_id(relative_path, "type_definition", named_type, start_line, end_line),
        scope_node_id=scope_node_id,
        kind="type_definition",
        name=named_type,
        path=relative_path,
        start_line=start_line,
        end_line=end_line,
    )


def _extract_macros(relative_path: str, source_text: str, scope_node_id: str) -> list[AnchorRecord]:
    anchors: list[AnchorRecord] = []
    for match in _MACRO_RE.finditer(source_text):
        start_line = source_text.count("\n", 0, match.start()) + 1
        anchor = AnchorRecord(
            anchor_id=make_anchor_id(relative_path, "macro_definition", match.group(1), start_line, start_line),
            scope_node_id=scope_node_id,
            kind="macro_definition",
            name=match.group(1),
            path=relative_path,
            start_line=start_line,
            end_line=start_line,
        )
        anchors.append(anchor)
    return anchors


def _build_include_relations(anchor: AnchorRecord, relative_path: str, source_text: str) -> list[AnchorRelation]:
    relations: list[AnchorRelation] = []
    for match in _INCLUDE_RE.finditer(source_text):
        line = source_text.count("\n", 0, match.start()) + 1
        relations.append(
            AnchorRelation(
                kind="includes",
                source_anchor_id=anchor.anchor_id,
                source_name=anchor.name,
                target_name=match.group(1),
                target_path=match.group(1),
                line=line,
            )
        )
    return relations


def _extract_direct_calls(
    *,
    anchor: AnchorRecord,
    function_name: str,
    body_text: str,
    body_start_offset: int,
    line_starts: list[int],
) -> list[AnchorRelation]:
    relations: list[AnchorRelation] = []
    seen: set[tuple[str, int]] = set()
    for match in _CALL_RE.finditer(body_text):
        callee_name = match.group(1)
        if callee_name == function_name or callee_name in _CONTROL_CALLS:
            continue
        if callee_name.upper() == callee_name:
            continue
        line_start = body_text.rfind("\n", 0, match.start()) + 1
        line_prefix = body_text[line_start:match.start()].strip()
        if line_prefix.startswith("extern "):
            continue
        line = _line_number(line_starts, body_start_offset + match.start())
        relation_key = (callee_name, line)
        if relation_key in seen:
            continue
        seen.add(relation_key)
        relations.append(
            AnchorRelation(
                kind="direct_call",
                source_anchor_id=anchor.anchor_id,
                source_name=anchor.name,
                target_name=callee_name,
                line=line,
            )
        )
    return relations


def _extract_function_name(candidate: str) -> str | None:
    normalized = " ".join(_strip_preprocessor_lines(candidate).split())
    if not normalized or _DECLARATION_EXCLUDE_RE.match(normalized):
        return None
    if normalized.startswith("#"):
        return None
    if "typedef" in normalized and normalized.rstrip().endswith(")"):
        return None
    matches = _FUNCTION_NAME_RE.findall(normalized)
    if not matches:
        return None
    name = matches[-1]
    if name in _CONTROL_CALLS:
        return None
    return name


def _extract_type_name(statement: str) -> str | None:
    alias_match = _TYPEDEF_ALIAS_RE.search(statement)
    if alias_match is not None:
        return alias_match.group(1)
    return _extract_named_type(statement)


def _extract_named_type(statement: str) -> str | None:
    match = _NAMED_TYPE_RE.search(statement)
    if match is None:
        return None
    return match.group(2)


def _resolve_target_anchor(
    anchors_by_name: dict[str, list[AnchorRecord]],
    target_name: str,
) -> AnchorRecord | None:
    candidates = anchors_by_name.get(target_name, [])
    if not candidates:
        return None
    return sorted(
        candidates,
        key=lambda item: (
            0 if item.kind == "function_definition" else 1,
            item.path,
            item.start_line,
        ),
    )[0]


def _matching_brace(cleaned_text: str, opening_index: int) -> int:
    depth = 0
    for index in range(opening_index, len(cleaned_text)):
        character = cleaned_text[index]
        if character == "{":
            depth += 1
        elif character == "}":
            depth -= 1
            if depth == 0:
                return index
    return len(cleaned_text) - 1


def _scope_label(relative_path: str) -> str:
    parts = PurePosixPath(relative_path).parts
    if not parts:
        return "root"
    return parts[0]


def _line_starts(source_text: str) -> list[int]:
    starts = [0]
    for index, character in enumerate(source_text):
        if character == "\n":
            starts.append(index + 1)
    return starts


def _line_number(line_starts: list[int], offset: int) -> int:
    return bisect_right(line_starts, offset)


def _strip_comments_and_strings(source_text: str) -> str:
    characters = list(source_text)
    index = 0
    length = len(characters)
    while index < length:
        current = characters[index]
        nxt = characters[index + 1] if index + 1 < length else ""
        if current == "/" and nxt == "/":
            characters[index] = " "
            characters[index + 1] = " "
            index += 2
            while index < length and characters[index] != "\n":
                characters[index] = " "
                index += 1
            continue
        if current == "/" and nxt == "*":
            characters[index] = " "
            characters[index + 1] = " "
            index += 2
            while index + 1 < length and not (characters[index] == "*" and characters[index + 1] == "/"):
                if characters[index] != "\n":
                    characters[index] = " "
                index += 1
            if index + 1 < length:
                characters[index] = " "
                characters[index + 1] = " "
                index += 2
            continue
        if current in {'"', "'"}:
            quote = current
            characters[index] = " "
            index += 1
            while index < length:
                if characters[index] == "\\" and index + 1 < length:
                    characters[index] = " "
                    if characters[index + 1] != "\n":
                        characters[index + 1] = " "
                    index += 2
                    continue
                if characters[index] == quote:
                    characters[index] = " "
                    index += 1
                    break
                if characters[index] != "\n":
                    characters[index] = " "
                index += 1
            continue
        index += 1
    return "".join(characters)


def _strip_preprocessor_lines(candidate: str) -> str:
    return "\n".join(
        line
        for line in candidate.splitlines()
        if not line.lstrip().startswith("#")
    )


def _first_meaningful_offset(candidate: str) -> int:
    offset = 0
    for line in candidate.splitlines(keepends=True):
        stripped = line.strip()
        if stripped and not stripped.startswith("#"):
            return offset + line.index(stripped)
        offset += len(line)
    return 0
