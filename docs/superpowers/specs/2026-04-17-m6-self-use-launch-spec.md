# M6 Self-Use Launch Spec

> Parent spec: `docs/superpowers/specs/2026-04-17-repo-analysis-platform-design.md`
>
> Milestone: `M6`

## 1. Goal

Reach a stable self-use launch where the new repository replaces the old repository as the operator's normal environment for C repository analysis in Codex.

This is an adoption milestone, not a public release milestone.

## 2. Scope

Included:

- Codex-first bootstrap and install path
- Claude-compatible skill distribution
- minimal operating documentation
- demo or smoke validation script
- end-to-end daily-use validation

Excluded:

- public packaging polish
- marketplace-grade distribution
- broad team onboarding requirements

## 3. Launch Requirements

For self-use launch, the platform must support a realistic day-to-day workflow that includes:

- repository scan and refresh
- repository understanding with evidence traceability
- basic change impact analysis
- document generation through spec, DSL, and renderer

These flows must work on a real C repository, not just synthetic tests.

## 4. Operator Experience Requirement

M6 should provide:

- a clear setup path for Codex
- a documented compatibility path for Claude
- enough documentation to run the main workflows without returning to the old repository

The goal is practical replacement, not polished packaging.

## 5. Validation Requirement

M6 validation must show that the operator can complete an end-to-end run that includes:

- starting from a real repository
- performing repository understanding
- tracing evidence
- optionally evaluating a change
- generating a structured Markdown artifact

## 6. Acceptance Criteria

M6 is complete when:

- the new repository is the default daily analysis entry point
- the old repository is no longer needed for routine work
- Codex-first workflows are stable
- the self-use documentation is sufficient for repeated use

## 7. Risks

Main risks:

- declaring launch before real workflows are comfortable
- over-investing in public-release work too early
- leaving setup knowledge trapped in memory instead of documentation

Control measures:

- define launch by repeated real use
- keep the milestone self-use focused
- document the operator path explicitly

## 8. Post-M6 Direction

After M6, the project can decide whether to remain self-use only or evolve toward wider reuse.

That decision is intentionally outside this milestone. M6 only establishes that the new platform is viable as the operator's real working environment.
