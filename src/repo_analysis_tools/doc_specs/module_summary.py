from repo_analysis_tools.doc_specs.base import DocumentSpec, SectionPolicy


MODULE_SUMMARY_SPEC = DocumentSpec(
    document_type="module-summary",
    required_sections=("Summary", "Key Anchors", "Call Flow", "Risks", "Recommendations"),
    section_policies={
        "Summary": SectionPolicy("Summary", "allowed"),
        "Key Anchors": SectionPolicy("Key Anchors", "allowed"),
        "Call Flow": SectionPolicy("Call Flow", "required"),
        "Risks": SectionPolicy("Risks", "allowed"),
        "Recommendations": SectionPolicy("Recommendations", "disallowed"),
    },
)
