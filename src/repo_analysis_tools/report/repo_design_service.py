from __future__ import annotations

import json
from pathlib import Path

from repo_analysis_tools.doc_dsl.builders import (
    build_evidence_index_document,
    build_module_detail_document,
    build_module_map_document,
    build_reading_order_document,
    build_repo_architecture_document,
)
from repo_analysis_tools.doc_dsl.mermaid_validator import MermaidValidator
from repo_analysis_tools.doc_dsl.models import Document, MermaidBlock
from repo_analysis_tools.doc_dsl.validators import validate_document
from repo_analysis_tools.doc_specs.base import build_document_spec_registry
from repo_analysis_tools.renderers.markdown import MarkdownRenderer
from repo_analysis_tools.report.repo_design_models import (
    GeneratedDocument,
    RepositoryDesignManifest,
    RepositoryFindingsPackage,
)


class RepositoryDesignWriter:
    def __init__(
        self,
        renderer: MarkdownRenderer | None = None,
        mermaid_validator: MermaidValidator | None = None,
    ) -> None:
        self.renderer = renderer or MarkdownRenderer()
        self.mermaid_validator = mermaid_validator or MermaidValidator()
        self.spec_registry = build_document_spec_registry()

    def write_document_set(
        self, package: RepositoryFindingsPackage
    ) -> RepositoryDesignManifest:
        self._validate_module_report_coverage(package)

        output_root = Path(package.output_root)
        modules_root = output_root / "modules"
        output_root.mkdir(parents=True, exist_ok=True)
        modules_root.mkdir(parents=True, exist_ok=True)

        controlled_documents: list[tuple[str, Document]] = [
            ("index.md", build_reading_order_document(package)),
            ("repository-architecture.md", build_repo_architecture_document(package)),
            ("module-map.md", build_module_map_document(package)),
            ("evidence-index.md", build_evidence_index_document(package)),
        ]
        for module in package.module_map:
            controlled_documents.append(
                (
                    f"modules/{module.module_id}.md",
                    build_module_detail_document(package, module.module_id),
                )
            )

        self._validate_unique_relative_paths(controlled_documents)
        rendered_documents = [
            (relative_path, document, self._validate_and_render(document))
            for relative_path, document in controlled_documents
        ]

        documents = [
            GeneratedDocument(
                document_type=document.document_type,
                relative_path=relative_path,
                title=document.title,
            )
            for relative_path, document, _markdown in rendered_documents
        ]

        for relative_path, _document, markdown in rendered_documents:
            (output_root / relative_path).write_text(markdown, encoding="utf-8")

        manifest = RepositoryDesignManifest(
            output_root=str(output_root),
            validation_status="ok",
            documents=documents,
            unknown_count=self._unknown_count(package),
        )
        (output_root / "manifest.json").write_text(
            json.dumps(manifest.to_dict(), indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        return manifest

    def _validate_and_render(self, document: Document) -> str:
        spec = self.spec_registry[document.document_type]
        errors = validate_document(document, spec)
        if errors:
            raise ValueError(f"{document.document_type}: {'; '.join(errors)}")
        for section in document.sections:
            for block in section.blocks:
                if isinstance(block, MermaidBlock):
                    self.mermaid_validator.validate(block.source, diagram_kind=block.diagram_kind)
        return self.renderer.render(document)

    def _validate_unique_relative_paths(
        self, documents: list[tuple[str, Document]]
    ) -> None:
        seen: set[str] = set()
        for relative_path, _document in documents:
            if relative_path in seen:
                raise ValueError(f"duplicate generated document path: {relative_path}")
            seen.add(relative_path)

    def _validate_module_report_coverage(self, package: RepositoryFindingsPackage) -> None:
        module_ids = {module.module_id for module in package.module_map}
        report_ids = {report.module_id for report in package.module_reports}
        missing = sorted(module_ids - report_ids)
        orphaned = sorted(report_ids - module_ids)
        if missing:
            raise ValueError(f"missing module_reports for module ids: {', '.join(missing)}")
        if orphaned:
            raise ValueError(f"orphan module_reports for module ids: {', '.join(orphaned)}")

    def _unknown_count(self, package: RepositoryFindingsPackage) -> int:
        return len(package.global_findings.unknowns) + sum(
            len(report.unknowns) for report in package.module_reports
        )
