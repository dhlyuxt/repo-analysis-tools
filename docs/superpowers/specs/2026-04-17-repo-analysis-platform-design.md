# Repo Analysis Platform Design

> Scope: new repository architecture and rollout plan for replacing `mycodewiki` with a Codex-first, MCP-centered C repository analysis platform.

## 1. Goal

Build a new repository that replaces `mycodewiki` as the daily entry point for C repository analysis.

The new repository is not a chat application and not a clone of the old CLI surface. It is a layered analysis platform with:

- a deterministic offline analysis core
- a domain-organized MCP server that exposes the offline capabilities
- workflow skills for repository understanding, change impact analysis, and analysis document authoring
- a document specification and DSL layer that renders structured analysis artifacts into Markdown

The initial priority is analysis-first: a user working in Codex should be able to understand a real C repository, trace evidence, and inspect precise code spans through MCP-driven workflows.

## 2. Product Positioning

### 2.1 What This Repository Is

This repository is a code repository analysis platform composed of:

1. offline analysis capabilities
2. MCP tools organized by analysis domain
3. workflow-oriented skills
4. structured document specs, document DSL models, and Python renderers

### 2.2 What This Repository Is Not

This repository is not:

- a new agent runtime
- a legacy CLI compatibility layer
- a whole-repository chat product
- a prompt-heavy orchestration shell that hides core logic inside skills

The new platform is client-neutral at the architecture level, but it is optimized first for Codex usage and kept Claude-compatible.

## 3. Design Constraints

The design is constrained by the following approved decisions:

- `Codex` is the primary client target.
- The repository is `self-use first`, but the structure should stay extensible.
- The migration strategy is `new repository rebuild + selective harvesting`.
- Compatibility policy is `zero compatibility` with old CLI and legacy output formats.
- The roadmap must include repository understanding, change impact analysis, and analysis document authoring.
- The first milestone priority is `analysis first`.
- Old offline analysis capabilities should be moved into `domain-organized MCP tools` as much as practical.
- Skills should represent `workflows`, not thin wrappers around single tools.
- Document output must be driven by `document spec + typed DSL + Python renderer`, not free-form Markdown templates.

## 4. Core Principles

### 4.1 MCP First

Offline analysis capabilities with long-term value belong in the MCP layer, not in ad hoc CLI code and not inside workflow skills.

### 4.2 Workflow Skills Only

Skills define how to execute an analysis workflow. They do not own analysis logic, indexing logic, or evidence extraction rules.

### 4.3 Facts Before Prose

Structured facts come first:

- scope
- anchors
- slices
- evidence packs
- impact results
- report skeletons

Natural-language explanations and documents are downstream products of those facts.

### 4.4 Analysis First

The first production-quality workflow is repository understanding with evidence traceability. Change impact and document authoring follow after that path is stable.

### 4.5 Zero Compatibility Debt

The new platform does not preserve old command names, old output contracts, or old directory layouts just to ease migration. The old repository is a reference implementation and test baseline, not a compatibility target.

## 5. Target Architecture

The platform is split into four runtime layers and one migration support layer.

### 5.1 Offline Analysis Core

Responsibilities:

- scan repositories
- classify scope
- extract anchors
- plan and expand slices
- build evidence packs
- calculate change impact
- produce report skeletons
- export analysis assets

This layer must remain deterministic and independent from chat workflows and prompt orchestration.

### 5.2 Domain MCP Layer

Responsibilities:

- expose core capabilities as MCP tools
- validate inputs and normalize paths
- manage stable handles and IDs
- enforce read boundaries for span access
- provide consistent response contracts
- recommend likely next tools for workflow clients

This layer is the main product API.

### 5.3 Workflow Skill Layer

Responsibilities:

- define repository understanding workflows
- define change impact workflows
- define analysis writing workflows
- tell clients how to sequence MCP tools
- constrain outputs into structured findings

Skills are orchestration and authoring guides, not analysis engines.

### 5.4 Document Spec / DSL / Renderer Layer

Responsibilities:

- define per-document structural requirements
- hold typed document models
- validate document completeness and evidence binding
- render final Markdown artifacts from typed document objects

This layer is required so document generation remains reproducible and reviewable.

### 5.5 Migration and Verification Layer

Responsibilities:

- inventory old repository capabilities
- classify each old module as keep, rewrite, test-only, or drop
- preserve golden fixtures
- preserve behavior baselines
- validate new results against selected old outputs when useful

## 6. Repository Layout

Recommended repository shape:

```text
repo-analysis-tools/
  pyproject.toml
  README.md

  docs/
    architecture.md
    contracts/
    migration/
    workflows/

  docs/superpowers/specs/

  src/repo_analysis_tools/
    core/
      models/
      errors.py
      types.py
      ids.py
      paths.py

    storage/
      repo_store.py
      scan_store.py
      slice_store.py
      evidence_store.py
      report_store.py

    scan/
    scope/
    anchors/
    slice/
    evidence/
    impact/
    report/
    export/

    mcp/
      server.py
      registry.py
      contracts/
      tools/
        scan_tools.py
        scope_tools.py
        anchor_tools.py
        slice_tools.py
        evidence_tools.py
        impact_tools.py
        report_tools.py
        export_tools.py

    skills/
      src/
      dist/

    doc_specs/
      module_summary.py
      issue_analysis.py
      design_note.py
      review_report.py

    doc_dsl/
      models.py
      builders.py
      validators.py

    renderers/
      markdown.py
      citations.py
      sections.py

    cli/
      main.py
      dev.py

  migration/
    old-repo-inventory.md
    capability-mapping.md
    keep-drop-rewrite.md

  tests/
    fixtures/
    golden/
    contract/
    integration/
    e2e/

  third_party/
    fsoft_codewiki_c/
```

## 7. Runtime and Storage Conventions

### 7.1 Runtime Directory

Per-target-repository runtime artifacts live under:

```text
<target_repo>/.codewiki/
```

This replaces client-specific layouts such as `<repo>/.claude/...` and keeps the platform neutral.

### 7.2 Stable Handles

MCP tools should prefer stable identifiers and handles for reusable artifacts, including:

- scan IDs
- slice IDs
- evidence pack IDs
- report IDs
- export IDs

### 7.3 CLI Role

CLI support is secondary and exists mainly for development, diagnostics, and local validation. The primary product surface is MCP.

## 8. Domain-Organized MCP Surface

The MCP surface is grouped by analysis domain instead of old command names.

### 8.1 Scan Tools

Purpose: create and refresh base analysis assets for a target repository.

Initial tools:

- `scan_repo`
- `refresh_scan`
- `get_scan_status`

### 8.2 Scope Tools

Purpose: expose the repository structure and classified areas.

Initial tools:

- `show_scope`
- `list_scope_nodes`
- `explain_scope_node`

### 8.3 Anchor Tools

Purpose: expose structural anchors such as functions, macros, types, globals, and exported entry points.

Initial tools:

- `list_anchors`
- `find_anchor`
- `describe_anchor`

### 8.4 Slice Tools

Purpose: build focused analysis slices around a question, symbol, path set, or structural target.

Initial tools:

- `plan_slice`
- `expand_slice`
- `inspect_slice`

### 8.5 Evidence Tools

Purpose: turn slices into readable evidence artifacts and bound detailed code reading.

Initial tools:

- `build_evidence_pack`
- `read_evidence_pack`
- `open_span`

`open_span` must remain guarded. It should only expose code within the selected evidence or explicitly validated regions, and it should enforce line limits.

### 8.6 Impact Tools

Purpose: support change-centered reasoning.

Initial tools:

- `impact_from_paths`
- `impact_from_anchor`
- `summarize_impact`

### 8.7 Report Tools

Purpose: produce structured report skeletons from analysis outputs.

Initial tools:

- `render_focus_report`
- `render_module_summary`
- `render_analysis_outline`

### 8.8 Export Tools

Purpose: export reusable analysis assets for later workflows and review.

Initial tools:

- `export_analysis_bundle`
- `export_scope_snapshot`
- `export_evidence_bundle`

## 9. MCP Response Contract

All MCP tools should converge on a common response shape:

```json
{
  "schema_version": "1",
  "status": "ok",
  "data": {},
  "messages": [],
  "recommended_next_tools": []
}
```

Recommended rules:

- `data` contains the typed domain payload.
- `messages` contains human-readable notes, warnings, or freshness hints.
- `recommended_next_tools` points workflow clients to the next likely analysis step.
- error responses should preserve the same top-level shape where possible.

## 10. Workflow Skill System

Skills should be few, top-level, and workflow-oriented.

### 10.1 `repo-understand`

Primary goal: understand an unfamiliar C repository with evidence traceability.

Typical flow:

```text
scan_repo
-> get_scan_status
-> show_scope
-> find_anchor / list_anchors
-> plan_slice
-> build_evidence_pack
-> read_evidence_pack
-> open_span
-> structured findings
```

Expected outputs:

- repository structure summary
- module responsibility summary
- anchor explanation
- call-path or initialization-path explanation
- explicit distinction between confirmed facts, interpretation, and unknowns

### 10.2 `change-impact`

Primary goal: analyze the effect of changing files, anchors, or areas.

Typical flow:

```text
refresh_scan
-> impact_from_paths / impact_from_anchor
-> summarize_impact
-> inspect affected slices and anchors
-> build_evidence_pack
-> risk note
```

Expected outputs:

- directly affected modules
- likely propagation points
- risk notes
- recommended regression targets
- identified blind spots

### 10.3 `analysis-writing`

Primary goal: convert structured analysis outputs into typed document objects, then render final Markdown through Python renderers.

Typical flow:

```text
select document type
-> gather evidence / impact / report assets
-> build typed document object
-> validate against document spec
-> render Markdown
```

This workflow must not jump directly from analysis to free-form prose.

### 10.4 `analysis-maintenance`

Primary goal: maintain analysis freshness and asset reuse.

Typical flow:

```text
get_scan_status
-> inspect asset freshness
-> refresh selected assets
-> export reusable artifacts
```

This workflow is lower priority but supports long-term usability.

## 11. Document System

The document layer is not a plain template system. It is a structured specification-and-rendering pipeline.

### 11.1 Document Specs

Each document type defines:

- required sections
- accepted evidence sources
- allowed field types
- mandatory conclusion fields
- evidence-binding requirements

Initial document types:

- `module-summary`
- `issue-analysis`
- `design-note`
- `review-report`

### 11.2 Document DSL

The DSL source of truth uses typed Python models, preferably `pydantic` or `dataclass`-based models.

The typed models should represent:

- document metadata
- section tree
- factual findings
- interpretations
- unknowns
- cited anchors, slices, evidence packs, and spans
- risks
- recommendations
- summary statements

The system may serialize those objects to YAML or JSON for storage and debugging, but the authoritative in-memory source is the typed Python model.

### 11.3 Python Renderers

Renderers convert typed document objects into Markdown.

Renderer responsibilities:

- validate document completeness
- enforce section order and hierarchy
- standardize citation placement
- standardize evidence formatting
- generate final Markdown files

## 12. Migration Strategy

Migration strategy is selective harvesting, not direct transplantation.

### 12.1 Categories

Old repository modules should be classified into:

- `migrate and reorganize`
- `extract logic, rewrite shell`
- `test-only baseline`
- `drop`

### 12.2 Likely Keep Areas

Expected sources of reusable deterministic logic:

- `scan`
- `scope`
- `anchors`
- `slices`
- `evidence`
- `impact`
- `reporting`
- selected C-analysis vendored modules

### 12.3 Likely Drop Areas

Expected non-target areas:

- `ask`
- `answers`
- `retrieval`
- `agent_runtime`
- legacy compatibility commands
- chat-style orchestration shells

### 12.4 Migration Artifacts

The new repository should maintain:

- `old-repo-inventory`
- `capability-mapping`
- `keep-drop-rewrite`

These documents are part of the product build process, not optional notes.

## 13. Roadmap Overview

### Phase 0: Harvest and Classify the Old Repository

Deliverables:

- complete offline capability inventory
- domain remapping into scan, scope, anchors, slice, evidence, impact, report, export
- keep, rewrite, test-only, and drop decisions
- selected real C repositories for long-term fixtures
- `.codewiki/` runtime decision recorded

### Phase 1: New Repository Skeleton and Contracts

Deliverables:

- base package layout
- unified IDs, error types, and storage contracts
- `.codewiki/` runtime layout
- bootable MCP server with contract stubs
- contract test skeleton
- golden test skeleton

Exit criteria:

- the repository layout is stable
- MCP server starts successfully
- response contracts are fixed enough to support workflow work

### Phase 2: Analysis-First Mainline

Priority path:

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

Deliverables:

- migrated and reorganized `scan`, `scope`, `anchors`, `slice`, and `evidence` capabilities
- domain MCP tools for the path above
- first `repo-understand` workflow skill
- end-to-end validation on a real C repository

Exit criteria:

- a Codex session can analyze an unfamiliar C repository and trace findings back to evidence

### Phase 3: Change Impact Workflow

Deliverables:

- reorganized impact analysis core
- `impact_from_paths`, `impact_from_anchor`, and `summarize_impact`
- first `change-impact` workflow skill
- real-change validation scenario

Exit criteria:

- file or anchor changes produce a credible impact summary, risk notes, and regression targets

### Phase 4: Document Spec / DSL / Renderer

Deliverables:

- document specs for the initial document types
- typed document DSL models
- validators
- Markdown renderer
- first `analysis-writing` workflow skill

Exit criteria:

- structured analysis results can be rendered into constrained Markdown through the typed document pipeline

### Phase 5: Export and Asset Reuse

Deliverables:

- export tools
- reusable analysis bundles
- scope snapshots
- evidence bundles
- freshness and reuse hooks where practical

Exit criteria:

- analysis results can be reused across later workflows and reviews

### Phase 6: Self-Use Launch

Deliverables:

- Codex-first install and bootstrap path
- Claude-compatible skill distribution
- minimal operator documentation
- demo validation script
- end-to-end dry run from scan through at least repository understanding and document rendering

Exit criteria:

- the new repository can replace the old one for daily analysis work on real C repositories

Detailed phase specs live in separate documents:

- `M0`: `docs/superpowers/specs/2026-04-17-m0-old-repo-harvest-spec.md`
- `M1`: `docs/superpowers/specs/2026-04-17-m1-platform-skeleton-and-contracts-spec.md`
- `M2`: `docs/superpowers/specs/2026-04-17-m2-analysis-first-mainline-spec.md`
- `M3`: `docs/superpowers/specs/2026-04-17-m3-change-impact-workflow-spec.md`
- `M4`: `docs/superpowers/specs/2026-04-17-m4-document-dsl-and-rendering-spec.md`
- `M5`: `docs/superpowers/specs/2026-04-17-m5-export-and-asset-reuse-spec.md`
- `M6`: `docs/superpowers/specs/2026-04-17-m6-self-use-launch-spec.md`

## 14. Milestones

- `M0`: old repository inventory and migration decisions complete
- `M1`: repository skeleton, storage rules, and MCP contracts complete
- `M2`: analysis-first mainline usable
- `M3`: change impact workflow usable
- `M4`: document DSL and Markdown rendering usable
- `M5`: export and asset reuse usable
- `M6`: self-use launch complete

## 15. Major Risks and Controls

### 15.1 MCP Surface Sprawl

Risk: tool design degenerates into a renamed copy of old commands.

Control: keep tools domain-based and ensure each tool owns one analysis responsibility.

### 15.2 Business Logic Leaking into Skills

Risk: workflows become the real implementation layer.

Control: require all durable analysis logic to live in core or MCP layers.

### 15.3 Document System Collapsing into Free-Form Markdown

Risk: document quality becomes inconsistent and unreviewable.

Control: keep typed DSL models and spec validation mandatory before rendering.

### 15.4 Overloading Phase 2

Risk: first execution phase tries to solve analysis, impact, export, and document authoring at once.

Control: protect the analysis-first path and defer deeper impact and authoring work until later phases.

### 15.5 Structural Drift Toward the Old Repository

Risk: migration convenience pulls the new repository back into the old layout.

Control: treat the new package structure as the architectural source of truth.

## 16. Launch Definition

For this self-use launch, the platform is considered live when the following statement is true:

> In Codex, on a real C repository, the system can reliably perform repository understanding, evidence tracing, and basic change impact analysis, and it can render structured analysis results into Markdown through the document spec and typed DSL pipeline.

## 17. Summary

The new repository replaces `mycodewiki` by separating concerns cleanly:

- offline deterministic analysis becomes the core
- domain-organized MCP tools become the main interface
- workflow skills drive analysis behavior
- typed document specs and renderers produce final Markdown artifacts
- the old repository becomes a mining site and verification baseline rather than a compatibility target
