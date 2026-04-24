# Repo Doc Writer Spec

> Parent specs:
> - `docs/superpowers/history/specs/2026-04-17-repo-analysis-platform-design.md`
> - `docs/superpowers/history/specs/2026-04-17-m4-document-dsl-and-rendering-spec.md`

## 1. Goal

Define a subagent-only `repo-doc-writer` skill that turns repository audit outputs into a controlled multi-document design set.

This feature exists to keep document generation structured and reviewable. The coordinating agent must not learn document-writing rules or improvise repository design prose on its own.

## 2. Core Rule

`repo-doc-writer` is a dedicated skill for a document-writer subagent.

The coordinating agent:

- does not load `repo-doc-writer`
- does not decide section layout
- does not draft final Markdown
- does not bypass the document pipeline with ad hoc prose

The document-writer subagent:

- loads `repo-doc-writer`
- consumes structured repository findings
- produces the final document set
- enforces the document spec and rendering rules

## 3. Scope

Included:

- one mirrored skill in `.agents/skills/` and `.claude/skills/`
- a subagent handoff contract from repository-audit workflows into document generation
- a controlled multi-document output for repository design documentation
- document generation driven by `doc_specs`, `doc_dsl`, validators, and renderer stages
- validation rules that reject incomplete or free-form document output

Excluded:

- teaching the coordinating agent how to write documents
- making repository-reading MCP tools responsible for prose generation
- free-form Markdown authoring by the document subagent
- publishing workflows, site generation, or PDF export
- diagram engines other than the existing Mermaid-capable document pipeline

## 4. Agent Boundary

The feature must preserve a hard boundary between orchestration and writing.

The coordinating agent is allowed to know only this handoff protocol:

```text
spawn document-writer subagent
-> tell it to load repo-doc-writer
-> provide the structured repository findings package
-> wait for generated document paths and validation status
```

The coordinating agent must not absorb any of the following:

- section policies
- per-document structure rules
- Mermaid placement rules
- citation formatting rules
- document renderer behavior

Those concerns belong only to `repo-doc-writer` and the code it drives.

## 5. Required Inputs

`repo-doc-writer` must require a structured findings package. The minimum accepted shape is:

```json
{
  "repo_name": "repo-analysis-tools",
  "target_repo": "/abs/path/to/repo",
  "output_root": "/abs/path/to/repo/docs/repo-design",
  "module_map": [
    {
      "module_id": "query",
      "module_name": "Query",
      "responsibility": "Symbol and call-graph queries",
      "paths": ["src/repo_analysis_tools/query"],
      "dependencies": ["scan", "anchors", "scope"]
    }
  ],
  "module_reports": [
    {
      "module_id": "query",
      "summary": [
        "Provides file, symbol, and call-path lookups over persisted scan data."
      ],
      "entry_points": [
        "QueryService.list_priority_files",
        "QueryService.resolve_symbols"
      ],
      "key_symbols": [
        "QueryService",
        "find_call_paths"
      ],
      "call_flows": [
        "query_tools -> QueryService -> scope/anchors stores"
      ],
      "risks": [
        "Results depend on the in-process scan registry."
      ],
      "unknowns": [
        "No benchmark data for very large repositories."
      ],
      "citations": [
        {
          "file_path": "src/repo_analysis_tools/query/service.py",
          "line_start": 1,
          "line_end": 520,
          "symbol_name": "QueryService"
        }
      ]
    }
  ],
  "global_findings": {
    "architecture_summary": [
      "The active surface is query-first and scan-rooted."
    ],
    "cross_module_flows": [
      "scan -> scope -> anchors -> query -> mcp"
    ],
    "unknowns": [
      "No active report MCP surface is exposed."
    ],
    "citations": [
      {
        "file_path": "docs/architecture.md",
        "line_start": 1,
        "line_end": 120,
        "symbol_name": null
      }
    ]
  }
}
```

If any required field is missing, `repo-doc-writer` must stop and report the missing input instead of inferring or filling it in.

## 6. Output Contract

The output is a document set, not a single long report.

The default output root is:

```text
<target_repo>/docs/repo-design/
```

The required document set is:

```text
docs/repo-design/
├── index.md
├── repository-architecture.md
├── module-map.md
├── evidence-index.md
├── modules/
│   ├── <module-id>.md
│   └── ...
└── manifest.json
```

Required meanings:

- `index.md`: entry point and reading order
- `repository-architecture.md`: whole-repository framework, boundaries, and major flows
- `module-map.md`: module inventory, boundaries, and inter-module relationships
- `evidence-index.md`: claim-to-citation index plus unresolved items
- `modules/<module-id>.md`: one detailed design note per module
- `manifest.json`: generated file list plus validation status

## 7. Writing Discipline

`repo-doc-writer` must not produce free-form Markdown directly from a prompt.

The required generation path is:

```text
structured findings package
-> typed document inputs
-> doc_specs selection
-> doc_dsl document objects
-> structure validation
-> Mermaid validation
-> MarkdownRenderer
-> final Markdown files
```

This means:

- the subagent chooses document types, not arbitrary page shapes
- every final document is backed by a typed document object
- final Markdown comes from the renderer, not handwritten prose
- diagrams are Mermaid blocks in the DSL, not raw Markdown fragments pasted into text

## 8. Document Types

The repository design set must define at least these controlled document types:

- `repo-architecture`
- `module-map`
- `module-detail`
- `evidence-index`

Each document type must define:

- required sections
- Mermaid policy by section: required, allowed, or disallowed
- evidence-binding expectations
- how unknowns are represented

The system must not allow a repository design document without explicit section policy.

## 9. Validation Rules

Validation must reject:

- missing required sections
- module documents without a matching `module_id`
- claims that appear as conclusions without citations
- Mermaid blocks placed in disallowed sections
- output sets that omit one or more module documents
- hand-authored Markdown passed off as renderer output

Unknowns are allowed, but they must remain explicitly labeled as unknowns.

## 10. Fallback Policy

If the active environment does not expose an MCP-facing report surface, the feature may still generate the document set through local Python code.

That fallback is allowed only if all of the following remain true:

- `doc_specs` still define the shape
- `doc_dsl` still defines the document objects
- validators still run before render
- `MarkdownRenderer` still produces the final Markdown

The fallback must not degrade into prompt-only document drafting.

## 11. Acceptance Criteria

The feature is complete when:

- `repo-doc-writer` exists as a mirrored skill in `.agents/skills/` and `.claude/skills/`
- the skill text explicitly says it is for a document-writer subagent only
- the coordinating agent can hand off a structured findings package without loading the skill itself
- the document set contains the required top-level files plus one module document per module
- the generated documents are produced through the controlled document pipeline
- missing inputs and unsupported layouts fail fast instead of triggering improvisation
- unknowns remain labeled as unknowns in the final output

## 12. Risks

Main risks:

- the coordinating agent gradually reabsorbs document-writing logic
- the document subagent bypasses the renderer and writes prose directly
- repository findings arrive under-specified and tempt the subagent to invent facts
- a single mega-document replaces the required document set

Control measures:

- keep the coordinating-agent contract extremely small
- make `repo-doc-writer` subagent-only in both wording and tests
- require structured input and fail on missing fields
- keep the output set fixed and reviewable
- keep Markdown downstream from typed document objects
