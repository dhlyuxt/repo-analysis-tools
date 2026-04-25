from repo_analysis_tools.doc_specs.base import DocumentSpec, SectionPolicy


REPO_ARCHITECTURE_SPEC = DocumentSpec(
    document_type="repo-architecture",
    required_sections=(
        "Overview",
        "System Boundaries",
        "Runtime Flow",
        "Constraints",
        "Unknowns",
    ),
    section_policies={
        "Overview": SectionPolicy("Overview", "allowed", requires_evidence_bindings=True),
        "System Boundaries": SectionPolicy(
            "System Boundaries", "allowed", requires_evidence_bindings=True
        ),
        "Runtime Flow": SectionPolicy(
            "Runtime Flow", "required", requires_evidence_bindings=True
        ),
        "Constraints": SectionPolicy(
            "Constraints", "allowed", requires_evidence_bindings=True
        ),
        "Unknowns": SectionPolicy("Unknowns", "allowed", requires_evidence_bindings=False),
    },
)
