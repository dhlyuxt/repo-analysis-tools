from __future__ import annotations

from dataclasses import dataclass
import re
from typing import Any


MODULE_ID_PATTERN = re.compile(r"^[A-Za-z0-9_.-]+$")


def _require(payload: dict[str, Any], field: str) -> Any:
    if field not in payload:
        raise ValueError(f"missing required field: {field}")
    return payload[field]


def _string_list(value: Any, field: str) -> list[str]:
    if not isinstance(value, list):
        raise ValueError(f"{field} must be a list")
    if not all(isinstance(item, str) for item in value):
        raise ValueError(f"{field} items must be strings")
    return list(value)


def _object(value: Any, field: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ValueError(f"{field} entries must be objects")
    return value


def _safe_module_id(value: Any) -> str:
    if not isinstance(value, str):
        raise ValueError("module_id must be a string")
    if not value or ".." in value or MODULE_ID_PATTERN.fullmatch(value) is None:
        raise ValueError(
            "module_id must match ^[A-Za-z0-9_.-]+$ and must not contain '..'"
        )
    return value


def _reject_duplicate_module_ids(
    entries: list["ModuleDescriptor"] | list["ModuleReport"], field: str
) -> None:
    seen: set[str] = set()
    for entry in entries:
        if entry.module_id in seen:
            raise ValueError(f"duplicate {field} module_id: {entry.module_id}")
        seen.add(entry.module_id)


@dataclass(frozen=True)
class CitationInput:
    file_path: str
    line_start: int
    line_end: int
    symbol_name: str | None = None

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "CitationInput":
        return cls(
            file_path=str(_require(payload, "file_path")),
            line_start=int(_require(payload, "line_start")),
            line_end=int(_require(payload, "line_end")),
            symbol_name=(
                None if payload.get("symbol_name") is None else str(payload["symbol_name"])
            ),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "file_path": self.file_path,
            "line_start": self.line_start,
            "line_end": self.line_end,
            "symbol_name": self.symbol_name,
        }


@dataclass(frozen=True)
class ModuleDescriptor:
    module_id: str
    module_name: str
    responsibility: str
    paths: list[str]
    dependencies: list[str]

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "ModuleDescriptor":
        return cls(
            module_id=_safe_module_id(_require(payload, "module_id")),
            module_name=str(_require(payload, "module_name")),
            responsibility=str(_require(payload, "responsibility")),
            paths=_string_list(_require(payload, "paths"), "paths"),
            dependencies=_string_list(_require(payload, "dependencies"), "dependencies"),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "module_id": self.module_id,
            "module_name": self.module_name,
            "responsibility": self.responsibility,
            "paths": list(self.paths),
            "dependencies": list(self.dependencies),
        }


@dataclass(frozen=True)
class ModuleReport:
    module_id: str
    summary: list[str]
    entry_points: list[str]
    key_symbols: list[str]
    call_flows: list[str]
    risks: list[str]
    unknowns: list[str]
    citations: list[CitationInput]

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "ModuleReport":
        citations = _require(payload, "citations")
        if not isinstance(citations, list):
            raise ValueError("citations must be a list")
        return cls(
            module_id=_safe_module_id(_require(payload, "module_id")),
            summary=_string_list(_require(payload, "summary"), "summary"),
            entry_points=_string_list(_require(payload, "entry_points"), "entry_points"),
            key_symbols=_string_list(_require(payload, "key_symbols"), "key_symbols"),
            call_flows=_string_list(_require(payload, "call_flows"), "call_flows"),
            risks=_string_list(_require(payload, "risks"), "risks"),
            unknowns=_string_list(_require(payload, "unknowns"), "unknowns"),
            citations=[
                CitationInput.from_dict(_object(item, "citations")) for item in citations
            ],
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "module_id": self.module_id,
            "summary": list(self.summary),
            "entry_points": list(self.entry_points),
            "key_symbols": list(self.key_symbols),
            "call_flows": list(self.call_flows),
            "risks": list(self.risks),
            "unknowns": list(self.unknowns),
            "citations": [citation.to_dict() for citation in self.citations],
        }


@dataclass(frozen=True)
class GlobalFindings:
    architecture_summary: list[str]
    cross_module_flows: list[str]
    constraints: list[str]
    unknowns: list[str]
    citations: list[CitationInput]

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "GlobalFindings":
        citations = _require(payload, "citations")
        if not isinstance(citations, list):
            raise ValueError("citations must be a list")
        return cls(
            architecture_summary=_string_list(
                _require(payload, "architecture_summary"), "architecture_summary"
            ),
            cross_module_flows=_string_list(
                _require(payload, "cross_module_flows"), "cross_module_flows"
            ),
            constraints=_string_list(payload.get("constraints", []), "constraints"),
            unknowns=_string_list(_require(payload, "unknowns"), "unknowns"),
            citations=[
                CitationInput.from_dict(_object(item, "citations")) for item in citations
            ],
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "architecture_summary": list(self.architecture_summary),
            "cross_module_flows": list(self.cross_module_flows),
            "constraints": list(self.constraints),
            "unknowns": list(self.unknowns),
            "citations": [citation.to_dict() for citation in self.citations],
        }


@dataclass(frozen=True)
class RepositoryFindingsPackage:
    repo_name: str
    target_repo: str
    output_root: str
    module_map: list[ModuleDescriptor]
    module_reports: list[ModuleReport]
    global_findings: GlobalFindings

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "RepositoryFindingsPackage":
        for field in (
            "repo_name",
            "target_repo",
            "output_root",
            "module_map",
            "module_reports",
            "global_findings",
        ):
            _require(payload, field)
        module_map = payload["module_map"]
        module_reports = payload["module_reports"]
        if not isinstance(module_map, list):
            raise ValueError("module_map must be a list")
        if not isinstance(module_reports, list):
            raise ValueError("module_reports must be a list")
        if not isinstance(payload["global_findings"], dict):
            raise ValueError("global_findings must be an object")
        parsed_module_map = [
            ModuleDescriptor.from_dict(_object(item, "module_map")) for item in module_map
        ]
        parsed_module_reports = [
            ModuleReport.from_dict(_object(item, "module_reports"))
            for item in module_reports
        ]
        _reject_duplicate_module_ids(parsed_module_map, "module_map")
        _reject_duplicate_module_ids(parsed_module_reports, "module_reports")
        return cls(
            repo_name=str(payload["repo_name"]),
            target_repo=str(payload["target_repo"]),
            output_root=str(payload["output_root"]),
            module_map=parsed_module_map,
            module_reports=parsed_module_reports,
            global_findings=GlobalFindings.from_dict(payload["global_findings"]),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "repo_name": self.repo_name,
            "target_repo": self.target_repo,
            "output_root": self.output_root,
            "module_map": [module.to_dict() for module in self.module_map],
            "module_reports": [report.to_dict() for report in self.module_reports],
            "global_findings": self.global_findings.to_dict(),
        }


@dataclass(frozen=True)
class GeneratedDocument:
    document_type: str
    relative_path: str
    title: str

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "GeneratedDocument":
        return cls(
            document_type=str(_require(payload, "document_type")),
            relative_path=str(_require(payload, "relative_path")),
            title=str(_require(payload, "title")),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "document_type": self.document_type,
            "relative_path": self.relative_path,
            "title": self.title,
        }


@dataclass(frozen=True)
class RepositoryDesignManifest:
    output_root: str
    validation_status: str
    documents: list[GeneratedDocument]
    unknown_count: int

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "RepositoryDesignManifest":
        documents = _require(payload, "documents")
        if not isinstance(documents, list):
            raise ValueError("documents must be a list")
        return cls(
            output_root=str(_require(payload, "output_root")),
            validation_status=str(_require(payload, "validation_status")),
            documents=[GeneratedDocument.from_dict(item) for item in documents],
            unknown_count=int(_require(payload, "unknown_count")),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "output_root": self.output_root,
            "validation_status": self.validation_status,
            "documents": [document.to_dict() for document in self.documents],
            "unknown_count": self.unknown_count,
        }
