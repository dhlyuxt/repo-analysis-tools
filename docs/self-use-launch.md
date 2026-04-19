# Self-Use Launch

This is the daily-use playbook for the Codex-first launch path.

## Setup

1. Configure Codex in `.codex/config.toml`.
2. Point `.mcp.json` at `repo-analysis-mcp`.
3. Use `/home/hyx/anaconda3/envs/agent/bin/python tools/run_self_use_demo.py` to verify the repo is wired correctly.

## Daily Use

1. Run `scan_repo` to refresh the repository view when the tree changes.
2. Run `build_evidence_pack` after slice planning to capture cited evidence.
3. Run `summarize_impact` when a change needs regression focus.
4. Run `render_module_summary` to turn evidence into a stable Markdown report.
5. Run `export_analysis_bundle` when you want to hand the report to a later workflow.
6. Run `refresh_scan` before reuse if the repository may have drifted.

## Demo

Use the self-use demo command to exercise the full launch path:

`/home/hyx/anaconda3/envs/agent/bin/python tools/run_self_use_demo.py`
