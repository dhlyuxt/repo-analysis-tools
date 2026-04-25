from repo_analysis_tools.doc_specs.base import DocumentSpec, SectionPolicy


EVIDENCE_INDEX_SPEC = DocumentSpec(
    document_type="evidence-index",
    required_sections=("Coverage", "Claims", "Unknowns"),
    section_policies={
        "Coverage": SectionPolicy("Coverage", "allowed", requires_evidence_bindings=True),
        "Claims": SectionPolicy("Claims", "allowed", requires_evidence_bindings=True),
        "Unknowns": SectionPolicy("Unknowns", "allowed", requires_evidence_bindings=False),
    },
)
