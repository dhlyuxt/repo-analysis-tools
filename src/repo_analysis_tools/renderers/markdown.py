from repo_analysis_tools.doc_dsl.models import Document, MermaidBlock, TextBlock
from repo_analysis_tools.renderers.citations import render_evidence_bindings
from repo_analysis_tools.renderers.sections import render_section_heading


class MarkdownRenderer:
    def render(self, document: Document) -> str:
        lines: list[str] = [f"# {document.title}"]
        for section in document.sections:
            lines.extend(["", render_section_heading(section)])
            for block in section.blocks:
                lines.append("")
                if isinstance(block, TextBlock):
                    lines.append(block.text)
                    continue
                if block.title is not None:
                    lines.extend([f"### {block.title}", ""])
                lines.extend(
                    [
                        "```mermaid",
                        block.source.rstrip(),
                        "```",
                        "",
                        block.caption,
                    ]
                )
                evidence_lines = render_evidence_bindings(block.evidence_bindings)
                if evidence_lines:
                    lines.extend(["", *evidence_lines])
        return "\n".join(lines) + "\n"
