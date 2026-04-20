# Minimal Query MCP Design

## 1. Goal

Define a minimal MCP query surface for repository reading that is:

- query-first
- structure-first
- file/symbol/call-graph centered
- free of natural-language input and output fields

This design replaces the current question-planning-centered mainline with a narrow set of deterministic query tools.

## 2. Design Rules

The future MCP surface follows these rules:

- MCP tools do not accept natural-language questions.
- MCP tools do not emit natural-language fields such as `summary`, `description`, `notes`, `reasons`, or `messages`.
- The only repository bootstrap tool is `rebuild_repo_snapshot`.
- All follow-up query tools accept `scan_id`.
- Cross-tool symbol navigation uses `symbol_id`.
- Scope remains file-level only.
- Call-graph queries are function-only.

Allowed field categories:

- identifiers: `scan_id`, `symbol_id`, `path`
- enums: `kind`, `storage`, `role`, `status`
- counts and scores
- booleans
- source spans
- raw source lines

## 3. MCP Surface

### 3.1 `rebuild_repo_snapshot`

Input:

```json
{
  "target_repo": "/repo"
}
```

Output:

```json
{
  "scan_id": "scan_xxx",
  "file_count": 120,
  "symbol_count": 860,
  "function_count": 430,
  "call_edge_count": 1200
}
```

### 3.2 `list_priority_files`

Input:

```json
{
  "scan_id": "scan_xxx"
}
```

Output:

```json
{
  "files": [
    {
      "path": "src/main.c",
      "priority_score": 98
    },
    {
      "path": "src/boot.c",
      "priority_score": 91
    }
  ]
}
```

Rules:

- sort by `priority_score` descending
- return only `path` and `priority_score`

### 3.3 `get_file_info`

Input:

```json
{
  "scan_id": "scan_xxx",
  "path": "src/main.c"
}
```

Output:

```json
{
  "path": "src/main.c",
  "role": "primary",
  "priority_score": 98,
  "line_count": 120,
  "symbol_count": 9,
  "function_count": 7,
  "type_count": 1,
  "macro_count": 3,
  "include_count": 4,
  "incoming_call_count": 0,
  "outgoing_call_count": 12,
  "root_function_count": 1,
  "has_main_definition": true
}
```

### 3.4 `list_file_symbols`

Input:

```json
{
  "scan_id": "scan_xxx",
  "paths": ["src/main.c", "src/flash.c"]
}
```

Output:

```json
{
  "files": [
    {
      "path": "src/main.c",
      "symbols": [
        {
          "symbol_id": "sym_main",
          "name": "main",
          "kind": "function",
          "line_start": 10,
          "line_end": 30,
          "is_definition": true,
          "storage": "global"
        }
      ]
    }
  ]
}
```

### 3.5 `resolve_symbols`

Input:

```json
{
  "scan_id": "scan_xxx",
  "symbol_name": "flash_init"
}
```

Output:

```json
{
  "match_count": 1,
  "matches": [
    {
      "symbol_id": "sym_flash_init",
      "name": "flash_init",
      "kind": "function",
      "path": "src/flash.c",
      "line_start": 20,
      "line_end": 45,
      "is_definition": true,
      "storage": "global"
    }
  ]
}
```

Rules:

- input does not include symbol type
- output always includes real `kind`
- multiple matches are allowed

### 3.6 `open_symbol_context`

Input:

```json
{
  "scan_id": "scan_xxx",
  "symbol_id": "sym_flash_init",
  "context_lines": 8
}
```

Output:

```json
{
  "symbol_id": "sym_flash_init",
  "name": "flash_init",
  "kind": "function",
  "path": "src/flash.c",
  "definition_line_start": 20,
  "definition_line_end": 45,
  "context_line_start": 12,
  "context_line_end": 53,
  "lines": [
    "/* ... */",
    "int flash_init(void) {",
    "...",
    "}"
  ]
}
```

Rules:

- function queries return the full function definition including body
- type queries return the full type definition
- `context_lines` expands before and after the definition span

### 3.7 `query_call_relations`

Input:

```json
{
  "scan_id": "scan_xxx",
  "function_id": "sym_flash_init"
}
```

Output:

```json
{
  "callers": [
    {
      "symbol_id": "sym_main",
      "name": "main",
      "path": "src/main.c",
      "call_lines": [27]
    }
  ],
  "callees": [
    {
      "symbol_id": "sym_port_init",
      "name": "port_init",
      "path": "src/port.c",
      "call_lines": [33]
    }
  ],
  "non_resolved_callees": [
    {
      "name": "HAL_Init",
      "status": "external",
      "call_lines": [35]
    }
  ]
}
```

Rules:

- return only direct callers and direct callees
- tool is function-only

### 3.8 `find_root_functions`

Input:

```json
{
  "scan_id": "scan_xxx",
  "paths": ["src/main.c", "src/startup.c"]
}
```

Output:

```json
{
  "roots": [
    {
      "symbol_id": "sym_main",
      "name": "main",
      "path": "src/main.c",
      "line_start": 10,
      "line_end": 30,
      "storage": "global"
    }
  ]
}
```

Rules:

- strict semantic: root means `in_repo_caller_count == 0`
- no heuristic filtering

### 3.9 `find_call_paths`

Input:

```json
{
  "scan_id": "scan_xxx",
  "from_function_id": "sym_main",
  "to_function_id": "sym_flash_init"
}
```

Output:

```json
{
  "status": "found",
  "returned_path_count": 2,
  "truncated": false,
  "paths": [
    {
      "hop_count": 2,
      "nodes": [
        {
          "symbol_id": "sym_main",
          "name": "main",
          "path": "src/main.c"
        },
        {
          "symbol_id": "sym_boot",
          "name": "boot_init",
          "path": "src/boot.c"
        },
        {
          "symbol_id": "sym_flash_init",
          "name": "flash_init",
          "path": "src/flash.c"
        }
      ],
      "call_lines": [22, 41]
    }
  ]
}
```

Rules:

- return the first `K` simple paths
- order by `hop_count` ascending
- if actual path count exceeds `K`, set `status = "truncated"` and `truncated = true`
- do not expose `K` as an input parameter in the first implementation

## 4. Fixed Enums

```text
kind = function | type | macro | variable
storage = global | static | extern | unknown
role = primary | support | external | generated
status = found | no_path | truncated
non_resolved_callees.status = external | ambiguous | function_pointer_like | macro_like | unresolved
```

## 5. Scope Reuse Direction

The new file-priority tools must reuse the existing `scope` domain instead of introducing a second file-analysis system.

Current `scope` already provides:

- file inclusion and filtering
- file role classification
- top-level grouping into nodes
- persisted `ScopeSnapshot`

The next step is to extend persisted file records so file-priority and file-info MCPs can read from one stored snapshot.

## 6. Explicit Non-Goals

This design does not include:

- natural-language planning tools such as `plan_slice(question)`
- function-importance explanations in MCP output
- module-level scope redesign
- version-management-oriented scan tools
- deleting legacy tools before the replacement surface is implemented
