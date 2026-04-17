# M4 Document DSL and Rendering Spec

> Parent spec: `docs/superpowers/specs/2026-04-17-repo-analysis-platform-design.md`
>
> Milestone: `M4`

## 1. Goal

Create the structured document system that turns analysis outputs into typed document objects and renders them into Markdown through Python.

This phase establishes disciplined document generation instead of free-form text output.

## 2. Scope

Included:

- document specs for initial document types
- typed document DSL models
- validation rules
- Markdown rendering pipeline
- first analysis-writing workflow skill

Excluded:

- arbitrary prose generation without structure
- alternate output formats unless they directly support the Markdown path
- public publishing workflows

## 3. Document Types

M4 must define initial specs for:

- `module-summary`
- `issue-analysis`
- `design-note`
- `review-report`

Each spec must define:

- required sections
- expected evidence sources
- mandatory fields
- conclusion requirements
- citation or evidence-binding expectations

## 4. DSL Requirement

The document DSL source of truth must use typed Python models, preferably `pydantic` or `dataclass`.

Those models must be able to represent:

- metadata
- section hierarchy
- findings
- interpretation
- unknowns
- risks
- recommendations
- evidence bindings

Serialization to YAML or JSON is allowed as a storage or debug format, but not as the primary design center.

## 5. Rendering Requirement

The renderer must:

- validate document objects before rendering
- enforce document structure
- standardize heading layout
- standardize evidence and citation formatting
- write final Markdown output

The renderer is a required Python stage, not a formatting afterthought.

## 6. Skill Requirement

M4 must introduce an `analysis-writing` workflow skill that:

- chooses a document type
- gathers relevant analysis assets
- builds a typed document object
- validates it against the spec
- renders Markdown through Python

The workflow must not jump directly from evidence to unstructured Markdown drafting.

## 7. Acceptance Criteria

M4 is complete when:

- initial document specs are defined
- typed DSL models exist and are usable
- validation rules prevent structurally incomplete documents
- Markdown rendering works end to end
- the writing workflow consumes analysis outputs instead of bypassing them

## 8. Risks

Main risks:

- drifting back to plain Markdown templates
- making the DSL too weak to capture evidence structure
- embedding rendering logic into workflow skill text

Control measures:

- keep specs and DSL types explicit
- require Python rendering
- validate before render

## 9. Handoff to M5

M4 hands off:

- document specs
- typed document models
- render pipeline
- workflow hooks for document generation

M5 can then focus on portability and reuse of those outputs.
