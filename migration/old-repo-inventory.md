# Old Repo Inventory

## Inputs

- Primary evidence repo: `D:/workspace/python/aiagent/mycodewiki`
- Parent design spec: `docs/superpowers/specs/2026-04-17-repo-analysis-platform-design.md`
- M0 harvest spec: `docs/superpowers/specs/2026-04-17-m0-old-repo-harvest-spec.md`
- Secondary review note: `docs/gpt5.4proreview.md`
- Old-repo sources inspected for this baseline:
  - `docs/README.md`
  - `AGENTS.md`
  - `codewiki/agent_runtime/tools/registry.py`
  - `codewiki/agent_runtime/orchestrator.py`
  - `codewiki/agent_runtime/session_manager.py`
  - `codewiki/scan/service.py`
  - `codewiki/scan/models.py`
  - `codewiki/scan/storage.py`
  - `codewiki/scope/service.py`
  - `codewiki/scope/config.py`
  - `codewiki/anchors/service.py`
  - `codewiki/anchors/adapter.py`
  - `codewiki/slices/planner.py`
  - `codewiki/slices/classifier_v2.py`
  - `codewiki/slices/seed_resolver_v2.py`
  - `codewiki/evidence/builder.py`
  - `codewiki/evidence/citations.py`
  - `codewiki/evidence/models.py`
  - `codewiki/evidence/renderers.py`
  - `codewiki/retrieval/service.py`
  - `codewiki/retrieval/freshness.py`
  - `codewiki/retrieval/snippets.py`
  - `codewiki/impact/service.py`
  - `codewiki/reporting/service.py`
  - `codewiki/ask/service.py`
  - `codewiki/answers/models.py`
  - `codewiki/indexing/service.py`
  - `codewiki/storage/repo_store.py`
  - `codewiki/storage/slice_store.py`
  - `codewiki/storage/session_store.py`
  - `codewiki/storage/trace_store.py`
  - `codewiki/storage/migrations.py`
  - `testscript/test_partition.py`
  - `builds/easyflash-e2e-artifacts/manifest.json`
  - `builds/easyflash-e2e-clean/README.md`
  - `builds/easyflash-e2e-demo/README.md`
  - `tests/fixtures/scope_first_repo.py`
  - `tests/test_agent_runtime/test_registry.py`
  - `tests/test_anchors/test_service.py`
  - `tests/test_ask/test_service.py`
  - `tests/test_cli/test_main.py`
  - `tests/test_evidence/test_builder.py`
  - `tests/test_impact/test_service.py`
  - `tests/test_pipeline/test_scope_first_pipeline.py`
  - `tests/test_reporting/test_service.py`
  - `tests/test_retrieval/test_service.py`
  - `tests/test_scan/test_service.py`
  - `tests/test_scope/test_service.py`
  - `tests/test_slices/test_planner.py`
  - `tests/test_storage/test_repo_store.py`
- Required verification commands for this document:
  - `Get-ChildItem -Name 'd:/workspace/python/aiagent/mycodewiki/codewiki'`
  - `Get-ChildItem -Name 'd:/workspace/python/aiagent/mycodewiki/tests'`
  - `rg -n "mcp__codewiki__" 'd:/workspace/python/aiagent/mycodewiki/codewiki/agent_runtime/tools/registry.py'`
  - `rg -n "scan|scope|ask|impact|report|bundle|\.claude/codewiki/index.db" 'd:/workspace/python/aiagent/mycodewiki/docs/README.md'`
  - `rg -n "build_scope_first_repo" 'd:/workspace/python/aiagent/mycodewiki/tests'`
  - `rg -n "EasyFlash|easyflash-e2e-clean|easyflash-e2e-demo" 'd:/workspace/python/aiagent/mycodewiki'`
  - `rg -n "plan_slice|impact_from_paths|render_focus_report|open_span" 'd:/workspace/python/aiagent/mycodewiki/codewiki' 'd:/workspace/python/aiagent/mycodewiki/tests'`

## Harvest Ledger

| Area | Legacy surface | Evidence | Mapped domain | Initial disposition | Notes |
| --- | --- | --- | --- | --- | --- |
| Scope-first mainline | `scan`, `scope`, `anchors`, `slices`, `evidence`, `impact`, `reporting` | README workflow plus service modules | `scan`, `scope`, `anchors`, `slice`, `evidence`, `impact`, `report` | migrate and reorganize | Deterministic offline core worth harvesting. |
| Runtime wrapper | `agent_runtime/tools/registry.py` | MCP-style tool names and guarded `open_span` | MCP shell, later domain tool contracts | extract logic, rewrite shell | Tool boundary names are useful; chat session shell is not. |
| Ask and answer flow | `ask/service.py`, `answers/models.py` | Scope-first Q&A contract built from slices/evidence | workflow shell over `slice` + `evidence` | extract logic, rewrite shell | Keep answer contract ideas, drop old CLI/chat framing. |
| Storage and traces | `storage/*.py`, `scan/storage.py` | SQLite-backed scan, slice, evidence, session, trace persistence | cross-cutting storage support layer plus asset handles | migrate and reorganize | Keep durable asset-persistence/schema ideas, move runtime root to `.codewiki/`, and do not carry forward runtime session/trace telemetry persistence by default. |
| Compatibility layer | `indexing/service.py`, CLI `index/analyze/export/bundle` aliases | README deprecation note and indexing wrapper | none | drop | Compatibility commands must not survive. |
| Fixtures | `tests/fixtures/scope_first_repo.py`, pipeline tests, real repo references | Synthetic repo builder plus EasyFlash references | fixtures / golden baselines | test-only baseline | Preserve for later contract and e2e validation. |

## Visible Capability Surfaces

- README advertises a scope-first workflow: `scan`, `scope show`, `ask`, `impact`, `report`, and `bundle`, with `index`, `analyze`, and `export` left as compatibility commands.
- Runtime tool registry exposes eight MCP-style operations: `scan_repo`, `plan_slice`, `expand_slice`, `read_evidence_pack`, `get_repo_freshness`, `impact_from_paths`, `render_focus_report`, and guarded `open_span`.
- The offline core is already separated into domain-ish packages: `scan`, `scope`, `anchors`, `slices`, `evidence`, `retrieval`, `impact`, and `reporting`, with `storage` acting as a cross-cutting support layer rather than a ninth analysis domain.
- The test tree mirrors those surfaces with dedicated suites for `agent_runtime`, `ask`, `anchors`, `evidence`, `impact`, `retrieval`, `scan`, `scope`, `slices`, `storage`, `reporting`, CLI, and pipeline coverage.
- The old runtime root is hard-coded to `<repo>/.claude/codewiki/index.db` via `codewiki/scan/models.py`, which conflicts with the new neutral `.codewiki/` runtime rule.
- Tests already encode the intended scope-first golden path: build repo fixture, run scan, answer a locate-symbol question, compute impact, and export a report.

## Capability Inventory

| Capability | Concrete source paths | Key entrypoints | Supporting tests | Deterministic offline logic | Mapped domain | Disposition | Current role |
| --- | --- | --- | --- | --- | --- | --- | --- |
| scan core | `codewiki/scan/service.py`, `codewiki/scan/storage.py`, `codewiki/scan/models.py` | `ScanService.scan`, `ScanStorage.record_scan`, `ScanPaths.for_repo` | `tests/test_scan/test_service.py`, `tests/test_scan/test_storage.py`, `tests/test_pipeline/test_scope_first_pipeline.py` | Yes; filesystem + git provenance only | `scan` | migrate and reorganize | Builds repo-local scan state, persists scan runs, triggers scope and anchor extraction. |
| scope core | `codewiki/scope/service.py`, `codewiki/scope/config.py` | `ScopeService.for_repo`, `ScopeService.classify` | `tests/test_scope/test_service.py`, `tests/test_scope/test_config.py`, `tests/test_cli/test_main.py` | Yes | `scope` | migrate and reorganize | Classifies files into primary/support/external/generated/ignored roles using path and config heuristics. |
| anchor extraction | `codewiki/anchors/service.py`, `codewiki/anchors/adapter.py`, vendored analyzer under `codewiki/vendor/fsoft_codewiki` | `AnchorService.for_repo`, `AnchorService.extract_for_paths` | `tests/test_anchors/test_service.py`, `tests/test_anchors/test_storage.py`, `tests/test_pipeline/test_scope_first_pipeline.py` | Yes, assuming local parser assets | `anchors` | migrate and reorganize | Extracts definitions plus relation anchors and augments them with raw field declarations. |
| slice planning | `codewiki/slices/planner.py`, `codewiki/slices/seed_resolver_v2.py`, `codewiki/slices/classifier_v2.py`, `codewiki/slices/expansion/*` | `SlicePlanner.plan`, `SlicePlanner.plan_for_change_impact`, `SlicePlanner.expand_manifest` | `tests/test_slices/test_planner.py`, `tests/test_slices/test_expansion_recipes.py`, `tests/test_agent_runtime/test_expand_slice_tool.py` | Yes | `slice` | migrate and reorganize | Converts questions or changed paths into bounded manifests of files, spans, notes, and expansion budgets. |
| evidence builder | `codewiki/evidence/builder.py`, `codewiki/evidence/citations.py`, `codewiki/evidence/models.py` | `ContextPackBuilder.build` | `tests/test_evidence/test_builder.py`, `tests/test_reporting/test_service.py`, `tests/test_pipeline/test_scope_first_pipeline.py` | Yes | `evidence` | migrate and reorganize | Turns slice manifests into structured context packs with citations, relations, freshness, and missing slots. |
| retrieval guards | `codewiki/retrieval/service.py`, `codewiki/retrieval/freshness.py`, `codewiki/retrieval/snippets.py` | `RetrievalService.build_evidence_pack`, `evaluate_retrieval_freshness`, `read_snippet` | `tests/test_retrieval/test_service.py`, `tests/test_retrieval/test_freshness.py`, `tests/test_agent_runtime/test_registry.py` | Yes | `evidence` | migrate and reorganize | Enforces scan binding, git freshness, tracked-file checks, and bounded snippet materialization. |
| impact analysis | `codewiki/impact/service.py` | `ImpactAnalysisService.analyze` | `tests/test_impact/test_service.py`, `tests/test_cli/test_main.py`, `tests/test_pipeline/test_scope_first_pipeline.py` | Yes | `impact` | migrate and reorganize | Computes conservative caller impact from changed files using stored call relations and answer contracts. |
| reporting shell | `codewiki/reporting/service.py`, `codewiki/evidence/renderers.py` | `ReportingService.render_focus_report`, `ReportingService.export` | `tests/test_reporting/test_service.py`, `tests/test_cli/test_main.py`, `tests/test_pipeline/test_scope_first_pipeline.py` | Mostly yes; writes markdown output | `report` | extract logic, rewrite shell | Renders focus reports from context packs and writes them under `docs/codewiki/`. |
| storage layer | `codewiki/storage/repo_store.py`, `codewiki/storage/slice_store.py`, `codewiki/storage/session_store.py`, `codewiki/storage/trace_store.py`, `codewiki/storage/migrations.py` | `RepoStore.for_repo`, `SliceStore.record_slice_run`, `SessionStore.record_tool_event` | `tests/test_storage/test_repo_store.py`, `tests/test_storage/test_slice_store.py`, `tests/test_storage/test_session_store.py`, `tests/test_storage/test_trace_store.py` | Yes | cross-cutting storage support layer | migrate and reorganize | Owns SQLite schema, latest views, and durable asset persistence used by the analysis domains; runtime session telemetry and trace linkage do not carry forward by default. |
| indexing wrapper | `codewiki/indexing/service.py`, `codewiki/cli/main.py` | `IndexingService.build_full_index`, CLI `index` handler | `tests/test_cli/test_main.py` | Yes, but only as alias | none | drop | Thin compatibility wrapper forwarding legacy `index` behavior to `scan`. |
| runtime shell | `codewiki/agent_runtime/tools/registry.py`, `codewiki/agent_runtime/orchestrator.py`, `codewiki/agent_runtime/session_manager.py` | `RuntimeToolRegistry.invoke`, per-tool handlers such as `_open_span` | `tests/test_agent_runtime/test_registry.py`, `tests/test_agent_runtime/test_orchestrator.py`, `tests/test_agent_runtime/test_telemetry.py` | Mixed; tool boundaries wrap deterministic core, session/orchestration is runtime-specific | MCP shell | extract logic, rewrite shell | Packages domain services into tool calls, persists session events, and adds guarded read boundaries. |
| ask and answer shell | `codewiki/ask/service.py`, `codewiki/answers/models.py` | `AskService.answer`, `AnswerContract.to_json` | `tests/test_ask/test_service.py`, `tests/test_cli/test_main.py`, `tests/test_pipeline/test_scope_first_pipeline.py` | Yes for current contract build path | workflow shell over `slice` + `evidence` | extract logic, rewrite shell | Converts evidence packs into conservative answer contracts for symbol questions and no-match/unknown cases. |
| legacy compatibility surface | `docs/README.md`, `codewiki/cli/main.py`, `codewiki/indexing/service.py` | README workflow, CLI `index`, `bundle`, deprecated aliases | `tests/test_cli/test_main.py`, `tests/test_pipeline/test_bundle_export.py`, `tests/test_pipeline/test_demo_export.py` | No unique value beyond wrappers | none | drop | Keeps old command names alive during transition and preserves old path assumptions. |
| synthetic baseline fixture | `tests/fixtures/scope_first_repo.py` | `build_scope_first_repo` | `tests/test_pipeline/test_scope_first_pipeline.py`, `tests/test_agent_runtime/test_registry.py`, `tests/test_storage/test_repo_store.py` | Yes | fixtures | test-only baseline | Tiny deterministic C fixture covering primary/support/external/generated roles plus one resolvable symbol. |
| real fixture baselines | `EasyFlash-master`, `builds/easyflash-e2e-clean`, `builds/easyflash-e2e-demo` | `AGENTS.md:29`, `testscript/test_partition.py:22`, `builds/easyflash-e2e-artifacts/manifest.json:3` | `tests/test_pipeline/test_demo_export.py`, `tests/test_pipeline/test_bundle_export.py` | N/A as inventory item | fixtures | test-only baseline | `EasyFlash-master` is the accepted primary real-fixture baseline for M1; `builds/easyflash-e2e-clean` is an optional secondary regression snapshot, and the listed tests are adjacent evidence around fixture handling rather than direct validation of each checked-in tree. |

## Fixtures and Example Repositories

- Synthetic baseline fixture:
  - `tests/fixtures/scope_first_repo.py` creates a minimal C repository with `src`, `ports`, `demo`, and `generated` directories.
  - `tests/test_pipeline/test_scope_first_pipeline.py` proves the current golden path: `scan -> ask -> impact -> report`.
  - `rg -n "build_scope_first_repo" tests` shows broad reuse across storage, slices, retrieval, reporting, CLI, pipeline, and agent runtime suites, so this fixture is already the de facto regression backbone.
  - Reuse value: fast offline contract test for scope classification, anchor extraction, slice planning, and report output.
-- Real fixture baselines:
  - Primary accepted real fixture baseline: `EasyFlash-master`
    Evidence: `AGENTS.md:29` names it as an example C repo, and `testscript/test_partition.py:22` points at `EasyFlash-master/easyflash/src`.
  - Optional regression snapshot: `builds/easyflash-e2e-clean`
    Evidence: `builds/easyflash-e2e-artifacts/manifest.json:3` records this exact repo root, and `builds/easyflash-e2e-clean/README.md` is a concrete checked-in fixture tree.
  - `builds/easyflash-e2e-demo`
    Evidence: `builds/easyflash-e2e-demo/README.md` is a concrete checked-in fixture tree with embedded demo sources under `demo/` and library sources under `easyflash/`.
  - Task 4 accepted handoff: `EasyFlash-master` is the unambiguous primary real-fixture baseline for M1, while `builds/easyflash-e2e-clean` remains an optional secondary regression snapshot.
- Example runtime outputs worth preserving only as baselines:
  - repo-local scan database under `.claude/codewiki/index.db`
  - `docs/codewiki/focus-report.md` report shell output
  - slice/evidence/session tables in SQLite for later migration comparison

## Legacy Assumptions That Must Not Survive

- Runtime state must not remain under `<repo>/.claude/codewiki/`; M1+ should move to neutral `<repo>/.codewiki/`.
- The new platform must not preserve `index`, `analyze`, `export`, or other compatibility command names just because the old CLI exposed them.
- `ask` must not remain a mega-surface that hides slice planning and evidence retrieval behind a chat-style entrypoint.
- Agent runtime orchestration, session replay, and telemetry shells are not the product architecture; only durable domain contracts and guarded tool boundaries survive.
- Report generation should not stay as an ad hoc markdown shell without the new typed document spec / DSL / renderer pipeline.
- Retrieval must keep bounded-read and freshness enforcement, but those guards belong in domain MCP tools, not inside a legacy chat runtime.
- Vendored or parser-heavy anchor extraction can survive only as harvested deterministic logic; old package boundaries and old repository layout must not be copied forward.

## Acceptance Handoff Note

- Task 4 finalization: this document owns the accepted inventory of major old-repo capabilities, fixtures, legacy assumptions, and supporting evidence references for M1.
- M1 should consume this inventory together with `migration/capability-mapping.md` and `migration/keep-drop-rewrite.md`.
- If any final migration decision or handoff-precedence conflict appears across the three documents, `migration/keep-drop-rewrite.md` is the synthesis authority for M1.
