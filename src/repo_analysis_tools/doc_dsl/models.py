from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class EvidenceBinding:
    file_path: str
    anchor_name: str | None = None
    line_start: int | None = None
    line_end: int | None = None


@dataclass(frozen=True)
class TextBlock:
    text: str


@dataclass(frozen=True)
class MermaidBlock:
    diagram_kind: str
    source: str
    caption: str
    placement: str
    evidence_bindings: tuple[EvidenceBinding, ...]
    title: str | None = None


@dataclass(frozen=True)
class Section:
    title: str
    blocks: tuple[TextBlock | MermaidBlock, ...]


@dataclass(frozen=True)
class Document:
    document_type: str
    title: str
    sections: tuple[Section, ...]
    metadata: dict[str, str] = field(default_factory=dict)
