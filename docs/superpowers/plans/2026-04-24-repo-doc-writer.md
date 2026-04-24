# Repo Doc Writer Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a subagent-only `repo-doc-writer` workflow that turns structured repository findings into a controlled multi-document design set under `docs/repo-design/` without teaching the coordinating agent how to write documents.

**Architecture:** Reuse the existing M4 document pipeline instead of inventing a second prose path. Extend `doc_specs`, `doc_dsl`, validators, and the Markdown renderer so repository-design document types can express evidence-bound text and Mermaid-backed flows, then add a deterministic writer service plus a small CLI entrypoint that the `repo-doc-writer` skill can invoke. The coordinating agent remains orchestration-only; the mirrored skill is loaded only by the document-writer subagent and drives the local Python writer rather than free-form Markdown drafting.

**Tech Stack:** Python 3.11, stdlib `unittest`, stdlib `json`/`subprocess`/`tempfile`/`pathlib`, existing `doc_specs`, `doc_dsl`, `MarkdownRenderer`, `MermaidValidator`, Markdown skill files under `.agents/skills/` and `.claude/skills/`

---

## File Structure

### New Files

- Create: `src/repo_analysis_tools/doc_specs/repo_architecture.py`
  Responsibility: section policy for repository-wide architecture documents.
- Create: `src/repo_analysis_tools/doc_specs/module_map.py`
  Responsibility: section policy for module inventory and dependency-map documents.
- Create: `src/repo_analysis_tools/doc_specs/module_detail.py`
  Responsibility: section policy for per-module detail documents.
- Create: `src/repo_analysis_tools/doc_specs/evidence_index.py`
  Responsibility: section policy for claim-to-citation index documents.
- Create: `src/repo_analysis_tools/report/repo_design_models.py`
  Responsibility: typed input package, module findings, citation payloads, and generated-manifest models for repository design document sets.
- Create: `src/repo_analysis_tools/report/repo_design_service.py`
  Responsibility: build, validate, render, and persist the full repository design document set from a structured findings package.
- Create: `tools/write_repo_design_docs.py`
  Responsibility: deterministic CLI entrypoint used by the document-writer subagent to turn an input JSON package into rendered documents plus `manifest.json`.
- Create: `tests/unit/test_repo_doc_writer_service.py`
  Responsibility: unit coverage for findings-package parsing, document-set generation, output layout, and manifest persistence.
- Create: `tests/integration/test_repo_doc_writer_workflow.py`
  Responsibility: end-to-end coverage for the CLI writer workflow from input JSON to final document set.
- Create: `.agents/skills/repo-doc-writer/SKILL.md`
  Responsibility: Codex skill text for the document-writer subagent only.
- Create: `.claude/skills/repo-doc-writer/SKILL.md`
  Responsibility: mirrored Claude-compatible copy of the same skill text.

### Modified Files

- Modify: `src/repo_analysis_tools/doc_specs/base.py`
  Responsibility: register the new repository-design document types and expose any extra section-policy fields needed for evidence requirements.
- Modify: `src/repo_analysis_tools/doc_dsl/models.py`
  Responsibility: allow text blocks to carry evidence bindings so repository-design prose can stay citation-backed without inventing a raw Markdown escape hatch.
- Modify: `src/repo_analysis_tools/doc_dsl/validators.py`
  Responsibility: reject repository-design documents with missing required evidence-bound sections or invalid per-document structure.
- Modify: `src/repo_analysis_tools/doc_dsl/builders.py`
  Responsibility: add typed builders for `repo-architecture`, `module-map`, `module-detail`, and `evidence-index` documents from the findings package.
- Modify: `src/repo_analysis_tools/renderers/markdown.py`
  Responsibility: render evidence bindings consistently for both text and Mermaid blocks.
- Modify: `tests/unit/test_document_dsl.py`
  Responsibility: cover the new document types, text-block evidence rules, and renderer behavior.
- Modify: `tests/unit/test_client_skill_distribution.py`
  Responsibility: require `repo-doc-writer` to be mirrored between `.agents/skills/` and `.claude/skills/`.
- Modify: `tests/smoke/test_package_layout.py`
  Responsibility: require the mirrored skill files in the active tree.
- Modify: `tests/unit/test_architecture_docs.py`
  Responsibility: assert the new skill is subagent-scoped and references the controlled document pipeline.
- Modify: `README.md`
  Responsibility: document the additional active skill and state that it is for document-writer subagents rather than the coordinating repository reader.
- Modify: `docs/architecture.md`
  Responsibility: record the repo-audit-to-document-writer handoff and the controlled document-set pipeline.

### Existing Files To Reuse As References

- Reuse: `docs/superpowers/specs/2026-04-24-repo-doc-writer-spec.md`
  Responsibility: source of truth for the coordinating-agent boundary, input contract, output contract, and acceptance criteria.
- Reuse: `docs/superpowers/history/specs/2026-04-17-m4-document-dsl-and-rendering-spec.md`
  Responsibility: source of truth for the existing typed-document pipeline and Mermaid validation sequence.
- Reuse: `src/repo_analysis_tools/report/service.py`
  Responsibility: implementation reference for validate-render-persist ordering.
- Reuse: `.agents/skills/repo-understand/SKILL.md`
  Responsibility: reference for concise active skill style and mirrored distribution.

---

### Task 1: Extend The Typed Document Pipeline For Repository Design Documents

**Files:**
- Create: `src/repo_analysis_tools/doc_specs/repo_architecture.py`
- Create: `src/repo_analysis_tools/doc_specs/module_map.py`
- Create: `src/repo_analysis_tools/doc_specs/module_detail.py`
- Create: `src/repo_analysis_tools/doc_specs/evidence_index.py`
- Modify: `src/repo_analysis_tools/doc_specs/base.py`
- Modify: `src/repo_analysis_tools/doc_dsl/models.py`
- Modify: `src/repo_analysis_tools/doc_dsl/validators.py`
- Modify: `src/repo_analysis_tools/doc_dsl/builders.py`
- Modify: `src/repo_analysis_tools/renderers/markdown.py`
- Modify: `tests/unit/test_document_dsl.py`

- [ ] **Step 1: Write the failing document-pipeline tests for repo-doc-writer document types**

Add these tests to `tests/unit/test_document_dsl.py`:

```python
    def test_registry_exposes_repo_doc_writer_document_types(self) -> None:
        registry = build_document_spec_registry()

        self.assertTrue(
            {"repo-architecture", "module-map", "module-detail", "evidence-index"}.issubset(set(registry))
        )
        self.assertEqual(
            registry["module-detail"].section_policies["Internal Flow"].mermaid_policy,
            "required",
        )
        self.assertTrue(
            registry["repo-architecture"].section_policies["Overview"].requires_evidence_bindings
        )

    def test_validator_rejects_repo_architecture_section_without_evidence_bound_text(self) -> None:
        document = Document(
            document_type="repo-architecture",
            title="Repository Architecture",
            sections=[
                Section("Overview", [TextBlock(text="A claim without evidence bindings")]),
                Section("System Boundaries", [TextBlock(text="Boundary notes", evidence_bindings=[])]),
                Section(
                    "Runtime Flow",
                    [
                        MermaidBlock(
                            diagram_kind="flowchart",
                            source="flowchart LR\nScan --> Query\n",
                            caption="Runtime flow",
                            placement="inline",
                            evidence_bindings=[],
                            title="Flow",
                        )
                    ],
                ),
                Section("Constraints", [TextBlock(text="Constraint text", evidence_bindings=[])]),
                Section("Unknowns", [TextBlock(text="Unknowns are allowed without citations")]),
            ],
        )

        errors = validate_document(document, build_document_spec_registry()["repo-architecture"])

        self.assertIn("section 'Overview' requires evidence-bound blocks", errors)

    def test_markdown_renderer_renders_text_block_evidence_bindings(self) -> None:
        document = Document(
            document_type="evidence-index",
            title="Evidence Index",
            sections=[
                Section(
                    "Claims",
                    [
                        TextBlock(
                            text="QueryService owns symbol resolution.",
                            evidence_bindings=[
                                EvidenceBinding(
                                    file_path="src/repo_analysis_tools/query/service.py",
                                    line_start=1,
                                    line_end=80,
                                    anchor_name="QueryService",
                                )
                            ],
                        )
                    ],
                )
            ],
        )

        markdown = MarkdownRenderer().render(document)

        self.assertIn("src/repo_analysis_tools/query/service.py:1-80", markdown)
```

- [ ] **Step 2: Run the document pipeline tests and verify they fail**

Run:

```bash
/home/hyx/anaconda3/envs/agent/bin/python -m unittest tests.unit.test_document_dsl -v
```

Expected: FAIL because the registry does not expose the new document types, `SectionPolicy` has no evidence-binding rule, and `TextBlock` evidence bindings are not rendered.

- [ ] **Step 3: Add the new document specs and evidence-aware section policy**

Update `src/repo_analysis_tools/doc_specs/base.py` to extend `SectionPolicy` and register the new spec modules:

```python
@dataclass(frozen=True)
class SectionPolicy:
    title: str
    mermaid_policy: str
    requires_evidence_bindings: bool = False


def build_document_spec_registry() -> dict[str, DocumentSpec]:
    from repo_analysis_tools.doc_specs.design_note import DESIGN_NOTE_SPEC
    from repo_analysis_tools.doc_specs.evidence_index import EVIDENCE_INDEX_SPEC
    from repo_analysis_tools.doc_specs.issue_analysis import ISSUE_ANALYSIS_SPEC
    from repo_analysis_tools.doc_specs.module_detail import MODULE_DETAIL_SPEC
    from repo_analysis_tools.doc_specs.module_map import MODULE_MAP_SPEC
    from repo_analysis_tools.doc_specs.module_summary import MODULE_SUMMARY_SPEC
    from repo_analysis_tools.doc_specs.repo_architecture import REPO_ARCHITECTURE_SPEC
    from repo_analysis_tools.doc_specs.review_report import REVIEW_REPORT_SPEC

    return {
        MODULE_SUMMARY_SPEC.document_type: MODULE_SUMMARY_SPEC,
        ISSUE_ANALYSIS_SPEC.document_type: ISSUE_ANALYSIS_SPEC,
        DESIGN_NOTE_SPEC.document_type: DESIGN_NOTE_SPEC,
        REVIEW_REPORT_SPEC.document_type: REVIEW_REPORT_SPEC,
        REPO_ARCHITECTURE_SPEC.document_type: REPO_ARCHITECTURE_SPEC,
        MODULE_MAP_SPEC.document_type: MODULE_MAP_SPEC,
        MODULE_DETAIL_SPEC.document_type: MODULE_DETAIL_SPEC,
        EVIDENCE_INDEX_SPEC.document_type: EVIDENCE_INDEX_SPEC,
    }
```

Create `src/repo_analysis_tools/doc_specs/repo_architecture.py`:

```python
from repo_analysis_tools.doc_specs.base import DocumentSpec, SectionPolicy


REPO_ARCHITECTURE_SPEC = DocumentSpec(
    document_type="repo-architecture",
    required_sections=("Overview", "System Boundaries", "Runtime Flow", "Constraints", "Unknowns"),
    section_policies={
        "Overview": SectionPolicy("Overview", "disallowed", requires_evidence_bindings=True),
        "System Boundaries": SectionPolicy("System Boundaries", "allowed", requires_evidence_bindings=True),
        "Runtime Flow": SectionPolicy("Runtime Flow", "required", requires_evidence_bindings=True),
        "Constraints": SectionPolicy("Constraints", "allowed", requires_evidence_bindings=True),
        "Unknowns": SectionPolicy("Unknowns", "disallowed", requires_evidence_bindings=False),
    },
)
```

Create analogous spec files:

```python
# module_map.py -> sections: Module Inventory, Dependency Graph, Coverage Notes, Unknowns
# module_detail.py -> sections: Responsibility, Entry Points, Internal Flow, Dependencies, Risks, Unknowns
# evidence_index.py -> sections: Coverage, Claims, Unknowns
```

- [ ] **Step 4: Add evidence bindings to text blocks and validator support**

Update `src/repo_analysis_tools/doc_dsl/models.py`:

```python
@dataclass(frozen=True)
class TextBlock:
    text: str
    evidence_bindings: list[EvidenceBinding] = field(default_factory=list)
    title: str | None = None
```

Update `src/repo_analysis_tools/doc_dsl/validators.py`:

```python
from repo_analysis_tools.doc_dsl.models import Document, MermaidBlock, TextBlock


def _has_evidence_bound_block(section) -> bool:
    for block in section.blocks:
        if isinstance(block, TextBlock) and block.evidence_bindings:
            return True
        if isinstance(block, MermaidBlock) and block.evidence_bindings:
            return True
    return False


def validate_document(document: Document, spec: DocumentSpec) -> list[str]:
    errors: list[str] = []
    section_titles = {section.title for section in document.sections}

    for required_section in spec.required_sections:
        if required_section not in section_titles:
            errors.append(f"missing required section '{required_section}'")

    for section in document.sections:
        policy = spec.section_policies.get(section.title)
        if policy is None:
            errors.append(f"unexpected section '{section.title}'")
            continue

        mermaid_blocks = [block for block in section.blocks if isinstance(block, MermaidBlock)]
        if policy.mermaid_policy == "required" and not mermaid_blocks:
            errors.append(f"section '{section.title}' requires at least one MermaidBlock")
        if policy.mermaid_policy == "disallowed" and mermaid_blocks:
            errors.append(f"section '{section.title}' disallows MermaidBlock")
        if policy.requires_evidence_bindings and not _has_evidence_bound_block(section):
            errors.append(f"section '{section.title}' requires evidence-bound blocks")

    return errors
```

- [ ] **Step 5: Add repository-design builders and renderer support**

Append to `src/repo_analysis_tools/doc_dsl/builders.py`:

```python
def build_repo_architecture_document(package: RepositoryFindingsPackage) -> Document:
    architecture_bindings = _bindings_from_payload(package.global_findings.citations)
    return Document(
        document_type="repo-architecture",
        title=f"{package.repo_name} Repository Architecture",
        sections=[
            Section("Overview", [TextBlock(package.global_findings.architecture_summary[0], architecture_bindings)]),
            Section("System Boundaries", [TextBlock("\n".join(package.global_findings.architecture_summary), architecture_bindings)]),
            Section(
                "Runtime Flow",
                [
                    MermaidBlock(
                        diagram_kind="flowchart",
                        source=_runtime_flow_mermaid(package.global_findings.cross_module_flows),
                        caption="Whole-repository runtime flow derived from the structured findings package.",
                        placement="inline",
                        evidence_bindings=architecture_bindings,
                        title="Repository Runtime Flow",
                    )
                ],
            ),
            Section("Constraints", [TextBlock("\n".join(package.global_findings.constraints), architecture_bindings)]),
            Section("Unknowns", [TextBlock("\n".join(package.global_findings.unknowns))]),
        ],
    )
```

Update `src/repo_analysis_tools/renderers/markdown.py` so text blocks emit citations just like Mermaid blocks:

```python
                if isinstance(block, TextBlock):
                    if block.title is not None:
                        lines.extend([f"### {block.title}", ""])
                    lines.append(block.text)
                    evidence_lines = render_evidence_bindings(block.evidence_bindings)
                    if evidence_lines:
                        lines.extend(["", *evidence_lines])
                    continue
```

- [ ] **Step 6: Run the document pipeline tests and verify they pass**

Run:

```bash
/home/hyx/anaconda3/envs/agent/bin/python -m unittest tests.unit.test_document_dsl tests.unit.test_report_service -v
```

Expected: PASS with the new registry rows, evidence-binding validation, renderer output, and existing report-service coverage all green.

- [ ] **Step 7: Commit the pipeline extension**

```bash
git add src/repo_analysis_tools/doc_specs src/repo_analysis_tools/doc_dsl/models.py src/repo_analysis_tools/doc_dsl/validators.py src/repo_analysis_tools/doc_dsl/builders.py src/repo_analysis_tools/renderers/markdown.py tests/unit/test_document_dsl.py tests/unit/test_report_service.py
git commit -m "feat: add repository design document types"
```

### Task 2: Add A Deterministic Repository Design Writer Service And CLI

**Files:**
- Create: `src/repo_analysis_tools/report/repo_design_models.py`
- Create: `src/repo_analysis_tools/report/repo_design_service.py`
- Create: `tools/write_repo_design_docs.py`
- Create: `tests/unit/test_repo_doc_writer_service.py`
- Create: `tests/integration/test_repo_doc_writer_workflow.py`

- [ ] **Step 1: Write the failing unit and integration tests for the document-set writer**

Create `tests/unit/test_repo_doc_writer_service.py`:

```python
import tempfile
import unittest
from pathlib import Path

from repo_analysis_tools.report.repo_design_models import RepositoryFindingsPackage
from repo_analysis_tools.report.repo_design_service import RepositoryDesignWriter


class RepoDocWriterServiceTest(unittest.TestCase):
    def sample_payload(self, output_root: Path) -> dict[str, object]:
        return {
            "repo_name": "repo-analysis-tools",
            "target_repo": output_root.parents[1].as_posix(),
            "output_root": output_root.as_posix(),
            "module_map": [
                {
                    "module_id": "query",
                    "module_name": "Query",
                    "responsibility": "Symbol and graph queries",
                    "paths": ["src/repo_analysis_tools/query"],
                    "dependencies": ["scan", "anchors", "scope"],
                },
                {
                    "module_id": "mcp",
                    "module_name": "MCP",
                    "responsibility": "FastMCP wrappers for the active tool surface",
                    "paths": ["src/repo_analysis_tools/mcp"],
                    "dependencies": ["query"],
                },
            ],
            "module_reports": [
                {
                    "module_id": "query",
                    "summary": ["Provides file, symbol, and call-path lookups."],
                    "entry_points": ["QueryService.resolve_symbols"],
                    "key_symbols": ["QueryService"],
                    "call_flows": ["query_tools -> QueryService -> scope/anchors stores"],
                    "risks": ["Depends on the in-process scan registry."],
                    "unknowns": ["No benchmark data for very large repositories."],
                    "citations": [
                        {
                            "file_path": "src/repo_analysis_tools/query/service.py",
                            "line_start": 1,
                            "line_end": 120,
                            "symbol_name": "QueryService",
                        }
                    ],
                },
                {
                    "module_id": "mcp",
                    "summary": ["Wraps query services with FastMCP tools."],
                    "entry_points": ["list_priority_files", "resolve_symbols"],
                    "key_symbols": ["query_tools"],
                    "call_flows": ["mcp server -> query_tools -> QueryService"],
                    "risks": ["Relies on scan registry state in-process."],
                    "unknowns": [],
                    "citations": [
                        {
                            "file_path": "src/repo_analysis_tools/mcp/tools/query_tools.py",
                            "line_start": 1,
                            "line_end": 220,
                            "symbol_name": None,
                        }
                    ],
                },
            ],
            "global_findings": {
                "architecture_summary": ["The active surface is query-first and scan-rooted."],
                "cross_module_flows": ["scan -> scope -> anchors -> query -> mcp"],
                "constraints": ["No active report MCP surface is exposed."],
                "unknowns": ["No subagent-run telemetry exists yet."],
                "citations": [
                    {
                        "file_path": "docs/architecture.md",
                        "line_start": 1,
                        "line_end": 120,
                        "symbol_name": None,
                    }
                ],
            },
        }

    def test_write_document_set_creates_required_files_and_manifest(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            output_root = Path(tmpdir) / "repo" / "docs" / "repo-design"
            package = RepositoryFindingsPackage.from_dict(self.sample_payload(output_root))

            manifest = RepositoryDesignWriter().write_document_set(package)

            self.assertEqual(manifest.validation_status, "ok")
            self.assertEqual(
                {document.relative_path for document in manifest.documents},
                {
                    "index.md",
                    "repository-architecture.md",
                    "module-map.md",
                    "evidence-index.md",
                    "modules/query.md",
                    "modules/mcp.md",
                },
            )
            self.assertTrue((output_root / "manifest.json").is_file())
            architecture_markdown = (output_root / "repository-architecture.md").read_text(encoding="utf-8")
            self.assertIn("```mermaid", architecture_markdown)
            self.assertIn("docs/architecture.md:1-120", architecture_markdown)
```

Create `tests/integration/test_repo_doc_writer_workflow.py`:

```python
import json
import subprocess
import tempfile
import unittest
from pathlib import Path


class RepoDocWriterWorkflowTest(unittest.TestCase):
    def test_cli_writes_document_set_from_json_input(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            repo_root = Path(tmpdir) / "repo"
            output_root = repo_root / "docs" / "repo-design"
            input_path = Path(tmpdir) / "repo-doc-input.json"
            input_path.write_text(
                json.dumps(
                    {
                        "repo_name": "repo-analysis-tools",
                        "target_repo": repo_root.as_posix(),
                        "output_root": output_root.as_posix(),
                        "module_map": [],
                        "module_reports": [],
                        "global_findings": {
                            "architecture_summary": ["Minimal architecture summary."],
                            "cross_module_flows": ["query -> mcp"],
                            "constraints": ["No report MCP surface."],
                            "unknowns": ["No module reports supplied."],
                            "citations": [
                                {
                                    "file_path": "docs/architecture.md",
                                    "line_start": 1,
                                    "line_end": 20,
                                    "symbol_name": None,
                                }
                            ],
                        },
                    }
                ),
                encoding="utf-8",
            )

            completed = subprocess.run(
                [
                    "/home/hyx/anaconda3/envs/agent/bin/python",
                    "tools/write_repo_design_docs.py",
                    "--input",
                    str(input_path),
                ],
                cwd=repo_root,
                text=True,
                capture_output=True,
                check=False,
            )

            self.assertEqual(completed.returncode, 0, completed.stderr)
            self.assertTrue((output_root / "manifest.json").is_file())
            payload = json.loads((output_root / "manifest.json").read_text(encoding="utf-8"))
            self.assertEqual(payload["validation_status"], "ok")
```

- [ ] **Step 2: Run the writer tests and verify they fail**

Run:

```bash
/home/hyx/anaconda3/envs/agent/bin/python -m unittest tests.unit.test_repo_doc_writer_service tests.integration.test_repo_doc_writer_workflow -v
```

Expected: FAIL with `ModuleNotFoundError` for `repo_analysis_tools.report.repo_design_service` and a missing CLI script.

- [ ] **Step 3: Add typed findings-package and manifest models**

Create `src/repo_analysis_tools/report/repo_design_models.py`:

```python
from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class CitationInput:
    file_path: str
    line_start: int
    line_end: int
    symbol_name: str | None = None

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "CitationInput":
        return cls(
            file_path=str(payload["file_path"]),
            line_start=int(payload["line_start"]),
            line_end=int(payload["line_end"]),
            symbol_name=None if payload.get("symbol_name") is None else str(payload["symbol_name"]),
        )


@dataclass(frozen=True)
class ModuleDescriptor:
    module_id: str
    module_name: str
    responsibility: str
    paths: list[str]
    dependencies: list[str]


@dataclass(frozen=True)
class ModuleReport:
    module_id: str
    summary: list[str]
    entry_points: list[str]
    key_symbols: list[str]
    call_flows: list[str]
    risks: list[str]
    unknowns: list[str]
    citations: list[CitationInput]


@dataclass(frozen=True)
class GlobalFindings:
    architecture_summary: list[str]
    cross_module_flows: list[str]
    constraints: list[str]
    unknowns: list[str]
    citations: list[CitationInput]


@dataclass(frozen=True)
class RepositoryFindingsPackage:
    repo_name: str
    target_repo: str
    output_root: str
    module_map: list[ModuleDescriptor]
    module_reports: list[ModuleReport]
    global_findings: GlobalFindings

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "RepositoryFindingsPackage":
        ...


@dataclass(frozen=True)
class GeneratedDocument:
    document_type: str
    relative_path: str
    title: str


@dataclass(frozen=True)
class RepositoryDesignManifest:
    output_root: str
    validation_status: str
    documents: list[GeneratedDocument]
    unknown_count: int

    def to_dict(self) -> dict[str, Any]:
        ...
```

- [ ] **Step 4: Add the repository design writer service and CLI**

Create `src/repo_analysis_tools/report/repo_design_service.py`:

```python
from __future__ import annotations

import json
from pathlib import Path

from repo_analysis_tools.doc_dsl.builders import (
    build_evidence_index_document,
    build_module_detail_document,
    build_module_map_document,
    build_repo_architecture_document,
)
from repo_analysis_tools.doc_dsl.models import MermaidBlock
from repo_analysis_tools.doc_dsl.validators import validate_document
from repo_analysis_tools.doc_specs.base import build_document_spec_registry
from repo_analysis_tools.doc_dsl.mermaid_validator import MermaidValidator
from repo_analysis_tools.renderers.markdown import MarkdownRenderer
from repo_analysis_tools.report.repo_design_models import (
    GeneratedDocument,
    RepositoryDesignManifest,
    RepositoryFindingsPackage,
)


class RepositoryDesignWriter:
    def __init__(
        self,
        *,
        renderer: MarkdownRenderer | None = None,
        mermaid_validator: MermaidValidator | None = None,
    ) -> None:
        self.renderer = renderer or MarkdownRenderer()
        self.mermaid_validator = mermaid_validator or MermaidValidator()

    def write_document_set(self, package: RepositoryFindingsPackage) -> RepositoryDesignManifest:
        output_root = Path(package.output_root)
        output_root.mkdir(parents=True, exist_ok=True)
        (output_root / "modules").mkdir(parents=True, exist_ok=True)

        documents = [
            ("index.md", self._build_index_markdown(package)),
            ("repository-architecture.md", self._render_document(build_repo_architecture_document(package))),
            ("module-map.md", self._render_document(build_module_map_document(package))),
            ("evidence-index.md", self._render_document(build_evidence_index_document(package))),
        ]

        manifest_rows: list[GeneratedDocument] = []
        for relative_path, rendered in documents:
            target_path = output_root / relative_path
            target_path.write_text(rendered["markdown"], encoding="utf-8")
            manifest_rows.append(
                GeneratedDocument(
                    document_type=rendered["document_type"],
                    relative_path=relative_path,
                    title=rendered["title"],
                )
            )

        for module in package.module_map:
            rendered = self._render_document(build_module_detail_document(package, module.module_id))
            relative_path = f"modules/{module.module_id}.md"
            (output_root / relative_path).write_text(rendered["markdown"], encoding="utf-8")
            manifest_rows.append(
                GeneratedDocument(
                    document_type=rendered["document_type"],
                    relative_path=relative_path,
                    title=rendered["title"],
                )
            )

        manifest = RepositoryDesignManifest(
            output_root=output_root.as_posix(),
            validation_status="ok",
            documents=manifest_rows,
            unknown_count=sum(len(report.unknowns) for report in package.module_reports) + len(package.global_findings.unknowns),
        )
        (output_root / "manifest.json").write_text(json.dumps(manifest.to_dict(), indent=2, sort_keys=True), encoding="utf-8")
        return manifest

    def _render_document(self, document) -> dict[str, str]:
        spec = build_document_spec_registry()[document.document_type]
        errors = validate_document(document, spec)
        if errors:
            raise ValueError("; ".join(errors))
        for section in document.sections:
            for block in section.blocks:
                if isinstance(block, MermaidBlock):
                    self.mermaid_validator.validate(block.source, diagram_kind=block.diagram_kind)
        return {
            "document_type": document.document_type,
            "title": document.title,
            "markdown": self.renderer.render(document),
        }
```

Create `tools/write_repo_design_docs.py`:

```python
from __future__ import annotations

import argparse
import json
from pathlib import Path

from repo_analysis_tools.report.repo_design_models import RepositoryFindingsPackage
from repo_analysis_tools.report.repo_design_service import RepositoryDesignWriter


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    payload = json.loads(Path(args.input).read_text(encoding="utf-8"))
    package = RepositoryFindingsPackage.from_dict(payload)
    manifest = RepositoryDesignWriter().write_document_set(package)
    print(json.dumps(manifest.to_dict(), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

- [ ] **Step 5: Run the writer tests and verify they pass**

Run:

```bash
/home/hyx/anaconda3/envs/agent/bin/python -m unittest tests.unit.test_repo_doc_writer_service tests.integration.test_repo_doc_writer_workflow -v
```

Expected: PASS with the unit test confirming the required output files and the integration test confirming the CLI can write `manifest.json`.

- [ ] **Step 6: Commit the writer service**

```bash
git add src/repo_analysis_tools/report/repo_design_models.py src/repo_analysis_tools/report/repo_design_service.py tools/write_repo_design_docs.py tests/unit/test_repo_doc_writer_service.py tests/integration/test_repo_doc_writer_workflow.py
git commit -m "feat: add repository design writer"
```

### Task 3: Add The Mirrored Subagent-Only Skill And Active Documentation

**Files:**
- Create: `.agents/skills/repo-doc-writer/SKILL.md`
- Create: `.claude/skills/repo-doc-writer/SKILL.md`
- Modify: `tests/unit/test_client_skill_distribution.py`
- Modify: `tests/smoke/test_package_layout.py`
- Modify: `tests/unit/test_architecture_docs.py`
- Modify: `README.md`
- Modify: `docs/architecture.md`

- [ ] **Step 1: Write the failing distribution and documentation tests**

Update `tests/unit/test_client_skill_distribution.py`:

```python
SKILL_NAMES = [
    "repo-doc-writer",
    "repo-understand",
]
```

Update `tests/smoke/test_package_layout.py`:

```python
EXPECTED_FILES = [
    ROOT / ".codex" / "config.toml",
    ROOT / ".mcp.json",
    ROOT / ".agents" / "skills" / "repo-doc-writer" / "SKILL.md",
    ROOT / ".agents" / "skills" / "repo-understand" / "SKILL.md",
    ROOT / ".claude" / "skills" / "repo-doc-writer" / "SKILL.md",
    ROOT / ".claude" / "skills" / "repo-understand" / "SKILL.md",
    ROOT / "docs" / "self-use-launch.md",
    ROOT / "tools" / "run_self_use_demo.py",
]
```

Update `tests/unit/test_architecture_docs.py`:

```python
REPO_DOC_WRITER_SKILL = REPO_ROOT / ".agents" / "skills" / "repo-doc-writer" / "SKILL.md"

    def test_repo_doc_writer_skill_is_subagent_scoped_and_dsl_driven(self) -> None:
        skill = self.read_text(REPO_DOC_WRITER_SKILL)

        self.assertIn("document writer subagent", skill)
        self.assertIn("Do not use this skill in the coordinating agent", skill)
        self.assertIn("doc_specs", skill)
        self.assertIn("doc_dsl", skill)
        self.assertIn("MarkdownRenderer", skill)
        self.assertIn("not free-form Markdown", skill)
        self.assertNotIn("rebuild_repo_snapshot", skill)
        self.assertNotIn("list_priority_files", skill)
```

- [ ] **Step 2: Run the skill and docs tests to verify they fail**

Run:

```bash
/home/hyx/anaconda3/envs/agent/bin/python -m unittest tests.unit.test_client_skill_distribution tests.smoke.test_package_layout tests.unit.test_architecture_docs -v
```

Expected: FAIL because the mirrored skill files do not exist and the skill wording is not yet present.

- [ ] **Step 3: Add the mirrored skill text**

Create `.agents/skills/repo-doc-writer/SKILL.md`:

````markdown
---
name: repo-doc-writer
description: Use only in a document writer subagent to turn structured repository findings into a controlled repository design document set.
---

# Repo Doc Writer Workflow

Do not use this skill in the coordinating agent.

Use this skill only in a document writer subagent after another workflow has already produced the structured repository findings package.

## Required Input

- `repo_name`
- `target_repo`
- `output_root`
- `module_map`
- `module_reports`
- `global_findings`

If any required field is missing, stop and report the missing input instead of inferring it.

## Required Workflow

```text
structured findings package
-> doc_specs selection
-> doc_dsl document objects
-> validation
-> MarkdownRenderer output
-> final document set + manifest
```

Run:

```bash
/home/hyx/anaconda3/envs/agent/bin/python tools/write_repo_design_docs.py --input <input-json-path>
```

## Safety Rules

- This skill is for a document writer subagent only.
- This workflow is not free-form Markdown drafting.
- Do not call `rebuild_repo_snapshot`, `list_priority_files`, or other repository-reading tools here.
- Do not hand-write final Markdown when the local writer service is available.
- Keep unknowns labeled as unknowns.
```
````

Copy the same file to `.claude/skills/repo-doc-writer/SKILL.md`.

- [ ] **Step 4: Update active docs to describe the new subagent-only skill**

Update `README.md` so `## Current Skills` reads:

```markdown
## Current Skills

The repository currently mirrors two active workflow skills across [`.agents/skills`](./.agents/skills) and [`.claude/skills`](./.claude/skills):

- `repo-understand`
- `repo-doc-writer`

### `repo-doc-writer`

- Purpose: generate a controlled repository design document set from structured findings.
- Scope: document-writer subagent only.
- Constraint: final Markdown must come from the typed document pipeline rather than free-form drafting.
```

Append to `docs/architecture.md`:

````markdown
## Repository Design Document Handoff

Repository design documentation is produced through a subagent-only handoff:

```text
repository audit workflow
-> structured findings package
-> document writer subagent loads `repo-doc-writer`
-> doc_specs / doc_dsl / validators / MarkdownRenderer
-> docs/repo-design/*
```

The coordinating agent remains orchestration-only and does not absorb section policy or renderer rules.
```
````

- [ ] **Step 5: Run the skill and docs tests and verify they pass**

Run:

```bash
/home/hyx/anaconda3/envs/agent/bin/python -m unittest tests.unit.test_client_skill_distribution tests.smoke.test_package_layout tests.unit.test_architecture_docs -v
```

Expected: PASS with mirrored-skill distribution, package layout, and subagent-only wording assertions all green.

- [ ] **Step 6: Commit the mirrored skill and docs**

```bash
git add .agents/skills/repo-doc-writer/SKILL.md .claude/skills/repo-doc-writer/SKILL.md tests/unit/test_client_skill_distribution.py tests/smoke/test_package_layout.py tests/unit/test_architecture_docs.py README.md docs/architecture.md
git commit -m "feat: add repo-doc-writer skill"
```

## Final Verification

- [ ] Run:

```bash
/home/hyx/anaconda3/envs/agent/bin/python -m unittest tests.unit.test_document_dsl tests.unit.test_report_service tests.unit.test_repo_doc_writer_service tests.integration.test_repo_doc_writer_workflow tests.unit.test_client_skill_distribution tests.smoke.test_package_layout tests.unit.test_architecture_docs -v
```

Expected: PASS with the document pipeline, writer service, CLI workflow, and mirrored skill assertions all green.

- [ ] Run:

```bash
git status --short
```

Expected: empty output.

## Spec Coverage Check

- The coordinating-agent boundary is implemented in Task 3 through mirrored skill text and architecture documentation.
- The structured findings-package input contract is implemented in Task 2 through typed models and CLI loading.
- The multi-document output contract is implemented in Task 2 through `RepositoryDesignWriter` and `manifest.json`.
- The controlled document pipeline requirement is implemented in Task 1 and reused in Task 2.
- The fallback-to-local-Python rule is satisfied because the writer service and CLI run on local Python code while still using `doc_specs`, `doc_dsl`, validators, and `MarkdownRenderer`.

## Placeholder Scan

- No `TBD`, `TODO`, or “implement later” markers remain.
- Every code-touching step contains the exact file path and a concrete code shape.
- Every verification step includes a concrete command and expected outcome.
