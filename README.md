# Repo Analysis Tools

This repository is a self-use, query-first MCP toolkit for analyzing C repositories with Codex or Claude. The active query-first MCP surface rebuilds a repository snapshot, ranks the important files, and lets you inspect symbols and call relations without falling back to the old scan/scope/evidence workflow.

## Active Surface

- `rebuild_repo_snapshot`
- `list_priority_files`
- `get_file_info`
- `list_file_symbols`
- `resolve_symbols`
- `open_symbol_context`
- `query_call_relations`
- `find_root_functions`
- `find_call_paths`

```text
rebuild_repo_snapshot
-> list_priority_files
-> get_file_info
-> list_file_symbols / resolve_symbols
-> open_symbol_context / query_call_relations / find_root_functions / find_call_paths
```

## Quickstart

1. Put your Codex MCP settings in [`.codex/config.toml`](./.codex/config.toml).
2. Keep [`.mcp.json`](./.mcp.json) pointed at `repo_analysis_tools.mcp.server`.
3. Run the self-use demo to verify the query-first launch path on a real fixture:

```bash
/home/hyx/anaconda3/envs/agent/bin/python tools/run_self_use_demo.py
```

If you are using the MCP server directly, the configured server is:

- Server name: `repo-analysis-tools`
- Command: `/home/hyx/anaconda3/envs/agent/bin/python -m repo_analysis_tools.mcp.server`

## Current MCP Surface

The repository currently exposes one MCP server with a nine-tool active surface. The full request and response contract lives in [docs/contracts/mcp-tool-contracts.md](./docs/contracts/mcp-tool-contracts.md).

## Current Skills

The repository currently mirrors two workflow skills across [`.agents/skills`](./.agents/skills) and [`.claude/skills`](./.claude/skills):

- `repo-understand`
- `repo-doc-writer`

### `repo-understand`

- Purpose: analyze an unfamiliar C repository through the query-first surface.
- Required order: `rebuild_repo_snapshot -> list_priority_files -> get_file_info -> list_file_symbols/resolve_symbols -> open_symbol_context/query_call_relations/find_root_functions/find_call_paths`
- Use when you want repository understanding grounded in the active MCP surface rather than ad hoc source browsing.

### `repo-doc-writer`

- Purpose: produce a controlled repository design document set from structured findings.
- Scope: document-writer subagent only; the coordinating agent stays focused on orchestration.
- Output path: final Markdown comes from the typed document pipeline, not free-form drafting.

## Runtime Outputs

Analysis assets are stored under the target repository's `.codewiki/` directory, partitioned by domain ownership:

- `scan/`: scan snapshots and latest pointer
- `scope/`: file facts derived from scans
- `anchors/`: extracted anchors and call relations

Stable IDs currently use this prefix:

- `scan_<12-hex>`

## Key Docs

- [docs/contracts/mcp-tool-contracts.md](./docs/contracts/mcp-tool-contracts.md): MCP request/response contract surface
- [docs/architecture.md](./docs/architecture.md): architecture seams and runtime boundaries
- [docs/self-use-launch.md](./docs/self-use-launch.md): daily-use launch workflow

## Current Positioning

This project is intentionally self-use focused. It is already useful for query-first repository understanding and symbol/call tracing across a real C codebase. The workflow core is solidest when used as an MCP analysis pipeline rather than as a standalone prose-writing system.
