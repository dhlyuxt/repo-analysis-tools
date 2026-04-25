from repo_analysis_tools.doc_specs.base import DocumentSpec, SectionPolicy


MODULE_DETAIL_SPEC = DocumentSpec(
    document_type="module-detail",
    required_sections=(
        "Responsibility",
        "Entry Points",
        "Internal Flow",
        "Dependencies",
        "Risks",
        "Unknowns",
    ),
    section_policies={
        "Responsibility": SectionPolicy(
            "Responsibility", "allowed", requires_evidence_bindings=True
        ),
        "Entry Points": SectionPolicy(
            "Entry Points", "allowed", requires_evidence_bindings=True
        ),
        "Internal Flow": SectionPolicy(
            "Internal Flow", "required", requires_evidence_bindings=True
        ),
        "Dependencies": SectionPolicy(
            "Dependencies", "allowed", requires_evidence_bindings=True
        ),
        "Risks": SectionPolicy("Risks", "allowed", requires_evidence_bindings=True),
        "Unknowns": SectionPolicy("Unknowns", "allowed", requires_evidence_bindings=False),
    },
)
