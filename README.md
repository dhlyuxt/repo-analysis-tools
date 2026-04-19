# Repo Analysis Tools

This repository is a self-use, MCP-first toolkit for analyzing C repositories with Codex or Claude. It can scan a repository, build evidence-backed slices, trace change impact, render Markdown analysis documents, and export reusable bundles under the target repo's `.codewiki/` runtime root.

## What This Repository Does

- Scans a target repository and persists reusable analysis assets.
- Builds scope, anchor, slice, and evidence views before opening raw source.
- Traces downstream impact from changed paths or anchor names.
- Renders structured Markdown reports, including Mermaid-backed diagram blocks.
- Exports scope, evidence, and report bundles for later reuse.
- Ships a small set of workflow skills for Codex/Claude operators.

The intended workflow spine is:

```text
scan -> scope -> anchors -> slice -> evidence -> impact -> report -> export
```

## Quickstart

1. Put your Codex MCP settings in [`.codex/config.toml`](./.codex/config.toml).
2. Keep [`.mcp.json`](./.mcp.json) pointed at `repo_analysis_tools.mcp.server`.
3. Run the self-use demo to verify the launch path on a real fixture:

```bash
/home/hyx/anaconda3/envs/agent/bin/python tools/run_self_use_demo.py
```

If you are using the MCP server directly, the configured server is:

- Server name: `repo-analysis-tools`
- Command: `/home/hyx/anaconda3/envs/agent/bin/python -m repo_analysis_tools.mcp.server`

## Current MCP Surface

The repository currently exposes one MCP server with 8 tool domains and 24 tools. The full request and response contract lives in [docs/contracts/mcp-tool-contracts.md](./docs/contracts/mcp-tool-contracts.md).

### `scan`

- `scan_repo`: create a fresh scan snapshot for a target repository.
- `refresh_scan`: rescan an existing target from a prior `scan_id`.
- `get_scan_status`: reopen a persisted scan summary.

### `scope`

- `show_scope`: summarize high-level scope and role counts.
- `list_scope_nodes`: list scope nodes for the current scan.
- `explain_scope_node`: explain a specific scope node and its related files.

### `anchors`

- `list_anchors`: list extracted anchors for a scan.
- `find_anchor`: find matching definitions or declarations by anchor name.
- `describe_anchor`: describe an anchor and its discovered relations.

### `slice`

- `plan_slice`: turn a question into a bounded slice.
- `expand_slice`: expand a persisted slice.
- `inspect_slice`: inspect slice members before evidence building.

### `evidence`

- `build_evidence_pack`: create a cited evidence pack from a slice.
- `read_evidence_pack`: reopen the structured citations in an evidence pack.
- `open_span`: open only a cited source window within evidence bounds.

### `impact`

- `impact_from_paths`: analyze downstream impact starting from changed paths.
- `impact_from_anchor`: analyze downstream impact starting from an anchor.
- `summarize_impact`: produce confirmed impact, likely propagation, blind spots, and regression focus.

### `report`

- `render_focus_report`: render an evidence-backed `issue-analysis` or `review-report`.
- `render_module_summary`: render a `module-summary` document for a chosen module.
- `render_analysis_outline`: render a `design-note` style outline from a focus string.

### `export`

- `export_analysis_bundle`: export a rendered report plus freshness metadata.
- `export_scope_snapshot`: export a persisted scope snapshot.
- `export_evidence_bundle`: export a persisted evidence pack.

## Current Skills

The repository currently distributes 4 workflow skills. They are mirrored in both [`.agents/skills`](./.agents/skills) and [`.claude/skills`](./.claude/skills) so the same workflow guidance can be used from different clients.

### `repo-understand`

- Purpose: analyze an unfamiliar C repository through the analysis-first mainline.
- Required order: `scan_repo -> get_scan_status -> show_scope -> list_anchors/find_anchor/describe_anchor -> plan_slice -> build_evidence_pack -> read_evidence_pack -> open_span`
- Use when you want repository understanding grounded in MCP evidence rather than ad hoc source browsing.

### `change-impact`

- Purpose: analyze what a change may affect downstream.
- Required order: `refresh_scan -> impact_from_paths/impact_from_anchor -> summarize_impact -> inspect related anchors or slices -> build_evidence_pack`
- Use when you need regression focus and want confirmed impact, likely propagation, and blind spots kept separate.

### `analysis-writing`

- Purpose: turn evidence-backed analysis assets into structured Markdown documents.
- Required order: `scan_repo/refresh_scan -> plan_slice or summarize_impact -> build_evidence_pack -> render_focus_report/render_module_summary/render_analysis_outline`
- Use when you want report artifacts instead of free-form prose.

### `analysis-maintenance`

- Purpose: reuse exported analysis assets safely.
- Required order: `get_scan_status/refresh_scan -> export_scope_snapshot/export_evidence_bundle/export_analysis_bundle -> inspect manifest freshness -> hand recovered IDs or bundle paths to follow-up workflows`
- Use when a later workflow needs to recover `scan_id`, `evidence_pack_id`, `report_id`, or exported Markdown from a bundle.

## Runtime Outputs

Analysis assets are stored under the target repository's `.codewiki/` directory, partitioned by domain ownership:

- `scan/`: scan snapshots and latest pointer
- `scope/`: scope snapshots
- `anchors/`: extracted anchors and relations
- `slice/`: slice manifests
- `evidence/`: evidence packs and citations
- `impact/`: impact results
- `report/`: rendered Markdown reports and metadata
- `export/`: reusable bundles, manifests, payloads, and copied report artifacts

Stable IDs currently use these prefixes:

- `scan_<12-hex>`
- `slice_<12-hex>`
- `evidence_pack_<12-hex>`
- `impact_<12-hex>`
- `report_<12-hex>`
- `export_<12-hex>`

## Key Docs

- [docs/contracts/mcp-tool-contracts.md](./docs/contracts/mcp-tool-contracts.md): MCP request/response contract surface
- [docs/architecture.md](./docs/architecture.md): architecture seams and runtime boundaries
- [docs/self-use-launch.md](./docs/self-use-launch.md): daily-use launch workflow

## Current Positioning

This project is intentionally self-use focused. It is already useful for:

- evidence-backed repository understanding
- change-impact analysis
- structured Markdown report generation
- export and later reuse of analysis assets

It is not yet a polished general-purpose documentation generator. The workflow core is solidest when used as an MCP analysis pipeline rather than as a standalone prose-writing system.
