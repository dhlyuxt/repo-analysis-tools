# M0 Old Repository Harvest Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Produce the authoritative M0 migration baseline by inventorying the old `mycodewiki` repository, remapping retained capabilities into the new domain model, classifying every major old module, and nominating long-lived fixture repositories without writing any new platform implementation.

**Architecture:** Work from the old repository's visible surfaces inward. First harvest the concrete capability surface from the old README, runtime tool registry, package directories, tests, builds, and example repositories; then normalize that evidence into three durable migration documents. Treat this plan as an execution aid only: M0 acceptance still depends on the three migration documents, not on this plan file itself.

**Tech Stack:** Markdown, PowerShell, `rg`, the old `mycodewiki` repository at `d:/workspace/python/aiagent/mycodewiki`, and the design documents in `docs/superpowers/specs/`.

---

## File Structure

- Create: `migration/old-repo-inventory.md`
  Responsibility: authoritative inventory of old package families, visible capability surfaces, test and fixture assets, example repositories, and legacy runtime assumptions. Each major row must identify concrete source paths, supporting tests, mapped domain, and final disposition.
- Create: `migration/capability-mapping.md`
  Responsibility: explicit remapping from the old repository into the new domains `scan`, `scope`, `anchors`, `slice`, `evidence`, `impact`, `report`, and `export`, including which old shells decompose across domains instead of surviving intact.
- Create: `migration/keep-drop-rewrite.md`
  Responsibility: final disposition matrix assigning each major module or asset to exactly one class, plus written rationale, preserved baselines, selected fixture repositories, and the M1 handoff baseline.

## Working Set

- New-repo parent design: `docs/superpowers/specs/2026-04-17-repo-analysis-platform-design.md`
- New-repo M0 spec: `docs/superpowers/specs/2026-04-17-m0-old-repo-harvest-spec.md`
- New-repo review notes: `docs/gpt5.4proreview.md`
- Old repo root: `d:/workspace/python/aiagent/mycodewiki`
- Old repo README surface: `d:/workspace/python/aiagent/mycodewiki/docs/README.md`
- Old runtime registry: `d:/workspace/python/aiagent/mycodewiki/codewiki/agent_runtime/tools/registry.py`
- Old package roots: `d:/workspace/python/aiagent/mycodewiki/codewiki/*`
- Old test roots: `d:/workspace/python/aiagent/mycodewiki/tests/*`
- Old real-repo candidates: `d:/workspace/python/aiagent/mycodewiki/EasyFlash-master`, `d:/workspace/python/aiagent/mycodewiki/builds/easyflash-e2e-clean/easyflash`

### Task 1: Build the Old-Repo Inventory Baseline

**Files:**
- Create: `migration/old-repo-inventory.md`
- Inspect: `d:/workspace/python/aiagent/mycodewiki/docs/README.md`
- Inspect: `d:/workspace/python/aiagent/mycodewiki/codewiki/agent_runtime/tools/registry.py`
- Inspect: `d:/workspace/python/aiagent/mycodewiki/codewiki/scan/service.py`
- Inspect: `d:/workspace/python/aiagent/mycodewiki/codewiki/scope/service.py`
- Inspect: `d:/workspace/python/aiagent/mycodewiki/codewiki/anchors/service.py`
- Inspect: `d:/workspace/python/aiagent/mycodewiki/codewiki/slices/planner.py`
- Inspect: `d:/workspace/python/aiagent/mycodewiki/codewiki/evidence/builder.py`
- Inspect: `d:/workspace/python/aiagent/mycodewiki/codewiki/retrieval/service.py`
- Inspect: `d:/workspace/python/aiagent/mycodewiki/codewiki/impact/service.py`
- Inspect: `d:/workspace/python/aiagent/mycodewiki/codewiki/reporting/service.py`
- Inspect: `d:/workspace/python/aiagent/mycodewiki/tests/fixtures/scope_first_repo.py`
- Inspect: `d:/workspace/python/aiagent/mycodewiki/tests/test_pipeline/test_scope_first_pipeline.py`

- [ ] **Step 1: Create the inventory document and seed it with the harvest ledger**

```md
# Old Repo Inventory

## Inputs
- Parent design spec: `docs/superpowers/specs/2026-04-17-repo-analysis-platform-design.md`
- M0 spec: `docs/superpowers/specs/2026-04-17-m0-old-repo-harvest-spec.md`
- Old repo root: `d:/workspace/python/aiagent/mycodewiki`
- Secondary review reference: `docs/gpt5.4proreview.md`

## Visible Capability Surfaces
| Surface | Evidence | Notes |
| --- | --- | --- |
| Runtime tool registry | `codewiki/agent_runtime/tools/registry.py` | Exposes `scan_repo`, `plan_slice`, `expand_slice`, `read_evidence_pack`, `get_repo_freshness`, `impact_from_paths`, `render_focus_report`, and `open_span`. |
| README command surface | `docs/README.md` | Exposes `scan`, `scope show`, `ask`, `impact`, `report`, and `bundle`; still documents `.claude/codewiki/index.db` as the runtime location. |
| Scope-first pipeline | `tests/test_pipeline/test_scope_first_pipeline.py` | Confirms the old mainline is still `scan -> ask -> impact -> report`. |

## Capability Inventory
| Area | Source paths | Key entrypoints | Supporting tests | Deterministic offline | Mapped domain | Disposition | Current role |
| --- | --- | --- | --- | --- | --- | --- | --- |
| scan core | `codewiki/scan/*` | `ScanService.scan` | `tests/test_scan/test_service.py`, `tests/test_scan/test_storage.py` | yes | `scan` | `migrate and reorganize` | Builds scan metadata, records provenance, and publishes the active scan. |
| scope core | `codewiki/scope/*` | `ScopeService.classify` | `tests/test_scope/*`, `tests/test_pipeline/test_scope_first_pipeline.py` | yes | `scope` | `migrate and reorganize` | Classifies file roles and drives scan inclusion. |
| anchor extraction | `codewiki/anchors/*`, `codewiki/infrastructure/treesitter/*`, `codewiki/vendor/fsoft_codewiki/*` | `AnchorService.extract_for_paths` | `tests/test_anchors/*` | yes | `anchors` | `migrate and reorganize` | Extracts anchor facts and relations from C and header files. |
| slice planning | `codewiki/slices/*` | `SlicePlanner.plan`, `SlicePlanner.plan_for_change_impact`, `SlicePlanner.expand_manifest` | `tests/test_slices/*` | yes | `slice` | `migrate and reorganize` | Plans and expands bounded analysis slices. |
| evidence builder | `codewiki/evidence/*` | `ContextPackBuilder.for_repo(...).build` | `tests/test_evidence/*` | yes | `evidence` | `migrate and reorganize` | Builds evidence packs and renders evidence-oriented sections. |
| retrieval guards | `codewiki/retrieval/service.py`, `codewiki/retrieval/freshness.py`, `codewiki/retrieval/snippets.py` | `RetrievalService.build_evidence_pack`, `evaluate_retrieval_freshness`, `read_snippet` | `tests/test_retrieval/*` | yes | `evidence` | `extract logic, rewrite shell` | Holds freshness checks and bounded raw-span reads that belong under the new evidence layer, not a standalone retrieval domain. |
| impact analysis | `codewiki/impact/service.py` | `ImpactAnalysisService.analyze` | `tests/test_impact/test_service.py` | yes | `impact` | `migrate and reorganize` | Computes conservative change impact from changed files and stored relations. |
| reporting shell | `codewiki/reporting/service.py`, `codewiki/evidence/renderers.py` | `ReportingService.render_focus_report`, `ReportingService.export` | `tests/test_reporting/test_service.py` | yes | `report`, `export` | `extract logic, rewrite shell` | Renders focused Markdown outputs, but the old focus-report shell and output path should not survive intact. |
| storage layer | `codewiki/storage/*`, `codewiki/scan/storage.py`, `codewiki/anchors/storage.py` | repo, session, slice, trace, and scan storage helpers | `tests/test_storage/*`, `tests/test_scan/test_storage.py`, `tests/test_anchors/test_storage.py` | yes | `scan`, `slice`, `evidence`, `impact`, `report` | `migrate and reorganize` | Persists scan state, slice runs, evidence packs, traces, and session artifacts. |
| indexing wrapper | `codewiki/indexing/service.py` | `IndexingService.build_full_index`, `IndexingService.load_or_build` | `tests/test_scan/*`, `tests/test_pipeline/test_scope_first_pipeline.py` | yes | `scan` | `extract logic, rewrite shell` | Thin compatibility wrapper over scan lifecycle; keep behavior notes, not the package boundary. |
| runtime shell | `codewiki/agent_runtime/*` | `RuntimeToolRegistry`, orchestrator, hooks, budgets, permissions | `tests/test_agent_runtime/*` | mixed | none | `drop` | Old chat/runtime wrapper around reusable analysis logic. |
| ask and answer shell | `codewiki/ask/*`, `codewiki/answers/*` | `AskService.answer`, answer contract models/rendering | `tests/test_ask/*`, `tests/test_answers/*` | mixed | none | `drop` | User-facing answer shell layered on slice and evidence. |
| legacy compatibility surface | `codewiki/cli/*`, `codewiki/demo/*`, `codewiki/benchmarks/*` | `python -m codewiki ...`, demo export, golden replay | `tests/test_cli/*`, `tests/test_benchmarks/*`, `tests/test_pipeline/test_demo_export.py` | mixed | none | `drop` | Legacy CLI, demo wrappers, and benchmark shells kept only as historical references. |
| synthetic baseline fixture | `tests/fixtures/scope_first_repo.py` | `build_scope_first_repo` | reused across scan, slices, evidence, impact, reporting, storage, and CLI tests | yes | baseline only | `test-only baseline` | Deterministic synthetic repository for unit and integration coverage. |
| real fixture candidates | `EasyFlash-master/`, `builds/easyflash-e2e-clean/easyflash/` | real repository trees | current e2e/demo references and manual scan/report targets | yes | baseline only | `test-only baseline` | Real C repositories or snapshots available for long-lived validation. |

## Fixtures and Example Repositories
| Asset | Path | Type | Why it matters |
| --- | --- | --- | --- |
| Scope-first synthetic repo | `tests/fixtures/scope_first_repo.py` | synthetic fixture builder | Stable unit and integration baseline for scope, slices, evidence, impact, and reporting. |
| EasyFlash working repo | `EasyFlash-master/` | real C repository | Best current primary candidate for long-lived real-repo validation. |
| easyflash clean snapshot | `builds/easyflash-e2e-clean/easyflash/` | real-repo snapshot | Good regression baseline for e2e export/demo flows, but likely too close to the primary EasyFlash checkout to count as a distinct long-term fixture. |
| easyflash demo snapshot | `builds/easyflash-e2e-demo/demo/` | demo output fixture | Useful for harvesting example outputs, not a primary long-lived repository fixture. |

## Legacy Assumptions That Must Not Survive
- `docs/README.md` still documents `.claude/codewiki/index.db`; M0 must mark this as legacy and not inherit it into the new repository.
- The old runtime tool registry already exposes domain-shaped surfaces; M0 should harvest those tool boundaries as evidence for the new MCP API instead of preserving the old chat runtime.
```

- [ ] **Step 2: Run the source inventory commands and verify that the seeded ledger matches the old repo**

Run:
- `Get-ChildItem -Name 'd:/workspace/python/aiagent/mycodewiki/codewiki'`
- `Get-ChildItem -Name 'd:/workspace/python/aiagent/mycodewiki/tests'`
- `rg -n "mcp__codewiki__" 'd:/workspace/python/aiagent/mycodewiki/codewiki/agent_runtime/tools/registry.py'`
- `rg -n "scan|scope|ask|impact|report|bundle|\\.claude/codewiki/index.db" 'd:/workspace/python/aiagent/mycodewiki/docs/README.md'`

Expected:
- The package list includes `agent_runtime`, `anchors`, `answers`, `ask`, `evidence`, `impact`, `indexing`, `reporting`, `retrieval`, `scan`, `scope`, `slices`, `storage`, and `vendor`.
- The test list includes `test_agent_runtime`, `test_anchors`, `test_answers`, `test_ask`, `test_cli`, `test_evidence`, `test_impact`, `test_pipeline`, `test_reporting`, `test_retrieval`, `test_scan`, `test_scope`, `test_slices`, and `test_storage`.
- The runtime registry lists the domain-shaped tools already called out in the `Visible Capability Surfaces` section.
- The README still shows legacy CLI surfaces and the `.claude/codewiki/index.db` runtime path.

- [ ] **Step 3: Confirm fixture reuse and surface reach with targeted code searches**

Run:
- `rg -n "build_scope_first_repo" 'd:/workspace/python/aiagent/mycodewiki/tests'`
- `rg -n "EasyFlash|easyflash-e2e-clean|easyflash-e2e-demo" 'd:/workspace/python/aiagent/mycodewiki'`
- `rg -n "plan_slice|impact_from_paths|render_focus_report|open_span" 'd:/workspace/python/aiagent/mycodewiki/codewiki' 'd:/workspace/python/aiagent/mycodewiki/tests'`

Expected:
- `build_scope_first_repo` appears across many unit and integration tests, confirming it is a long-lived synthetic baseline fixture.
- `EasyFlash` or the e2e/demo snapshots appear somewhere in the old repo's docs, builds, or scripts, confirming they belong in the fixture inventory even if they are not referenced by every current test module.
- Tool-surface names such as `plan_slice`, `impact_from_paths`, `render_focus_report`, and `open_span` are visible in the old runtime surface and any related tests, reinforcing that the runtime registry is a useful migration signal even though the runtime code is not a migration target.

- [ ] **Step 4: Commit the inventory baseline**

```bash
git add migration/old-repo-inventory.md
git commit -m "docs: add M0 old repo inventory baseline"
```

### Task 2: Map Old Capabilities into the New Domain Model

**Files:**
- Create: `migration/capability-mapping.md`
- Read: `migration/old-repo-inventory.md`
- Read: `docs/superpowers/specs/2026-04-17-repo-analysis-platform-design.md`
- Read: `docs/superpowers/specs/2026-04-17-m0-old-repo-harvest-spec.md`

- [ ] **Step 1: Create the capability-mapping document with one section per required new domain**

```md
# Capability Mapping

## scan
| Old source | Carry forward | New contract direction |
| --- | --- | --- |
| `codewiki/scan/service.py` | scan orchestration, git provenance capture, and scan publication | `scan_repo`, `refresh_scan`, `get_scan_status` |
| `codewiki/scan/storage.py` | scan refs, query traces, and scan metadata | storage support for scan handles and freshness |
| `codewiki/indexing/service.py` | compatibility wrapper semantics only | fold into `scan`; do not preserve `indexing` as a top-level package |

## scope
| Old source | Carry forward | New contract direction |
| --- | --- | --- |
| `codewiki/scope/service.py` | file discovery and role classification heuristics | `show_scope`, `list_scope_nodes`, `explain_scope_node` |
| `codewiki/scope/config.py` | include, exclude, and focus-root loading | scope configuration contracts under `.codewiki/` |

## anchors
| Old source | Carry forward | New contract direction |
| --- | --- | --- |
| `codewiki/anchors/service.py` | anchor extraction for selected paths | `list_anchors`, `find_anchor`, `describe_anchor` |
| `codewiki/anchors/adapter.py`, `codewiki/anchors/models.py` | normalized anchor facts and relationships | typed anchor payloads in the new core |
| `codewiki/infrastructure/treesitter/*`, `codewiki/vendor/fsoft_codewiki/*` | C parsing and vendored relation analysis | retained deterministic extraction support, reorganized under new boundaries |

## slice
| Old source | Carry forward | New contract direction |
| --- | --- | --- |
| `codewiki/slices/planner.py` | query-to-slice planning | `plan_slice` |
| `codewiki/slices/expansion/*` | bounded slice growth and budgeted expansion | `expand_slice`, `inspect_slice` |
| `codewiki/slices/seed_resolver*.py`, `codewiki/slices/query_classifier.py` | question normalization and seed resolution | slice seeding logic, not a user-facing shell |

## evidence
| Old source | Carry forward | New contract direction |
| --- | --- | --- |
| `codewiki/evidence/builder.py`, `codewiki/evidence/models.py` | evidence-pack construction and typed evidence payloads | `build_evidence_pack`, `read_evidence_pack` |
| `codewiki/evidence/citations.py`, `codewiki/evidence/renderers.py` | citation formatting and evidence summaries | evidence-pack presentation helpers under the report/evidence layers |
| `codewiki/retrieval/freshness.py`, `codewiki/retrieval/service.py`, `codewiki/retrieval/snippets.py` | freshness guards and bounded span reads | `open_span` guardrails and evidence freshness checks after shell rewrite |

## impact
| Old source | Carry forward | New contract direction |
| --- | --- | --- |
| `codewiki/impact/service.py` | conservative change-impact reasoning from changed files and stored relations | `impact_from_paths`, `impact_from_anchor`, `summarize_impact` |
| `codewiki/slices/planner.py::plan_for_change_impact` | change-seeded slice planning | impact workflow support logic |

## report
| Old source | Carry forward | New contract direction |
| --- | --- | --- |
| `codewiki/reporting/service.py::render_context_pack` | structured report rendering from evidence-backed packs | `render_focus_report`, `render_module_summary`, `render_analysis_outline` |
| `codewiki/evidence/renderers.py` | Markdown section rendering helpers | report renderer internals, not a top-level legacy package |

## export
| Old source | Carry forward | New contract direction |
| --- | --- | --- |
| `codewiki/reporting/service.py::export` | controlled write path for rendered analysis output | `export_analysis_bundle`, `export_scope_snapshot`, `export_evidence_bundle` after path-policy rewrite |
| `codewiki/cli/bundle.py`, `codewiki/demo/export.py` | output-shape and bundle UX ideas only | export concepts, not legacy CLI compatibility |

## Explicit Non-Mappings
- `codewiki/agent_runtime/*` is not a new domain. Keep its tool boundaries and safety observations as documentation input only.
- `codewiki/ask/*` and `codewiki/answers/*` decompose across `slice`, `evidence`, and `report`; they do not survive as a top-level `ask` product surface.
- `codewiki/cli/*` is not a target architecture layer. Only reuse output or contract ideas where they strengthen the MCP-first design.
```

- [ ] **Step 2: Reconcile the mapping document with the seeded inventory rows**

Run:
- `rg -n "^\\| .* \\| .* \\| .* \\| .* \\| .* \\| .* \\| .* \\| .* \\|$" migration/old-repo-inventory.md`
- `rg -n "^## (scan|scope|anchors|slice|evidence|impact|report|export)$" migration/capability-mapping.md`

Expected:
- The inventory already contains the major row families that need mapping.
- The mapping document contains exactly the eight required domain sections from the M0 spec.

- [ ] **Step 3: Add a short cross-domain note for shells that decompose instead of migrating intact**

```md
## Cross-Domain Decomposition Notes
- `AskService` currently wraps slice planning, evidence building, and conservative answer summarization. Preserve the underlying slice and evidence logic, but drop the top-level ask shell.
- The old runtime registry is a good source of tool boundaries and safety guardrails, but the new repository is not a chat runtime.
- Legacy CLI commands and demo exports can inform MCP tool naming or export expectations, but they do not survive as compatibility surfaces.
```

- [ ] **Step 4: Commit the domain mapping baseline**

```bash
git add migration/capability-mapping.md migration/old-repo-inventory.md
git commit -m "docs: map old repo capabilities into new domains"
```

### Task 3: Produce the Keep/Drop/Rewrite Decision Baseline

**Files:**
- Create: `migration/keep-drop-rewrite.md`
- Read: `migration/old-repo-inventory.md`
- Read: `migration/capability-mapping.md`
- Read: `docs/gpt5.4proreview.md`

- [ ] **Step 1: Create the disposition document with explicit rules and a single-class matrix**

```md
# Keep, Drop, Rewrite

## Decision Rules
- Favor deterministic offline analysis logic.
- Disfavor prompt orchestration, agent runtime code, and compatibility shells.
- Preserve test assets when they capture long-lived behavior, even if their production implementation is dropped.
- Do not preserve old package boundaries by habit.

## Disposition Matrix
| Item | Class | Evidence | Rationale | Preserve as baseline |
| --- | --- | --- | --- | --- |
| `codewiki/scan/*` | `migrate and reorganize` | `codewiki/scan/service.py`, `tests/test_scan/*` | Core deterministic scan lifecycle and provenance capture belong in the new offline analysis core. | `tests/test_scan/*` |
| `codewiki/scope/*` | `migrate and reorganize` | `codewiki/scope/service.py`, `tests/test_scope/*` | Scope classification is part of the new first-class domain model. | `tests/test_scope/*` |
| `codewiki/anchors/*` | `migrate and reorganize` | `codewiki/anchors/service.py`, `tests/test_anchors/*` | Anchor extraction is a direct fit for the `anchors` domain. | `tests/test_anchors/*` |
| `codewiki/infrastructure/treesitter/*` | `migrate and reorganize` | parser and extractor helpers under `codewiki/infrastructure/treesitter/*` | Deterministic C parsing support should move under the new analysis core. | old parser smoke behavior only if needed |
| `codewiki/vendor/fsoft_codewiki/*` | `migrate and reorganize` | vendored dependency analyzer code | Vendored C-analysis logic is explicitly called out as a selective keep area. | vendor provenance notes |
| `codewiki/slices/*` | `migrate and reorganize` | `codewiki/slices/planner.py`, `tests/test_slices/*` | Query-time slice planning is central to the new analysis workflow. | `tests/test_slices/*` |
| `codewiki/evidence/*` | `migrate and reorganize` | `codewiki/evidence/*`, `tests/test_evidence/*` | Evidence-pack construction and citation handling are core reusable logic. | `tests/test_evidence/*` |
| `codewiki/impact/service.py` | `migrate and reorganize` | `codewiki/impact/service.py`, `tests/test_impact/test_service.py` | Change-impact analysis is a planned first-class domain. | `tests/test_impact/test_service.py` |
| `codewiki/storage/*`, `codewiki/scan/storage.py`, `codewiki/anchors/storage.py` | `migrate and reorganize` | storage helpers and stores | Persistent scan, slice, evidence, and trace state belong in the new storage layer after reorganization. | `tests/test_storage/*`, related storage tests |
| `codewiki/indexing/service.py` | `extract logic, rewrite shell` | `codewiki/indexing/service.py` | Current package is a compatibility wrapper over scan behavior; keep semantics, not the package surface. | scan-related tests only |
| `codewiki/retrieval/*` | `extract logic, rewrite shell` | `codewiki/retrieval/service.py`, `tests/test_retrieval/*` | Freshness checks and bounded snippet reads should survive under `evidence`, but the retrieval-centric shell should not. | `tests/test_retrieval/*` |
| `codewiki/reporting/service.py` | `extract logic, rewrite shell` | `codewiki/reporting/service.py`, `tests/test_reporting/test_service.py` | Report rendering survives, but the old focus-report shell and `docs/codewiki/` output convention do not. | `tests/test_reporting/test_service.py` |
| `tests/fixtures/scope_first_repo.py` | `test-only baseline` | synthetic fixture builder reused across many tests | Preserve as a deterministic synthetic repository for later contract and integration tests. | yes |
| `EasyFlash-master/` | `test-only baseline` | real C repository checked into the old repo | Primary real-repo fixture candidate for later phases. | yes |
| `builds/easyflash-e2e-clean/easyflash/` | `test-only baseline` | e2e-clean snapshot of EasyFlash | Useful regression fixture, but likely not distinct enough to count as a second architectural source of truth. | yes |
| `codewiki/agent_runtime/*` | `drop` | runtime orchestration, tool policies, Claude client integration | New repository is not a chat application or agent runtime. | only behavioral notes when useful |
| `codewiki/ask/*`, `codewiki/answers/*` | `drop` | answer shell and answer-contract rendering | New repository uses workflow skills and structured facts, not a top-level ask product surface. | historical reference only |
| `codewiki/cli/*`, `codewiki/demo/*`, `codewiki/benchmarks/*` | `drop` | CLI compatibility commands, demo wrappers, and benchmark shells | Zero compatibility policy means these stay out of the new mainline. | historical reference only |

## Fixture Nominations
- Primary real-repo fixture: `d:/workspace/python/aiagent/mycodewiki/EasyFlash-master`
- Secondary regression snapshot: `d:/workspace/python/aiagent/mycodewiki/builds/easyflash-e2e-clean/easyflash`
- Synthetic baseline fixture: `d:/workspace/python/aiagent/mycodewiki/tests/fixtures/scope_first_repo.py`

## Notes for M1
- `.claude/codewiki/index.db` is a legacy runtime location and must not carry forward.
- The new repository inherits domain boundaries, deterministic logic, and test baselines, not the old chat/runtime shell.
```

- [ ] **Step 2: Verify that every major package family and baseline asset appears exactly once in the decision matrix**

Run:
- `rg -n "codewiki/(scan|scope|anchors|infrastructure/treesitter|vendor/fsoft_codewiki|slices|evidence|impact|storage|indexing|retrieval|reporting|agent_runtime|ask|answers|cli|demo|benchmarks)" migration/keep-drop-rewrite.md`
- `rg -n "EasyFlash-master|easyflash-e2e-clean/easyflash|scope_first_repo.py" migration/keep-drop-rewrite.md`

Expected:
- Each major old package family appears in the matrix with a single disposition.
- The real and synthetic fixture baselines are recorded explicitly.

- [ ] **Step 3: Add written rationale for the highest-risk drops and rewrites**

```md
## High-Risk Calls
- `agent_runtime`: drop because it would reintroduce the exact chat/runtime architecture the new repository explicitly rejects.
- `ask` and `answers`: drop because they hide durable logic behind a legacy answer shell; keep the underlying slice and evidence logic instead.
- `retrieval` and `reporting`: extract the durable freshness, snippet, and rendering logic, then rewrite the surrounding shell to fit the new domain-first MCP surface.
```

- [ ] **Step 4: Commit the disposition baseline**

```bash
git add migration/keep-drop-rewrite.md migration/capability-mapping.md migration/old-repo-inventory.md
git commit -m "docs: record M0 keep-drop-rewrite baseline"
```

### Task 4: Cross-Check Acceptance and Publish the M1 Handoff Baseline

**Files:**
- Modify: `migration/old-repo-inventory.md`
- Modify: `migration/capability-mapping.md`
- Modify: `migration/keep-drop-rewrite.md`

- [ ] **Step 1: Add the final M1 handoff section to the disposition document**

```md
## M1 Handoff Baseline
- Accepted inventory source of truth: `migration/old-repo-inventory.md`
- Accepted domain mapping source of truth: `migration/capability-mapping.md`
- Accepted disposition source of truth: `migration/keep-drop-rewrite.md`
- Accepted real-repo fixture baseline: `d:/workspace/python/aiagent/mycodewiki/EasyFlash-master`
- Accepted synthetic baseline fixture: `d:/workspace/python/aiagent/mycodewiki/tests/fixtures/scope_first_repo.py`
- Optional regression snapshot: `d:/workspace/python/aiagent/mycodewiki/builds/easyflash-e2e-clean/easyflash`
- Explicit non-goals handed to M1: legacy CLI compatibility, `agent_runtime`, `ask`, `answers`, and the `.claude/codewiki/` runtime layout
```

- [ ] **Step 2: Run the acceptance cross-check commands**

Run:
- `rg -n "^## " migration`
- `rg -n "^## (scan|scope|anchors|slice|evidence|impact|report|export)$" migration/capability-mapping.md`
- `rg -n "migrate and reorganize|extract logic, rewrite shell|test-only baseline|drop" migration/keep-drop-rewrite.md`
- `rg -n "Mapped domain|Disposition|Legacy Assumptions That Must Not Survive" migration/old-repo-inventory.md`

Expected:
- All three migration documents exist and have clearly named sections.
- `migration/capability-mapping.md` contains the eight required new-domain sections.
- `migration/keep-drop-rewrite.md` uses only the four approved decision classes.
- `migration/old-repo-inventory.md` explicitly records both the mapped domain and the final disposition for each major row, plus the legacy assumptions that must not survive.

- [ ] **Step 3: Perform a manual spec-coverage review before declaring M0 complete**

Review checklist:
- Every major old offline capability is present in `migration/old-repo-inventory.md`.
- Every inventoried item has a disposition in `migration/keep-drop-rewrite.md`.
- The new domain mapping is explicit in `migration/capability-mapping.md`.
- Fixture candidates are recorded and at least one real C repository is accepted.
- No unresolved question in the three documents blocks M1 package design.

- [ ] **Step 4: Commit the final accepted migration baseline**

```bash
git add migration/old-repo-inventory.md migration/capability-mapping.md migration/keep-drop-rewrite.md
git commit -m "docs: finalize M0 migration baseline"
```
