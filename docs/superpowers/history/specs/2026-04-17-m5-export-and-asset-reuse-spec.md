# M5 Export and Asset Reuse Spec

> Parent spec: `docs/superpowers/specs/2026-04-17-repo-analysis-platform-design.md`
>
> Milestone: `M5`

## 1. Goal

Make analysis results portable, reusable, and reviewable across later workflows instead of keeping them trapped inside a single session.

This phase strengthens the platform as a reusable analysis system rather than a transient tool run.

## 2. Scope

Included:

- export-oriented MCP tools
- reusable bundles for selected analysis artifacts
- scope snapshots
- evidence bundles
- reuse and freshness-oriented rules where practical
- stronger golden-output comparisons

Excluded:

- public distribution or package publishing work
- broad multi-format export ambitions that do not help the self-use workflow

## 3. Export Targets

M5 must support export for at least:

- analysis bundles
- scope snapshots
- evidence bundles

Each exported asset should preserve enough structure to be reused in later workflows or reviewed offline.

## 4. Reuse Requirement

The phase must improve reuse of prior analysis through:

- stable identifiers
- freshness checks where needed
- exportable structured payloads
- explicit ownership of exported artifacts

Reuse does not require full caching sophistication, but it must be intentional.

## 5. Validation Requirement

M5 validation should prove that analysis assets created in one workflow can be consumed later by:

- repository understanding follow-up
- impact review
- document authoring

## 6. Acceptance Criteria

M5 is complete when:

- export tools are usable
- exported artifacts preserve meaningful structure
- later workflows can consume exported results
- freshness and reuse behavior is understandable to the operator

## 7. Risks

Main risks:

- exporting blobs with weak structure
- creating reuse paths that hide stale analysis
- building a large asset system before the self-use workflow needs it

Control measures:

- keep exported payloads structured and domain-specific
- expose freshness state
- scope exports to real downstream workflows

## 8. Handoff to M6

M5 hands off:

- reusable exported analysis assets
- stronger cross-workflow portability
- better regression and golden comparison hooks

M6 can then focus on making the platform comfortable for daily use.
