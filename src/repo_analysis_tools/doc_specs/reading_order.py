from repo_analysis_tools.doc_specs.base import DocumentSpec, SectionPolicy


READING_ORDER_SPEC = DocumentSpec(
    document_type="reading-order",
    required_sections=("Reading Order", "Source"),
    section_policies={
        "Reading Order": SectionPolicy("Reading Order", "disallowed"),
        "Source": SectionPolicy("Source", "disallowed"),
    },
)
