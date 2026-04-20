# M2 Analysis-First Mainline Spec

> Parent spec: `docs/superpowers/specs/2026-04-17-repo-analysis-platform-design.md`
>
> Milestone: `M2`

## 1. Goal

Make the new platform genuinely useful for repository understanding in Codex by implementing the primary analysis-first workflow from scan through bounded evidence inspection.

This is the first milestone that must feel real in day-to-day use.

## 2. Scope

Included:

- functioning scan capability
- functioning scope inspection
- functioning anchor discovery and description
- slice planning for repository understanding tasks
- evidence pack creation and reading
- bounded span opening
- first repository-understanding workflow skill
- end-to-end validation on a real C repository

Excluded:

- full change-impact workflow depth
- full document authoring pipeline
- advanced export and reuse
- old CLI compatibility

## 3. Primary Workflow

M2 must make this path work as a coherent mainline:

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

This path is the milestone definition, not a side example.

## 4. Functional Requirements

Repository-understanding behavior must support:

- orienting on repository structure
- locating relevant files and regions
- identifying anchors such as functions, macros, globals, and types
- focusing on a bounded subset of the repository through slices
- reading structured evidence before reading raw spans
- opening precise code spans with constraints

## 5. Skill Requirement

M2 must introduce the first `repo-understand` workflow skill.

That skill must:

- sequence MCP tools rather than embed domain logic
- distinguish confirmed facts from interpretation
- encourage evidence-backed answers
- support unfamiliar C repositories, not just one demo case

## 6. Validation Requirement

M2 validation must include at least one real C repository fixture and one end-to-end scenario proving that a Codex session can:

- scan the repository
- understand its structure
- locate a relevant anchor
- build a focused slice
- read evidence
- inspect precise spans
- summarize findings with traceable support

## 7. Acceptance Criteria

M2 is complete when:

- the mainline workflow above is operational
- repository-understanding outputs are evidence-backed
- span access is bounded and not equivalent to unrestricted browsing
- the first workflow skill is usable in practice
- a real fixture repository passes the end-to-end scenario

## 8. Risks

Main risks:

- over-expanding scope into impact and document work
- letting `open_span` become an unrestricted file reader
- giving workflow skills hidden analysis responsibilities

Control measures:

- protect the mainline path from feature creep
- keep evidence pack access ahead of raw span access
- review workflow skill prompts against the MCP-first rule

## 9. Handoff to M3

M2 hands off:

- a usable repository-understanding platform core
- the first workflow skill
- trusted fixtures and end-to-end scenarios

M3 should build on this foundation instead of reworking it.
