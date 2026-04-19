from repo_analysis_tools.doc_specs.base import DocumentSpec, SectionPolicy


ISSUE_ANALYSIS_SPEC = DocumentSpec(
    document_type="issue-analysis",
    required_sections=("Issue Summary", "Evidence", "Causal Chain", "Unknowns", "Recommendations"),
    section_policies={
        "Issue Summary": SectionPolicy("Issue Summary", "allowed"),
        "Evidence": SectionPolicy("Evidence", "allowed"),
        "Causal Chain": SectionPolicy("Causal Chain", "required"),
        "Unknowns": SectionPolicy("Unknowns", "allowed"),
        "Recommendations": SectionPolicy("Recommendations", "disallowed"),
    },
)
