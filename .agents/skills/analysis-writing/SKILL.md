---
name: analysis-writing
description: Use when turning evidence-backed analysis assets into structured Markdown documents through the M4 report workflow.
---

# Analysis Writing Workflow

Use this skill when you need a structured analysis artifact instead of free-form prose.

## Required Tool Order

```text
scan_repo / refresh_scan
-> plan_slice or summarize_impact
-> build_evidence_pack
-> render_focus_report / render_module_summary / render_analysis_outline
```

## Output Rules

- Choose an explicit document type before rendering.
- Keep document generation MCP-first: do not hand-write Markdown that bypasses report tools.
- Treat the returned `markdown_path` as the final artifact location.
- Distinguish findings, interpretation, unknowns, and recommendations in the final answer.
