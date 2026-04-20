# MCP Tool Contracts

This document records the current runtime contract surface for `src/repo_analysis_tools/mcp/contracts/`. The active surface is query-first and consists of `rebuild_repo_snapshot` plus the eight query tools.

## Standard Response Envelope

All tool responses use the same outer envelope:

| Field | Meaning |
| --- | --- |
| `schema_version` | Shared envelope version. |
| `status` | `ok` or `error`. |
| `data` | Tool-specific output payload or wrapped error payload. |
| `messages` | Structured info or error messages. |
| `recommended_next_tools` | Ordered hints for the next likely tool call. |

## Stable ID Families

The current contract set uses one active stable ID family:

- `scan`: emitted as `scan_<12-hex>`

## Standard Failure Modes

The contract surface reuses the shared MCP-facing error taxonomy:

- `invalid_input`
- `not_found`
- `conflict`
- `runtime_state`
- `internal`

## Query-First Mainline

The supported mainline path is:

```text
rebuild_repo_snapshot
-> list_priority_files
-> get_file_info
-> list_file_symbols / resolve_symbols
-> open_symbol_context / query_call_relations / find_root_functions / find_call_paths
```

`rebuild_repo_snapshot` must run first in the current process so it can record the returned `scan_id` in the in-memory scan registry. Query tools read that registry instead of accepting `target_repo`, which keeps the surface query-first and prevents repeated repo-path plumbing.

## `scan`

| Tool | Inputs | Outputs | Stable IDs | Failure modes | Next tools |
| --- | --- | --- | --- | --- | --- |
| `rebuild_repo_snapshot` | `target_repo` | `scan_id`, `file_count`, `symbol_count`, `function_count`, `call_edge_count` | `scan` | `invalid_input`, `runtime_state`, `internal` | `list_priority_files`, `get_file_info` |

## `query`

| Tool | Inputs | Outputs | Stable IDs | Failure modes | Next tools |
| --- | --- | --- | --- | --- | --- |
| `list_priority_files` | `scan_id` | `files` | none | `invalid_input`, `not_found`, `internal` | `get_file_info`, `list_file_symbols` |
| `get_file_info` | `scan_id`, `path` | `path`, `role`, `priority_score`, `line_count`, `symbol_count`, `function_count`, `type_count`, `macro_count`, `include_count`, `incoming_call_count`, `outgoing_call_count`, `root_function_count`, `has_main_definition` | none | `invalid_input`, `not_found`, `internal` | `list_file_symbols`, `find_root_functions` |
| `list_file_symbols` | `scan_id`, `paths` | `files` | none | `invalid_input`, `not_found`, `internal` | `open_symbol_context`, `resolve_symbols` |
| `resolve_symbols` | `scan_id`, `symbol_name` | `match_count`, `matches` | none | `invalid_input`, `not_found`, `internal` | `open_symbol_context`, `query_call_relations` |
| `open_symbol_context` | `scan_id`, `symbol_id`, `context_lines` | `symbol_id`, `name`, `kind`, `path`, `definition_line_start`, `definition_line_end`, `context_line_start`, `context_line_end`, `lines` | none | `invalid_input`, `not_found`, `internal` | `query_call_relations`, `find_call_paths` |
| `query_call_relations` | `scan_id`, `function_id` | `callers`, `callees`, `non_resolved_callees` | none | `invalid_input`, `not_found`, `internal` | `find_call_paths`, `find_root_functions` |
| `find_root_functions` | `scan_id`, `paths` | `roots` | none | `invalid_input`, `not_found`, `internal` | `find_call_paths`, `open_symbol_context` |
| `find_call_paths` | `scan_id`, `from_function_id`, `to_function_id` | `status`, `returned_path_count`, `truncated`, `paths` | none | `invalid_input`, `not_found`, `internal` | `open_symbol_context`, `query_call_relations` |
