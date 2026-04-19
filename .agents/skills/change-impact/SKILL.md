---
name: change-impact
description: Use when analyzing the downstream impact of changed files or a specific anchor through the MCP change-impact workflow.
---

# Change Impact Workflow

Use this skill when you need an evidence-backed view of what a code change may affect.

## Required Tool Order

Start from either changed files or a known anchor and follow this order:

```text
refresh_scan
-> impact_from_paths / impact_from_anchor
-> summarize_impact
-> inspect related anchors or slices
-> build_evidence_pack
```

If you need to quote source afterward, reopen the cited material through `read_evidence_pack` and `open_span`.

## Output Rules

- Keep the skill orchestration-only. Do not add impact logic outside the MCP tools.
- Start by stating the seed you used: changed paths or anchor name.
- Report `confirmed_impact`, `likely_propagation`, and `blind_spots` as separate buckets.
- Treat `summarize_impact` as the handoff for risks and regression focus.
- Use `plan_slice` or anchor inspection only to narrow follow-up evidence after the impact summary.
- Treat `build_evidence_pack` as the evidence handoff point for any final code claims.

## Safety Rules

- Do not present likely propagation as proven caller impact.
- Do not skip `refresh_scan`; impact must run against a fresh scan snapshot.
- Do not treat `build_evidence_pack` as optional when making source-backed claims.
- If the summary leaves blind spots, say so explicitly instead of guessing.
