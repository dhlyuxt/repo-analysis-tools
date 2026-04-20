---
name: repo-understand
description: Use when analyzing an unfamiliar C repository through the query-first MCP surface.
---

# Repo Understand Workflow

Use this skill for repository understanding tasks that should stay within the active query-first MCP surface.

## Required Tool Order

Follow this order unless a later step is impossible:

```text
rebuild_repo_snapshot
-> list_priority_files
-> get_file_info
-> list_file_symbols / resolve_symbols
-> open_symbol_context / query_call_relations / find_root_functions / find_call_paths
```

## Output Rules

- Start with `rebuild_repo_snapshot` and the highest-priority files.
- Use `get_file_info` before opening raw source.
- Prefer `resolve_symbols` to locate a symbol, then `open_symbol_context`.
- Use `query_call_relations` and `find_call_paths` to trace behavior before guessing.
- Distinguish confirmed facts, interpretation, and unknowns in the final answer.
- Cite file paths and line ranges for every code claim.

## Safety Rules

- Do not treat the old scan/scope/evidence workflow as active.
- Do not use raw source browsing as the first move when the query surface can answer the question.
- Do not infer behavior that is not backed by a citation.
- If the query results are insufficient, say so and stop instead of guessing.
