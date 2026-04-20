# M7 Minimal Query MCP Spec

> Parent spec: `docs/superpowers/specs/2026-04-20-minimal-query-mcp-design.md`
>
> Milestone: `M7`

## 1. Goal

Implement the first query-first MCP surface that supports repository reading without natural-language planning tools.

This milestone must make file selection, symbol lookup, symbol opening, direct call lookup, root-function discovery, and path discovery usable on real C repositories.

## 2. Scope

Included:

- one rebuild tool for repository snapshots
- file-priority output built on the existing `scope` domain
- file-info output built on persisted scope file records
- symbol lookup by name
- symbol context opening
- direct call relation queries
- strict root-function queries
- bounded call-path queries
- persisted data-model changes needed by the tools

Excluded:

- deleting legacy tools
- module-level analysis redesign
- natural-language slice planning improvements
- report-layer changes
- export-layer changes

## 3. Primary Workflow

M7 must make this path usable:

```text
rebuild_repo_snapshot
-> list_priority_files
-> get_file_info
-> list_file_symbols / resolve_symbols
-> open_symbol_context / query_call_relations / find_root_functions / find_call_paths
```

## 4. Functional Requirements

### 4.1 Rebuild

`rebuild_repo_snapshot` must:

- rescan the target repository
- rebuild scope, symbol, and call-graph assets needed by the query tools
- return one `scan_id`
- avoid git/version-management fields

### 4.2 File Priority

`list_priority_files` must:

- read from persisted scope-backed file records
- return files sorted by `priority_score` descending
- emit only `path` and `priority_score`

### 4.3 File Facts

`get_file_info` must:

- read from persisted scope-backed file records
- return only file-level structured facts
- expose persisted counts and booleans directly

### 4.4 Symbol Lookup

`list_file_symbols` and `resolve_symbols` must:

- return structured symbol records
- expose `kind`, `storage`, `line_start`, and `line_end`
- allow multiple matches from `resolve_symbols`
- avoid natural-language explanations

### 4.5 Symbol Context

`open_symbol_context` must:

- reopen the full definition span of a symbol
- include surrounding lines based on `context_lines`
- return raw source lines only

### 4.6 Direct Call Relations

`query_call_relations` must:

- accept only function IDs
- return direct callers
- return direct callees
- return unresolved or non-resolved callees with structured status values

### 4.7 Root Functions

`find_root_functions` must:

- accept file paths
- use strict semantics only
- define root as `in_repo_caller_count == 0`
- avoid filtering callback-like or external-entry-like functions

### 4.8 Call Paths

`find_call_paths` must:

- accept source and destination function IDs
- return the first `K` simple paths
- order paths by `hop_count` ascending
- expose `status`, `returned_path_count`, `truncated`, `hop_count`, `nodes`, and `call_lines`
- keep `K` implementation-defined in this milestone

## 5. Data Model Requirements

The existing `scope` domain must be extended rather than replaced.

Persisted file records must include at least:

- `path`
- `role`
- `node_id`
- `priority_score`
- `line_count`
- `symbol_count`
- `function_count`
- `type_count`
- `macro_count`
- `include_count`
- `incoming_call_count`
- `outgoing_call_count`
- `root_function_count`
- `has_main_definition`

These fields are the backing store for:

- `list_priority_files`
- `get_file_info`

## 6. Legacy Tool Handling

Legacy tools may remain present during M7, but they are not the primary surface.

During this milestone:

- do not delete legacy tools
- do not route new workflow docs through `plan_slice(question)`
- do not document legacy tools as the preferred path for repository reading

## 7. Validation Requirements

M7 validation must cover at least one real fixture repository and one small synthetic fixture.

Validation must prove:

- a rebuild produces all needed assets
- priority files are returned in deterministic order
- file facts match persisted scope-backed records
- symbol lookup and symbol opening return stable spans
- direct callers and direct callees are correct on known fixtures
- strict root-function output matches fixture expectations
- multiple call paths are returned in sorted order when they exist
- truncated path results are represented correctly when path count exceeds the implementation bound

## 8. Acceptance Criteria

M7 is complete when:

- all nine query tools return structured outputs matching the agreed design
- no new MCP tool in this surface accepts natural-language questions
- no new MCP output in this surface emits natural-language summary fields
- file-priority and file-info tools are backed by persisted scope records
- call-path queries work on real fixture repositories
- repository reading no longer depends on `plan_slice(question)` as the primary path

## 9. Risks

Main risks:

- leaking natural-language fields back into the contracts
- recomputing file facts ad hoc instead of persisting them once
- overloading scope with module-level behavior that was explicitly excluded
- path search becoming unstable or unbounded on dense call graphs

Control measures:

- contract review focused on field shape
- persist file facts in scope snapshot
- keep scope file-level only
- bound call-path enumeration with fixed `K`

## 10. Handoff

M7 hands off:

- a stable minimal query surface
- persisted file-priority and file-info data
- bounded call-path behavior
- a cleaner base for later workflow and skill rewrites
