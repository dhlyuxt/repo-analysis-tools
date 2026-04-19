from repo_analysis_tools.doc_dsl.models import Section


def render_section_heading(section: Section) -> str:
    return f"## {section.title}"
