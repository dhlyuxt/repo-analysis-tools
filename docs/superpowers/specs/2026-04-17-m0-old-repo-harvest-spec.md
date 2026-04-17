# M0 Old Repository Harvest Spec

> Parent spec: `docs/superpowers/specs/2026-04-17-repo-analysis-platform-design.md`
>
> Milestone: `M0`

## 1. Goal

Establish a complete, explicit inventory of what the old `mycodewiki` repository contains, what is worth carrying forward, and what must be dropped before the new platform starts implementation.

This phase exists to prevent the new repository from inheriting accidental architecture from the old one.

## 2. Scope

M0 covers analysis and classification work only. It does not create the new platform implementation.

Included:

- inventory of old offline capabilities
- remapping old capabilities into the new domain model
- classification of old modules into keep, rewrite, test-only, and drop
- identification of long-lived test fixtures and sample repositories
- capture of migration decisions in durable documents

Excluded:

- implementing new MCP tools
- preserving old CLI compatibility
- building workflow skills
- writing implementation plans

## 3. Inputs

Primary inputs:

- the old `mycodewiki` repository
- its tests, fixtures, and example outputs
- the approved platform design spec

Secondary inputs:

- vendored or third-party C analysis code already present in the old repository
- current usage patterns that reveal which offline capabilities were actually useful

## 4. Required Outputs

M0 must produce these durable artifacts:

- `migration/old-repo-inventory.md`
- `migration/capability-mapping.md`
- `migration/keep-drop-rewrite.md`

Each artifact must be specific and reviewable, not a loose note dump.

## 5. Capability Classification Rules

Every relevant old module or capability must be assigned to exactly one class:

- `migrate and reorganize`
- `extract logic, rewrite shell`
- `test-only baseline`
- `drop`

Decision rules:

- deterministic offline analysis logic should be favored
- prompt orchestration and agent runtime code should be disfavored
- legacy compatibility shells should not be preserved
- test assets may survive even when their implementation does not

## 6. Domain Remapping Requirement

Old capabilities must be remapped into the new domain model:

- `scan`
- `scope`
- `anchors`
- `slice`
- `evidence`
- `impact`
- `report`
- `export`

This remapping is required even when the old repository used different package names or command surfaces.

## 7. Fixture Strategy

M0 must nominate at least one and preferably two real C repositories to serve as long-term fixtures for later phases.

Those fixtures should support:

- repository understanding scenarios
- anchor lookup scenarios
- slice and evidence scenarios
- later impact-analysis scenarios

## 8. Acceptance Criteria

M0 is complete when:

- every major old offline capability has been inventoried
- every inventoried item has a disposition
- the new domain mapping is explicit
- candidate fixtures are selected
- no unresolved question blocks M1 package design

## 9. Risks

Main risks:

- mixing implementation work into harvest work
- keeping old package boundaries by habit
- under-documenting why a module is dropped

Control measures:

- require written rationale in `keep-drop-rewrite`
- keep M0 document-first
- review classifications against the parent design spec

## 10. Handoff to M1

M0 hands off:

- the migration inventory
- the domain mapping
- the selected fixtures
- the list of non-goals and dropped subsystems

M1 may start only after these artifacts are accepted as the authoritative migration baseline.
