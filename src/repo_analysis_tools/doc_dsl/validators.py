from __future__ import annotations

from repo_analysis_tools.doc_dsl.models import Document, MermaidBlock
from repo_analysis_tools.doc_specs.base import DocumentSpec


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

    return errors
