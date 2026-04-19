---
name: analysis-maintenance
description: Use when checking export freshness and handing recovered IDs or bundle paths to later workflows.
---

# Analysis Maintenance Workflow

Use this skill when an exported analysis asset needs to be reused by a later workflow.

## Required Tool Order

```text
get_scan_status / refresh_scan
-> export_scope_snapshot / export_evidence_bundle / export_analysis_bundle
-> inspect manifest freshness
-> hand recovered IDs or bundle paths to follow-up workflows
```

## Workflow Rules

- Recover `scan_id`, `evidence_pack_id`, or `report_id` from the export manifest before calling follow-up tools.
- Prefer manifest data and copied bundle paths over ad hoc reconstruction.
- Treat `freshness.state` as the reuse signal. Reuse `fresh` bundles directly, and treat `stale` or `unknown` bundles as a prompt to refresh the source analysis first.
- For analysis bundles, use `copied_markdown_path` when the later workflow needs the exported Markdown artifact.
- Keep the handoff explicit: export first, inspect freshness second, then pass recovered IDs or bundle paths to the next workflow.
