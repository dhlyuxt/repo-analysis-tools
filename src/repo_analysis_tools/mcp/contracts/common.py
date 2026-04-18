from dataclasses import dataclass

from repo_analysis_tools.core.errors import ErrorCode
from repo_analysis_tools.core.ids import StableIdKind


@dataclass(frozen=True)
class ToolContract:
    name: str
    domain: str
    input_schema: dict[str, str]
    output_schema: dict[str, str]
    stable_ids: tuple[StableIdKind, ...]
    failure_modes: tuple[ErrorCode, ...]
    recommended_next_tools: tuple[str, ...]
