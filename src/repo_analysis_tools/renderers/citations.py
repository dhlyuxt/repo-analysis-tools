from repo_analysis_tools.doc_dsl.models import EvidenceBinding


def render_evidence_bindings(bindings: list[EvidenceBinding]) -> list[str]:
    rendered: list[str] = []
    for binding in bindings:
        if binding.line_start is not None and binding.line_end is not None:
            rendered.append(f"- `{binding.file_path}:{binding.line_start}-{binding.line_end}`")
        else:
            rendered.append(f"- `{binding.file_path}`")
    return rendered
