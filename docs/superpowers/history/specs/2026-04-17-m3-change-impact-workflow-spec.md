# M3 Change Impact Workflow Spec

> Parent spec: `docs/superpowers/specs/2026-04-17-repo-analysis-platform-design.md`
>
> Milestone: `M3`

## 1. Goal

Add a change-centered workflow that helps reason about the impact of modifying files, anchors, or focused regions in a real C repository.

This phase turns the platform from passive understanding into engineering decision support.

## 2. Scope

Included:

- impact analysis domain implementation
- path-based impact queries
- anchor-based impact queries
- impact summarization
- first change-impact workflow skill
- risk-oriented outputs

Excluded:

- full document DSL and renderer implementation
- extensive export ecosystem beyond what impact needs immediately
- compatibility shims for old behavior

## 3. Primary Workflow

M3 must make this path usable:

```text
refresh_scan
-> impact_from_paths / impact_from_anchor
-> summarize_impact
-> inspect related anchors or slices
-> build_evidence_pack
-> produce risk-oriented findings
```

## 4. Functional Requirements

Impact analysis must support:

- direct impact from changed files
- impact seeded from important anchors
- propagation hints to nearby modules or call sites
- explicit blind spots and uncertainty notes
- recommendations for regression focus

The output is not just a list of files. It must help a user reason about change consequences.

## 5. Skill Requirement

M3 must introduce a `change-impact` workflow skill that:

- starts from changed files or anchors
- uses MCP tools for evidence-backed impact analysis
- produces structured risk summaries
- highlights confirmed impact versus likely but unproven propagation

## 6. Validation Requirement

M3 validation must use at least one realistic change scenario against a real fixture repository.

The validation should show:

- changed inputs
- impacted areas
- supporting evidence
- recommended follow-up focus

## 7. Acceptance Criteria

M3 is complete when:

- impact tools return useful structured outputs
- the workflow skill helps analyze real changes
- risk summaries are more informative than a raw affected-file list
- uncertainty is surfaced explicitly instead of hidden

## 8. Risks

Main risks:

- overselling weak propagation as certainty
- collapsing impact output into prose with no evidence
- duplicating logic between impact tools and the workflow skill

Control measures:

- keep evidence and uncertainty explicit
- define structured impact payloads
- keep workflow skill orchestration-only

## 9. Handoff to M4

M3 hands off:

- a functioning change-impact workflow
- structured impact outputs
- realistic impact scenarios for future document generation

M4 can then consume those outputs for document authoring.
