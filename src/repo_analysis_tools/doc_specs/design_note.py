from repo_analysis_tools.doc_specs.base import DocumentSpec, SectionPolicy


DESIGN_NOTE_SPEC = DocumentSpec(
    document_type="design-note",
    required_sections=("Context", "Proposed Design", "Flow", "Tradeoffs", "Open Questions"),
    section_policies={
        "Context": SectionPolicy("Context", "allowed"),
        "Proposed Design": SectionPolicy("Proposed Design", "allowed"),
        "Flow": SectionPolicy("Flow", "required"),
        "Tradeoffs": SectionPolicy("Tradeoffs", "allowed"),
        "Open Questions": SectionPolicy("Open Questions", "disallowed"),
    },
)
