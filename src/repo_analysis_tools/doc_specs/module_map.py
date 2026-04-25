from repo_analysis_tools.doc_specs.base import DocumentSpec, SectionPolicy


MODULE_MAP_SPEC = DocumentSpec(
    document_type="module-map",
    required_sections=("Module Inventory", "Dependency Graph", "Coverage Notes", "Unknowns"),
    section_policies={
        "Module Inventory": SectionPolicy(
            "Module Inventory", "allowed", requires_evidence_bindings=True
        ),
        "Dependency Graph": SectionPolicy(
            "Dependency Graph", "required", requires_evidence_bindings=True
        ),
        "Coverage Notes": SectionPolicy(
            "Coverage Notes", "allowed", requires_evidence_bindings=True
        ),
        "Unknowns": SectionPolicy("Unknowns", "allowed", requires_evidence_bindings=False),
    },
)
