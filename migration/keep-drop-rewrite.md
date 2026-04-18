# Keep, Drop, Rewrite

This baseline collapses the approved M0 inventory and capability mapping into one authoritative disposition matrix for M1. The matrix is package-family oriented, single-class only, and uses the approved M0 documents as the source of truth. `docs/gpt5.4proreview.md` is used only to sharpen rewrite/drop rationale where the inventory and mapping already point the same way.

## Decision Rules

1. Every major legacy family or baseline asset appears exactly once in the matrix and is assigned exactly one class.
2. `migrate and reorganize` means the deterministic offline capability survives, but package boundaries, runtime paths, and storage layout may move to fit the new repo.
3. `extract logic, rewrite shell` means some durable logic or contracts survive, but the old top-level surface, orchestration shell, or output contract must not be carried forward intact.
4. `test-only baseline` means preserve as fixture, golden reference, or migration acceptance input only; it is not product code.
5. `drop` means no forward product surface, no compatibility promise, and no package-level migration beyond optional reference reading during rewrites.
6. When a family overlaps another concern, the matrix assigns ownership once and the notes column states the boundary to avoid double-classification.
7. Inventory and mapping win over convenience: no row may keep a compatibility alias, chat shell, or old runtime path just because it already exists.

## Disposition Matrix

| Legacy item | Class | Baseline rationale | M1 boundary note |
| --- | --- | --- | --- |
| `codewiki/scan/*` | migrate and reorganize | Approved inventory marks scan as deterministic offline core and capability mapping keeps it as the base asset-creation domain. | Move runtime assets from `.claude/codewiki/` to `.codewiki/`; keep scan IDs, provenance capture, and downstream bindings. |
| `codewiki/scope/*` | migrate and reorganize | Scope heuristics and config-backed classification are already domain-shaped and fixture-backed. | Preserve typed file-role logic and explanation signals, not formatted CLI-only output. |
| `codewiki/anchors/*` | migrate and reorganize | Anchor extraction is deterministic and central to later slice and impact flows. | Keep structural extraction logic; storage ownership lives with the storage row, not here. |
| `codewiki/infrastructure/treesitter/*` | migrate and reorganize | Parser substrate is part of the durable anchor extraction stack. | Harvest as infrastructure under new layout; do not preserve old package seams just because they are parser-adjacent. |
| `codewiki/vendor/fsoft_codewiki/*` | migrate and reorganize | Capability mapping explicitly allows harvested vendored analyzer logic where it supports offline structural facts. | Vendor only the useful deterministic analyzer logic; do not inherit the upstream repo-level workflow shape. |
| `codewiki/slices/*` | migrate and reorganize | Slice planning, expansion, seed resolution, and budgets are core query-time analysis capabilities. | Keep `plan_slice`/`expand_slice` behavior as first-class domain tools, not hidden behind `ask`. |
| `codewiki/evidence/*` | migrate and reorganize | Context-pack construction, citations, and evidence-pack structure are durable core logic. | Keep typed evidence assets and citation rules; shell rendering concerns are classified elsewhere. |
| `codewiki/impact/service.py` | migrate and reorganize | Conservative impact reasoning maps cleanly into the new `impact` domain. | Keep changed-path and anchor-centered analysis, but bind it to new typed impact assets instead of answer/report shells. |
| `codewiki/storage/*` plus related `codewiki/scan/storage.py` and anchor/scan persistence surfaces | migrate and reorganize | Storage is durable cross-cutting infrastructure for scans, slices, evidence, and assets, even though session/trace pieces need narrower forward use. | Rebuild schema/layout under `.codewiki/`; product asset persistence survives, while runtime/session telemetry survives only if later phases justify it. |
| `codewiki/indexing/service.py` | drop | Inventory and mapping both classify indexing as a compatibility wrapper with no new-domain destination. | No `index` compatibility surface survives M1. |
| `codewiki/retrieval/*` | extract logic, rewrite shell | Retrieval guardrails are valuable, but capability mapping folds them into `evidence` instead of preserving a standalone public subsystem. | Keep freshness, tracked-file checks, and bounded snippet reads as evidence-domain enforcement only. |
| `codewiki/reporting/service.py` | extract logic, rewrite shell | Reporting starts from durable evidence facts, but the old markdown-writing shell and fixed output path do not survive. | Rebuild as typed report skeleton generation that can feed the future document pipeline. |
| `tests/fixtures/scope_first_repo.py` | test-only baseline | Approved inventory names it as the de facto regression backbone across scan/scope/slice/evidence/reporting/runtime tests. | Preserve as a contract fixture and migration acceptance seed, not product code. |
| `EasyFlash-master/` | test-only baseline | Inventory identifies it as a real fixture candidate for later end-to-end repo-understanding validation. | Keep only as a repo-understanding baseline candidate. |
| `builds/easyflash-e2e-clean/easyflash/` | test-only baseline | Inventory identifies the clean EasyFlash tree as a checked-in real fixture candidate tied to existing demo/export evidence. | Use for later end-to-end and export validation; do not treat as shipped product content. |
| `codewiki/agent_runtime/*` | extract logic, rewrite shell | Tool boundaries and guarded read behavior are useful, but orchestration, session shells, and chat runtime architecture must not survive intact. | Preserve selected tool contracts and safety gates only; replace the runtime shell wholesale. |
| `codewiki/ask/*` and `codewiki/answers/*` | extract logic, rewrite shell | The useful part is the decomposition into slice, evidence, and conservative answer structure; the top-level ask product surface is explicitly non-mapped. | Keep answer-contract ideas where they inform typed result shapes, but do not preserve `ask` as a mega-surface. |
| `codewiki/cli/*` plus related `codewiki/demo/*` and `codewiki/benchmarks/*` shells | drop | CLI compatibility commands, bundle/demo export shells, and benchmark harnesses do not map forward as product surfaces. | Keep only any golden expectations indirectly through fixtures/tests; no CLI compatibility or demo-first shell survives. |

## Fixture Nominations

- `tests/fixtures/scope_first_repo.py` is the mandatory fast baseline fixture for contract and migration regression checks.
- `builds/easyflash-e2e-clean/easyflash/` is the preferred checked-in real-repo baseline because it is already normalized into the harvest evidence set.
- `EasyFlash-master/` remains a secondary real-repo candidate when M1 or later needs a second independent end-to-end corpus.
- Existing focus-report, bundle, and demo outputs should be treated only as comparison artifacts when validating rewritten report/export behavior.

## Notes for M1

- Treat this matrix as authoritative and single-source: no family gets split across multiple classes in planning docs unless M1 first updates this baseline.
- `retrieval` is not a standalone M1 domain. Its useful logic moves under `evidence`.
- `reporting` is not allowed to survive as a direct markdown writer with a fixed legacy path.
- `agent_runtime`, `ask`, and `answers` are reference implementations for logic harvesting, not architecture templates.
- `.claude/codewiki/` is a dead runtime root for migration purposes; `.codewiki/` is the only valid direction.
- Compatibility commands and wrapper names such as `index`, `analyze`, `export`, and `bundle` remain out of scope even if a shell is easy to keep.

Highest-risk rewrite and drop rationale:

- `codewiki/agent_runtime/*` is high risk because it mixes useful guarded tool boundaries with session orchestration, telemetry persistence, and chat-runtime assumptions. Migrating it wholesale would smuggle the old product architecture into M1, so only selected contracts such as guarded span access and domain tool boundaries should be harvested.
- `codewiki/ask/*` and `codewiki/answers/*` are high risk because they hide slice planning, evidence gathering, and conservative summarization behind a single ask-shaped surface. M1 needs those underlying capabilities exposed directly, not re-wrapped into another mega-entrypoint that blurs facts, inference, and unknowns.
- `codewiki/retrieval/*` is a rewrite rather than a keep because bounded reads and freshness checks are important, but the old package is organized like a separate subsystem. M1 should absorb those checks into `evidence` so scan binding and guarded snippet access stay mandatory without preserving a legacy public seam.
- `codewiki/reporting/service.py` is a rewrite rather than a keep because the durable value is the report skeleton assembled from evidence, not the old markdown shell or fixed destination under `docs/codewiki/`. Rewriting now prevents M1 from inheriting an output contract that conflicts with the future typed document pipeline.
- `codewiki/cli/*` plus related demo and benchmark shells are a drop because their main value is transitional wrapper behavior and experiment harnessing. Keeping them would reintroduce compatibility pressure and shell-shaped workflow assumptions that the approved mapping explicitly rejects.
