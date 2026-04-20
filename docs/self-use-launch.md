# Self-Use Launch

This is the daily-use playbook for the Codex-first query-first launch path.

## Setup

1. Configure Codex in `.codex/config.toml`.
2. Point `.mcp.json` at `repo_analysis_tools.mcp.server`.
3. Use `/home/hyx/anaconda3/envs/agent/bin/python tools/run_self_use_demo.py` to verify the repo is wired correctly.

## Daily Use

1. Run `rebuild_repo_snapshot` to refresh the repository view when the tree changes.
2. Run `list_priority_files` to see which files the scan ranked highest.
3. Run `get_file_info` before opening source for a specific path.
4. Run `list_file_symbols` or `resolve_symbols` to narrow the symbol search.
5. Run `open_symbol_context`, `query_call_relations`, `find_root_functions`, or `find_call_paths` to trace behavior.

## Demo

Use the self-use demo command to exercise the query-first launch path:

`/home/hyx/anaconda3/envs/agent/bin/python tools/run_self_use_demo.py`
