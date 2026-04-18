# Capability Mapping

This document remaps the approved old-repository inventory into the new domain model defined by the 2026-04-17 platform design and M0 harvest specs. It is intentionally domain-first instead of package-first so later keep/drop/rewrite decisions can separate durable offline logic from legacy shells, compatibility surfaces, and chat-oriented orchestration.

## scan

Old sources:
- `codewiki/scan/service.py`, `codewiki/scan/models.py`
- `codewiki/storage/repo_store.py`, `codewiki/storage/migrations.py`
- Runtime exposure via `codewiki/agent_runtime/tools/registry.py: scan_repo`
- Pipeline and scan tests in `tests/test_scan/*`, `tests/test_pipeline/test_scope_first_pipeline.py`

Carry forward:
- Deterministic repository scan logic, including filesystem traversal and git provenance capture
- Persisted scan runs and latest-scan state, as long as ownership stays with the shared storage layer under `<target_repo>/.codewiki/`
- Scan identifiers and freshness hooks that downstream domains can bind to

New contract direction:
- `scan` becomes the base asset-creation domain for `scan_repo`, `refresh_scan`, and `get_scan_status`
- The new contract should return stable scan IDs, normalized repository/runtime paths, freshness notes, and recommended next tools instead of old CLI- or session-shaped payloads
- Scan storage remains reusable infrastructure, but the contract belongs to the domain MCP layer rather than a legacy repo-local CLI shell
- Old visible surface `get_repo_freshness` does not survive as its own top-level domain tool; its freshness checks fold into `evidence` guardrails because they validate whether a scan-bound evidence read is still trustworthy

## scope

Old sources:
- `codewiki/scope/service.py`, `codewiki/scope/config.py`
- Scope-first fixture and tests in `tests/test_scope/*`, `tests/fixtures/scope_first_repo.py`, `tests/test_pipeline/test_scope_first_pipeline.py`
- README workflow and CLI references that surfaced `scope show`

Carry forward:
- File classification heuristics for primary, support, external, generated, and ignored areas
- Config-driven scope behavior that keeps repository structure interpretation deterministic and reviewable
- Fixture-backed expectations for how scope should explain repository layout to downstream consumers

New contract direction:
- `scope` owns read-oriented structure tools such as `show_scope`, `list_scope_nodes`, and `explain_scope_node`
- The new payloads should expose typed nodes and classification rationale, not only formatted shell output
- Scope should consume scan artifacts but remain an independently inspectable domain so workflow skills can distinguish confirmed structure from later interpretation

## anchors

Old sources:
- `codewiki/anchors/service.py`, `codewiki/anchors/adapter.py`
- Parser substrate under `codewiki/infrastructure/treesitter/*`
- Vendored analyzer code under `codewiki/vendor/fsoft_codewiki`
- Anchor tests and pipeline coverage in `tests/test_anchors/*`, `tests/test_pipeline/test_scope_first_pipeline.py`

Carry forward:
- Deterministic extraction of definitions, declarations, relations, and augmented field-level anchor details
- Local parser integration from `codewiki/infrastructure/treesitter/*` and the vendored analyzer family that can run offline against harvested repositories
- Anchor persistence and lookup state stay traceable through `codewiki/anchors/storage.py`, but ownership belongs to the shared storage layer rather than the `anchors` domain row
- Existing test-backed expectations for anchor lookup on the synthetic baseline fixture

New contract direction:
- `anchors` becomes the structural lookup domain behind `list_anchors`, `find_anchor`, and `describe_anchor`
- The new contract should normalize anchor IDs and relation shapes so later slice, impact, and reporting flows can cite anchors consistently
- Vendored parser logic may be harvested, but old package boundaries and adapter shells should be reorganized to fit the new repository layout

## slice

Old sources:
- `codewiki/slices/planner.py`, `codewiki/slices/seed_resolver_v2.py`, `codewiki/slices/classifier_v2.py`, `codewiki/slices/expansion/*`
- Runtime tools `plan_slice` and `expand_slice`
- Tests in `tests/test_slices/*`, `tests/test_agent_runtime/test_expand_slice_tool.py`
- Ask-flow usage via `codewiki/ask/service.py`

Carry forward:
- Slice planning from questions, symbols, and changed paths into bounded manifests
- Expansion recipes, budgets, and manifest inspection logic that keep focused analysis deterministic
- Seed resolution and classification logic that explains why files or spans enter a slice

New contract direction:
- `slice` owns `plan_slice`, `expand_slice`, and `inspect_slice` as first-class domain tools rather than hidden internals of `ask`
- The contract should emphasize stable slice IDs, explicit seeds, bounded regions, and machine-readable notes about why the slice exists
- Slice planning remains reusable for both repository-understanding and change-impact workflows, but the old ask-style top-level shell does not survive intact

## evidence

Old sources:
- `codewiki/evidence/builder.py`, `codewiki/evidence/citations.py`, `codewiki/evidence/models.py`
- `codewiki/retrieval/service.py`, `codewiki/retrieval/freshness.py`, `codewiki/retrieval/snippets.py`
- Guarded runtime `open_span` and old visible surface `get_repo_freshness`
- Tests in `tests/test_evidence/*`, `tests/test_retrieval/*`, `tests/test_agent_runtime/test_registry.py`

Carry forward:
- Context-pack construction from slices into citations, relations, freshness signals, and missing-data slots
- Retrieval guardrails: scan binding, tracked-file checks, `get_repo_freshness`-style freshness evaluation, and bounded snippet reading
- Evidence-backed span access rules that keep detailed code reading constrained and reviewable

New contract direction:
- `evidence` owns `build_evidence_pack`, `read_evidence_pack`, and guarded `open_span`
- The new contract should produce typed evidence-pack assets with stable IDs, citation records, freshness messages, and explicit read-boundary metadata
- `get_repo_freshness` folds into `evidence` instead of surviving as a standalone MCP surface: freshness becomes supporting metadata and validation inside evidence-pack reads and guarded span access
- Retrieval logic is preserved as evidence-domain enforcement, not as a separate user-facing legacy subsystem and not as a chat runtime concern

## impact

Old sources:
- `codewiki/impact/service.py`
- Ask/answer contracts that feed conservative impact reasoning
- CLI and pipeline coverage in `tests/test_impact/test_service.py`, `tests/test_cli/test_main.py`, `tests/test_pipeline/test_scope_first_pipeline.py`

Carry forward:
- Conservative impact analysis over changed files and stored call relations
- Existing reasoning patterns that distinguish direct effects, likely propagation, and uncertainty
- Integration points that let impact consume anchors, slices, and evidence outputs rather than duplicate them

New contract direction:
- `impact` owns `impact_from_paths`, `impact_from_anchor`, and `summarize_impact`
- The contract should emit typed impact assets with affected anchors/modules, risk notes, blind spots, and recommended follow-up inspection steps
- Old answer-shaped reasoning can inform result structure, but impact becomes a change-centered domain instead of a downstream branch of ask/report shells

## report

Old sources:
- `codewiki/reporting/service.py`
- `codewiki/evidence/renderers.py`
- README and CLI surfaces that wrote focus reports under `docs/codewiki/`
- Tests in `tests/test_reporting/test_service.py`, `tests/test_pipeline/test_scope_first_pipeline.py`

Carry forward:
- Report-skeleton assembly that starts from structured evidence instead of free-form prose
- Existing focus-report expectations as golden baseline material for later renderer validation
- Citation-aware rendering helpers where they support typed document outputs

New contract direction:
- `report` owns structured report skeleton generation such as `render_focus_report`, `render_module_summary`, and `render_analysis_outline`
- The new contract should return typed report assets or document-ready skeletons that the future document spec / DSL / renderer pipeline can validate and render
- `ReportingService.export` stays with the legacy report-shell writer path, not the new `export` domain
- Legacy markdown-writing shells and fixed output paths do not survive as compatibility surfaces; report is an upstream structured-facts producer, not the final document system by itself

## export

Old sources:
- `codewiki/cli/bundle.py`, `codewiki/demo/export.py`
- Legacy CLI compatibility surfaces in `codewiki/cli/main.py` and `codewiki/indexing/service.py` for `export` and `bundle`
- Example outputs and manifests under `builds/easyflash-e2e-artifacts/manifest.json`, `builds/easyflash-e2e-clean/`, and `builds/easyflash-e2e-demo/`
- Export-oriented tests in `tests/test_pipeline/test_bundle_export.py` and `tests/test_pipeline/test_demo_export.py`

Carry forward:
- The idea that analysis assets can be packaged for later reuse, comparison, review, or transport
- Manifest-style metadata from demo artifacts that can inform bundle shape and completeness checks
- Legacy export-oriented behavior from `codewiki/cli/bundle.py` and `codewiki/demo/export.py` is the historical seed for the new `export` domain, not for report generation
- Manifest and payload conventions that let exported artifacts refer back to scans, slices, evidence, and report inputs without assuming old storage-backed report/export handles

New contract direction:
- `export` is a new first-class domain for `export_analysis_bundle`, `export_scope_snapshot`, and `export_evidence_bundle`
- The new contract should export typed, reusable analysis assets with stable IDs and manifest metadata rather than preserve old CLI commands or old bundle formats as compatibility commitments
- The dropped legacy CLI `export` and `bundle` compatibility surfaces do not survive as product commands; that compatibility cleanup does not change the new `export` domain above
- Legacy bundle/demo export behavior is useful as expectation seeds, but export is rebuilt around MCP-facing asset reuse and later workflow integration

## Cross-Domain Decomposition Notes

- `AskService` wraps slice planning, evidence building, and conservative answer summarization; preserve the underlying logic where it is still useful, but drop the top-level ask shell as a product surface.
- The old runtime registry is a good source of tool boundaries and safety guardrails, especially around `plan_slice`, `expand_slice`, `read_evidence_pack`, and guarded `open_span`, but the new repository is not a chat runtime and should not inherit session orchestration as architecture.
- Legacy CLI commands and demo exports can inform MCP tool naming, manifest shape, and export expectations, but they do not survive as compatibility surfaces.
- Storage is a cross-cutting support layer/package rather than one of the eight analysis domain sections in this mapping; durable support survives for scan state, slice state, repo metadata, and anchor persistence through `codewiki/anchors/storage.py`, while report/export outputs remain file/manifest oriented and runtime/session/telemetry persistence from the old runtime shell is not automatically carried forward.
- `agent_runtime`, `ask`, and `answers` are not preserved as top-level product surfaces; only the logic that the matrix and explicit non-mappings retain may be harvested into new MCP/domain contracts.

## Explicit Non-Mappings

- `codewiki/agent_runtime/orchestrator.py` and `codewiki/agent_runtime/session_manager.py` do not map to a new product domain or top-level product surface; only selected guarded tool-boundary behavior informs MCP contracts.
- `codewiki/indexing/service.py` and deprecated CLI aliases such as `index`, `analyze`, `export`, and `bundle` do not map forward; zero compatibility remains the rule.
- `ask/service.py` and `answers/models.py` do not survive as a standalone domain or top-level product surface; their useful logic decomposes into `slice`, `evidence`, `impact`, and future workflow/document layers.
- `codewiki/retrieval/*` does not remain a separate public domain or top-level product surface even though its logic survives; bounded-read and freshness enforcement fold into `evidence`.
- `codewiki/storage/session_store.py`, `codewiki/storage/trace_store.py`, and old runtime telemetry/event persistence are not automatically mapped forward just because asset persistence survives; they require fresh justification in later phases.
- Old runtime paths under `<repo>/.claude/codewiki/` do not map forward; runtime assets move to `<repo>/.codewiki/`.
- Checked-in fixture repositories and synthetic fixture builders are not domain capabilities; they remain test-only baselines for later contract, integration, and golden validation.

## Acceptance Handoff Note

- Task 4 finalization: this document owns the accepted mapping from inventoried legacy capabilities into the M1 eight-domain contract baseline.
- This fixes the eight-domain contract baseline: `scan`, `scope`, `anchors`, `slice`, `evidence`, `impact`, `report`, and `export`, with `storage` treated as cross-cutting support rather than a ninth analysis domain.
- `migration/capability-mapping.md` is the domain-mapping baseline for M1.
- `migration/old-repo-inventory.md` is the evidence/inventory baseline for M1.
- If any final migration decision or handoff-precedence conflict appears across the three documents, `migration/keep-drop-rewrite.md` is the final disposition/decision authority for M1.
