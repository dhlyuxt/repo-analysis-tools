---
name: repo-understand
description: Use when analyzing an unfamiliar C repository through the analysis-first MCP mainline.
---

# Repo Understand Workflow

Use this skill for repository understanding tasks that must be grounded in MCP evidence.

## Required Tool Order

Follow this order unless a later step is impossible:

```text
scan_repo
-> get_scan_status
-> show_scope
-> list_anchors / find_anchor / describe_anchor
-> plan_slice
-> build_evidence_pack
-> read_evidence_pack
-> open_span
```

## Output Rules

- Start with facts from `scan_repo` and `show_scope`.
- Use anchors and slices to narrow the analysis before reading raw source.
- Treat `read_evidence_pack` as the evidence handoff point.
- Use `open_span` only for line ranges fully covered by the cited evidence pack.
- Distinguish confirmed facts, interpretation, and unknowns in the final answer.
- Cite file paths and line ranges for every code claim.

## Safety Rules

- Do not use `open_span` as a general file reader.
- Do not infer behavior that is not backed by a citation.
- If the evidence is insufficient, say so and stop instead of guessing.
