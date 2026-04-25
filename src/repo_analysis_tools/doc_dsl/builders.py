from __future__ import annotations

from repo_analysis_tools.doc_dsl.models import Document, EvidenceBinding, MermaidBlock, Section, TextBlock
from repo_analysis_tools.evidence.models import EvidencePack
from repo_analysis_tools.report.repo_design_models import (
    CitationInput,
    ModuleDescriptor,
    ModuleReport,
    RepositoryFindingsPackage,
)


def _bindings_from_evidence(evidence_pack: EvidencePack) -> list[EvidenceBinding]:
    return [
        EvidenceBinding(
            file_path=citation.file_path,
            anchor_name=citation.anchor_name,
            line_start=citation.line_start,
            line_end=citation.line_end,
        )
        for citation in evidence_pack.citations[:3]
    ]


def build_module_summary_document(evidence_pack: EvidencePack, module_name: str) -> Document:
    bindings = _bindings_from_evidence(evidence_pack)
    anchor_labels = ", ".join(binding.anchor_name or binding.file_path for binding in bindings)
    return Document(
        document_type="module-summary",
        title=f"Module Summary: {module_name}",
        sections=[
            Section("Summary", [TextBlock(f"Evidence-backed summary for module {module_name}.")]),
            Section("Key Anchors", [TextBlock(anchor_labels or evidence_pack.summary)]),
            Section(
                "Call Flow",
                [
                    MermaidBlock(
                        diagram_kind="flowchart",
                        source="flowchart LR\nQuestion --> Evidence --> Module\n",
                        caption="High-level module flow derived from the selected evidence.",
                        placement="inline",
                        evidence_bindings=bindings,
                        title="Module Flow",
                    ),
                ],
            ),
            Section("Risks", [TextBlock("Risk statements stay tied to cited evidence.")]),
            Section("Recommendations", [TextBlock("Prefer follow-up slices for deeper inspection.")]),
        ],
    )


def build_issue_analysis_document(evidence_pack: EvidencePack, issue_title: str) -> Document:
    bindings = _bindings_from_evidence(evidence_pack)
    return Document(
        document_type="issue-analysis",
        title=f"Issue Analysis: {issue_title}",
        sections=[
            Section("Issue Summary", [TextBlock(issue_title)]),
            Section("Evidence", [TextBlock(evidence_pack.summary)]),
            Section(
                "Causal Chain",
                [
                    MermaidBlock(
                        diagram_kind="flowchart",
                        source="flowchart TD\nSymptom --> Evidence --> SuspectedCause\n",
                        caption="Causal chain grounded in the selected evidence pack.",
                        placement="inline",
                        evidence_bindings=bindings,
                        title="Causal Chain",
                    ),
                ],
            ),
            Section("Unknowns", [TextBlock("List unresolved questions before concluding.")]),
            Section("Recommendations", [TextBlock("Recommend the next evidence-backed follow-up.")]),
        ],
    )


def build_design_note_document(focus: str) -> Document:
    return Document(
        document_type="design-note",
        title=f"Design Note: {focus}",
        sections=[
            Section("Context", [TextBlock(f"Design context for {focus}.")]),
            Section("Proposed Design", [TextBlock("Describe the proposed structure in concise terms.")]),
            Section(
                "Flow",
                [
                    MermaidBlock(
                        diagram_kind="flowchart",
                        source="flowchart LR\nInput --> Decision --> Output\n",
                        caption="Proposed flow for the design note.",
                        placement="inline",
                        evidence_bindings=[],
                        title="Proposed Flow",
                    ),
                ],
            ),
            Section("Tradeoffs", [TextBlock("Record the main tradeoffs explicitly.")]),
            Section("Open Questions", [TextBlock("List remaining unresolved design questions.")]),
        ],
    )


def build_review_report_document(evidence_pack: EvidencePack, title: str) -> Document:
    bindings = _bindings_from_evidence(evidence_pack)
    return Document(
        document_type="review-report",
        title=title,
        sections=[
            Section("Scope", [TextBlock(evidence_pack.summary)]),
            Section("Findings", [TextBlock("Summarize the evidence-backed findings.")]),
            Section(
                "Risk Map",
                [
                    MermaidBlock(
                        diagram_kind="flowchart",
                        source="flowchart TD\nFinding --> Risk --> NextStep\n",
                        caption="Risk map for the reviewed focus area.",
                        placement="inline",
                        evidence_bindings=bindings,
                        title="Risk Map",
                    ),
                ],
            ),
            Section("Unknowns", [TextBlock("Call out any remaining blind spots.")]),
            Section("Next Steps", [TextBlock("Recommend the next bounded workflow step.")]),
        ],
    )


def build_repo_architecture_document(package: RepositoryFindingsPackage) -> Document:
    bindings = _bindings_from_citations(package.global_findings.citations)
    return Document(
        document_type="repo-architecture",
        title=f"{package.repo_name} Repository Architecture",
        sections=[
            Section(
                "Overview",
                [
                    TextBlock(
                        _bullet_list(
                            package.global_findings.architecture_summary,
                            "No architecture summary reported.",
                        ),
                        evidence_bindings=bindings,
                    )
                ],
            ),
            Section(
                "System Boundaries",
                [
                    TextBlock(
                        _system_boundaries_text(package),
                        evidence_bindings=bindings,
                    )
                ],
            ),
            Section(
                "Runtime Flow",
                [
                    MermaidBlock(
                        diagram_kind="flowchart",
                        source=_module_flowchart(package.module_map, package.global_findings.cross_module_flows),
                        caption="Cross-module runtime flow derived from structured findings.",
                        placement="inline",
                        evidence_bindings=bindings,
                        title="Cross-Module Flow",
                    )
                ],
            ),
            Section(
                "Constraints",
                [
                    TextBlock(
                        _bullet_list(package.global_findings.constraints, "No constraints reported."),
                        evidence_bindings=bindings,
                    )
                ],
            ),
            Section(
                "Unknowns",
                [TextBlock(_bullet_list(package.global_findings.unknowns, "No unknowns reported."))],
            ),
        ],
    )


def build_module_map_document(package: RepositoryFindingsPackage) -> Document:
    bindings = _all_package_bindings(package)
    return Document(
        document_type="module-map",
        title=f"{package.repo_name} Module Map",
        sections=[
            Section(
                "Module Inventory",
                [
                    TextBlock(
                        _module_inventory_text(package.module_map),
                        evidence_bindings=bindings,
                    )
                ],
            ),
            Section(
                "Dependency Graph",
                [
                    MermaidBlock(
                        diagram_kind="flowchart",
                        source=_dependency_graph(package.module_map),
                        caption="Module dependency graph derived from the module map.",
                        placement="inline",
                        evidence_bindings=bindings,
                        title="Module Dependencies",
                    )
                ],
            ),
            Section(
                "Coverage Notes",
                [
                    TextBlock(
                        _coverage_notes_text(package),
                        evidence_bindings=bindings,
                    )
                ],
            ),
            Section(
                "Unknowns",
                [TextBlock(_package_unknowns_text(package))],
            ),
        ],
    )


def build_module_detail_document(
    package: RepositoryFindingsPackage, module_id: str
) -> Document:
    descriptor = _find_module_descriptor(package, module_id)
    report = _find_module_report(package, module_id)
    bindings = _bindings_from_citations(report.citations)
    return Document(
        document_type="module-detail",
        title=f"{descriptor.module_name} Module Detail",
        sections=[
            Section(
                "Responsibility",
                [
                    TextBlock(
                        descriptor.responsibility,
                        evidence_bindings=bindings,
                    ),
                    TextBlock(
                        _bullet_list(report.summary, "No summary reported."),
                        evidence_bindings=bindings,
                        title="Summary",
                    ),
                ],
            ),
            Section(
                "Entry Points",
                [
                    TextBlock(
                        _bullet_list(report.entry_points, "No entry points reported."),
                        evidence_bindings=bindings,
                    )
                ],
            ),
            Section(
                "Internal Flow",
                [
                    MermaidBlock(
                        diagram_kind="flowchart",
                        source=_module_internal_flowchart(report),
                        caption="Internal module flow derived from structured call flow findings.",
                        placement="inline",
                        evidence_bindings=bindings,
                        title="Internal Flow",
                    )
                ],
            ),
            Section(
                "Dependencies",
                [
                    TextBlock(
                        _module_dependencies_text(descriptor),
                        evidence_bindings=bindings,
                    )
                ],
            ),
            Section(
                "Risks",
                [
                    TextBlock(
                        _bullet_list(report.risks, "No risks reported."),
                        evidence_bindings=bindings,
                    )
                ],
            ),
            Section(
                "Unknowns",
                [TextBlock(_bullet_list(report.unknowns, "No unknowns reported."))],
            ),
        ],
    )


def build_evidence_index_document(package: RepositoryFindingsPackage) -> Document:
    bindings = _all_package_bindings(package)
    return Document(
        document_type="evidence-index",
        title=f"{package.repo_name} Evidence Index",
        sections=[
            Section(
                "Coverage",
                [
                    TextBlock(
                        _evidence_coverage_text(package),
                        evidence_bindings=bindings,
                    )
                ],
            ),
            Section(
                "Claims",
                [
                    TextBlock(
                        _evidence_claims_text(package),
                        evidence_bindings=bindings,
                    )
                ],
            ),
            Section(
                "Unknowns",
                [TextBlock(_package_unknowns_text(package))],
            ),
        ],
    )


def build_reading_order_document(package: RepositoryFindingsPackage) -> Document:
    reading_order = [
        "- [Repository Architecture](repository-architecture.md)",
        "- [Module Map](module-map.md)",
        "- [Evidence Index](evidence-index.md)",
    ]
    for module in package.module_map:
        reading_order.append(f"- [{module.module_name}](modules/{module.module_id}.md)")
    return Document(
        document_type="reading-order",
        title=f"{package.repo_name} Repository Design",
        sections=[
            Section("Reading Order", [TextBlock("\n".join(reading_order))]),
            Section("Source", [TextBlock(f"- Repository: `{package.target_repo}`")]),
        ],
    )


def _bindings_from_citations(citations: list[CitationInput]) -> list[EvidenceBinding]:
    return [
        EvidenceBinding(
            file_path=citation.file_path,
            anchor_name=citation.symbol_name,
            line_start=citation.line_start,
            line_end=citation.line_end,
        )
        for citation in citations
    ]


def _all_package_bindings(package: RepositoryFindingsPackage) -> list[EvidenceBinding]:
    citations = list(package.global_findings.citations)
    for report in package.module_reports:
        citations.extend(report.citations)
    return _bindings_from_citations(citations)


def _find_module_descriptor(
    package: RepositoryFindingsPackage, module_id: str
) -> ModuleDescriptor:
    for descriptor in package.module_map:
        if descriptor.module_id == module_id:
            return descriptor
    raise ValueError(f"module_id has no matching ModuleDescriptor: {module_id}")


def _find_module_report(package: RepositoryFindingsPackage, module_id: str) -> ModuleReport:
    for report in package.module_reports:
        if report.module_id == module_id:
            return report
    raise ValueError(f"module_id has no matching ModuleReport: {module_id}")


def _bullet_list(items: list[str], empty_text: str) -> str:
    if not items:
        return empty_text
    return "\n".join(f"- {item}" for item in items)


def _system_boundaries_text(package: RepositoryFindingsPackage) -> str:
    if not package.module_map:
        return "No modules reported."
    lines = [
        f"- {module.module_name} ({module.module_id}): {', '.join(module.paths) or 'no paths reported'}"
        for module in package.module_map
    ]
    return "\n".join(lines)


def _module_inventory_text(modules: list[ModuleDescriptor]) -> str:
    if not modules:
        return "No modules reported."
    lines = []
    for module in modules:
        dependencies = ", ".join(module.dependencies) if module.dependencies else "none"
        paths = ", ".join(module.paths) if module.paths else "none"
        lines.append(
            f"- {module.module_name} ({module.module_id}): {module.responsibility} "
            f"Paths: {paths}. Dependencies: {dependencies}."
        )
    return "\n".join(lines)


def _coverage_notes_text(package: RepositoryFindingsPackage) -> str:
    module_count = len(package.module_map)
    report_count = len(package.module_reports)
    citation_count = len(package.global_findings.citations) + sum(
        len(report.citations) for report in package.module_reports
    )
    return (
        f"Module descriptors: {module_count}. "
        f"Module reports: {report_count}. "
        f"Evidence citations: {citation_count}."
    )


def _package_unknowns_text(package: RepositoryFindingsPackage) -> str:
    unknowns = list(package.global_findings.unknowns)
    for report in package.module_reports:
        unknowns.extend(f"{report.module_id}: {unknown}" for unknown in report.unknowns)
    return _bullet_list(unknowns, "No unknowns reported.")


def _module_dependencies_text(module: ModuleDescriptor) -> str:
    dependencies = ", ".join(module.dependencies) if module.dependencies else "No dependencies reported."
    paths = ", ".join(module.paths) if module.paths else "No paths reported."
    return f"Paths: {paths}\nDependencies: {dependencies}"


def _evidence_coverage_text(package: RepositoryFindingsPackage) -> str:
    lines = [
        f"- Global findings: {len(package.global_findings.citations)} citations",
    ]
    for report in package.module_reports:
        lines.append(f"- {report.module_id}: {len(report.citations)} citations")
    return "\n".join(lines)


def _evidence_claims_text(package: RepositoryFindingsPackage) -> str:
    lines = [
        f"- Architecture: {summary}"
        for summary in package.global_findings.architecture_summary
    ]
    if not lines:
        lines.append("- Architecture: No architecture summary reported.")
    for module in package.module_map:
        lines.append(f"- {module.module_id}: {module.responsibility}")
    for report in package.module_reports:
        for risk in report.risks:
            lines.append(f"- {report.module_id} risk: {risk}")
    return "\n".join(lines)


def _dependency_graph(modules: list[ModuleDescriptor]) -> str:
    if not modules:
        return 'flowchart TD\n    Empty["No modules reported"]'
    lines = ["flowchart TD"]
    node_ids = {module.module_id: _node_id(module.module_id, index) for index, module in enumerate(modules)}
    for module in modules:
        lines.append(f'    {node_ids[module.module_id]}["{_escape_label(module.module_name)}"]')
    for module in modules:
        for dependency in module.dependencies:
            dependency_id = node_ids.get(dependency)
            if dependency_id is None:
                dependency_id = _node_id(dependency, len(node_ids))
                node_ids[dependency] = dependency_id
                lines.append(f'    {dependency_id}["{_escape_label(dependency)}"]')
            lines.append(f"    {node_ids[module.module_id]} --> {dependency_id}")
    return "\n".join(lines)


def _module_flowchart(modules: list[ModuleDescriptor], flows: list[str]) -> str:
    if not modules and not flows:
        return 'flowchart TD\n    Empty["No runtime flows reported"]'
    lines = ["flowchart TD"]
    label_to_node: dict[str, str] = {}
    for index, module in enumerate(modules):
        node_id = _node_id(module.module_id, index)
        label_to_node[module.module_id] = node_id
        label_to_node[module.module_name] = node_id
        lines.append(f'    {node_id}["{_escape_label(module.module_name)}"]')
    flow_edges = _parse_flow_edges(flows)
    if not flow_edges and flows:
        for index, flow in enumerate(flows):
            node_id = _node_id(f"flow_{index}", len(label_to_node) + index)
            lines.append(f'    {node_id}["{_escape_label(flow)}"]')
    for source, target in flow_edges:
        source_id = _node_for_label(source, label_to_node)
        target_id = _node_for_label(target, label_to_node)
        lines.append(f"    {source_id} --> {target_id}")
    if not flows and len(modules) == 1:
        lines.append(f"    {label_to_node[modules[0].module_id]}")
    return "\n".join(lines)


def _module_internal_flowchart(report: ModuleReport) -> str:
    if not report.call_flows:
        return f'flowchart TD\n    {_node_id(report.module_id, 0)}["{_escape_label(report.module_id)}"]'
    lines = ["flowchart TD"]
    label_to_node: dict[str, str] = {}
    flow_edges = _parse_flow_edges(report.call_flows)
    if flow_edges:
        for source, target in flow_edges:
            source_id = _node_for_label(source, label_to_node)
            target_id = _node_for_label(target, label_to_node)
            lines.append(f"    {source_id} --> {target_id}")
        return "\n".join(lines)
    for index, flow in enumerate(report.call_flows):
        lines.append(f'    {_node_id(flow, index)}["{_escape_label(flow)}"]')
    return "\n".join(lines)


def _parse_flow_edges(flows: list[str]) -> list[tuple[str, str]]:
    edges: list[tuple[str, str]] = []
    for flow in flows:
        if "->" not in flow:
            continue
        parts = [part.strip(" -") for part in flow.split("->") if part.strip(" -")]
        for index in range(len(parts) - 1):
            edges.append((parts[index], parts[index + 1]))
    return edges


def _node_for_label(label: str, label_to_node: dict[str, str]) -> str:
    if label in label_to_node:
        return label_to_node[label]
    node_id = _node_id(label, len(label_to_node))
    label_to_node[label] = node_id
    return f'{node_id}["{_escape_label(label)}"]'


def _node_id(raw: str, index: int) -> str:
    cleaned = "".join(ch if ch.isalnum() else "_" for ch in raw)
    cleaned = "_".join(part for part in cleaned.split("_") if part)
    if not cleaned:
        cleaned = "node"
    if cleaned[0].isdigit():
        cleaned = f"n_{cleaned}"
    return f"{cleaned}_{index}"


def _escape_label(label: str) -> str:
    normalized = " ".join(label.split())
    return normalized.replace("\\", "\\\\").replace('"', '\\"')
