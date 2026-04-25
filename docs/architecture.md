# Query-First Architecture

This document records the architecture seams that the active query-first MCP surface must preserve.

## Package Boundaries

The repository keeps a visible top-level split between:

- `core`: shared IDs, path rules, envelope helpers, and common error types.
- `storage`: domain-owned runtime directories and persistence boundaries.
- `scan`: repository scan lifecycle and scan handles.
- `scope`: persisted file facts derived from scans.
- `anchors`: anchor discovery and call-relation persistence.
- `query`: query orchestration across scan, scope, and anchor stores.
- `mcp`: server bootstrap, registry, contracts, and tool adapters.
- `skills`: workflow-facing skill packaging.
- `tests`: contract, unit, integration, and golden verification layers.

The intended workflow spine is `scan -> scope -> anchors -> query`.

## Query-First Handoff

The active MCP path for repository understanding is:

```text
rebuild_repo_snapshot
-> list_priority_files
-> get_file_info
-> list_file_symbols / resolve_symbols
-> open_symbol_context / query_call_relations / find_root_functions / find_call_paths
```

The active tools are:

- `rebuild_repo_snapshot`
- `list_priority_files`
- `get_file_info`
- `list_file_symbols`
- `resolve_symbols`
- `open_symbol_context`
- `query_call_relations`
- `find_root_functions`
- `find_call_paths`

The supported persistence model is JSON-first and domain-owned. Each rebuild writes runtime assets under `<target_repo>/.codewiki/` in domain-specific directories so later query steps can reopen prior results without recomputing everything:

- `<target_repo>/.codewiki/scan/` stores scan snapshots and the latest scan pointer.
- `<target_repo>/.codewiki/scope/` stores file facts derived from scans.
- `<target_repo>/.codewiki/anchors/` stores extracted anchors and call relations.

`rebuild_repo_snapshot` must complete before any query tool is used in the same process. The process-local `scan_id -> repo_root` registry is what lets the query wrappers recover the repo root without accepting a `target_repo` argument.

## Repository Design Document Handoff

Repository design documentation is a separate handoff from repository understanding:

```text
repository audit workflow
-> structured findings package
-> document writer subagent loads repo-doc-writer
-> doc_specs / doc_dsl / validators / MarkdownRenderer
-> docs/repo-design/*
```

The coordinating agent remains orchestration-only. It prepares and hands off structured findings, but does not absorb section policy or renderer rules from the document pipeline.

## Runtime Root And Path Rules

All runtime-owned artifacts live under `<target_repo>/.codewiki/`.

The runtime contract is:

- path normalization always resolves against the target repository root and emits repo-relative POSIX paths
- attempts to escape the repository root are rejected
- domain storage is allocated by declared ownership, not by ad hoc tool decisions

## Stable Identifier Families

The active surface reserves one stable ID prefix for reusable artifacts:

| Artifact | Prefix | Notes |
| --- | --- | --- |
| scan handle | `scan_` | Used for scan lifecycle and scan-derived reads. |
| query lookups | none | Query tools use the in-process registry and file paths instead of new stable IDs. |

## Storage Ownership

Every runtime directory is owned by one domain under `<target_repo>/.codewiki/`:

| Domain | Directory | Owned artifacts |
| --- | --- | --- |
| `scan` | `scan` | scan metadata and scan handles |
| `scope` | `scope` | scope snapshots derived from scans |
| `anchors` | `anchors` | anchor extraction outputs and call relations |

## MCP Response Envelope

Every MCP-facing tool response uses the same top-level envelope:

| Field | Meaning |
| --- | --- |
| `schema_version` | Contract schema version for the envelope. |
| `status` | `ok` on success or `error` on failure. |
| `data` | Tool-specific payload or error object. |
| `messages` | Structured info or error messages. |
| `recommended_next_tools` | Ordered hints for the next likely workflow step. |

The envelope exists to keep clients MCP-first and client-neutral instead of depending on any chat-runtime-specific format.

## MCP-Facing Error Taxonomy

The shared error code set is:

- `invalid_input`: caller supplied malformed or incomplete input.
- `not_found`: requested runtime artifact or repository target does not exist.
- `conflict`: the requested action collides with existing state or ownership.
- `runtime_state`: runtime prerequisites are missing or the runtime is not ready.
- `internal`: an unexpected internal failure escaped a lower layer.

These errors are exposed through the common envelope instead of domain-specific ad hoc payloads.
