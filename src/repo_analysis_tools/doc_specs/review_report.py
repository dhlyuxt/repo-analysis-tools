from repo_analysis_tools.doc_specs.base import DocumentSpec, SectionPolicy


REVIEW_REPORT_SPEC = DocumentSpec(
    document_type="review-report",
    required_sections=("Scope", "Findings", "Risk Map", "Unknowns", "Next Steps"),
    section_policies={
        "Scope": SectionPolicy("Scope", "allowed"),
        "Findings": SectionPolicy("Findings", "allowed"),
        "Risk Map": SectionPolicy("Risk Map", "required"),
        "Unknowns": SectionPolicy("Unknowns", "allowed"),
        "Next Steps": SectionPolicy("Next Steps", "disallowed"),
    },
)
