# M1 Platform Skeleton and Contracts Spec

> Parent spec: `docs/superpowers/specs/2026-04-17-repo-analysis-platform-design.md`
>
> Milestone: `M1`

## 1. Goal

Create the initial repository skeleton, runtime conventions, storage boundaries, and MCP contracts for the new platform without yet claiming full analysis capability.

This phase exists to lock the architectural seams before migration accelerates.

## 2. Scope

Included:

- package layout for core domains
- runtime directory convention under `<target_repo>/.codewiki/`
- shared IDs, error types, and path conventions
- storage contract boundaries
- MCP server bootstrap
- tool contract stubs for each domain group
- baseline contract tests and golden test scaffolding

Excluded:

- deep domain implementation
- full repository understanding workflow behavior
- mature impact analysis
- document DSL implementation
- implementation plans

## 3. Required Structure

M1 must establish the top-level code structure for:

- `core`
- `storage`
- `scan`
- `scope`
- `anchors`
- `slice`
- `evidence`
- `impact`
- `report`
- `export`
- `mcp`
- `skills`
- `doc_specs`
- `doc_dsl`
- `renderers`
- `tests`

The exact file count can remain small, but the boundaries must be visible.

## 4. Runtime Contract

The platform must standardize:

- runtime root as `<target_repo>/.codewiki/`
- stable IDs for scans, slices, evidence packs, reports, and exports
- path normalization rules
- error taxonomy for MCP-facing failures
- storage ownership by domain

These rules must be documented in code and in at least one architecture-facing document.

## 5. MCP Contract Scope

M1 must define contract stubs for the domain groups:

- scan
- scope
- anchors
- slice
- evidence
- impact
- report
- export

Each stub should define:

- input shape
- output shape
- stable identifiers
- standard response envelope
- expected failure modes

## 6. Testing Scope

M1 testing is structural and contract-oriented.

Required test classes:

- MCP contract tests
- storage and path normalization tests
- smoke test that the MCP server starts
- starter golden harness for later fixture-based comparisons

## 7. Acceptance Criteria

M1 is complete when:

- the new repository skeleton is in place
- the MCP server boots successfully
- response contracts are stable enough for workflow design
- runtime storage rules are explicit
- later phases can implement domains without reopening package boundaries

## 8. Risks

Main risks:

- rushing domain code before the boundaries settle
- leaving contract details implicit
- allowing client-specific runtime layout back into the design

Control measures:

- treat contract definitions as first-class deliverables
- keep `.codewiki/` mandatory
- review the skeleton against the parent architecture before moving on

## 9. Handoff to M2

M1 hands off:

- the repository skeleton
- MCP response contracts
- runtime and storage rules
- starter tests

M2 can then focus on real analysis behavior instead of package design.
