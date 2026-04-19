from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
import subprocess


REPO_ROOT = Path(__file__).resolve().parents[3]
MERMAID_VALIDATE_SCRIPT = REPO_ROOT / "tools" / "validate_mermaid.mjs"
DEFAULT_NODE_BINARY = Path("/home/hyx/anaconda3/envs/agent/bin/node")


class MermaidSyntaxError(ValueError):
    pass


@dataclass(frozen=True)
class MermaidValidationResult:
    diagram_type: str | None


class MermaidValidator:
    def __init__(self, *, node_binary: str | None = None) -> None:
        if node_binary is not None:
            self.node_binary = node_binary
        elif DEFAULT_NODE_BINARY.exists():
            self.node_binary = str(DEFAULT_NODE_BINARY)
        else:
            self.node_binary = "node"

    def validate(self, source: str, *, diagram_kind: str | None = None) -> MermaidValidationResult:
        requested_kind = diagram_kind or _infer_diagram_kind(source)
        payload = json.dumps({"source": source, "diagram_kind": requested_kind})
        completed = subprocess.run(
            [self.node_binary, str(MERMAID_VALIDATE_SCRIPT)],
            input=payload,
            text=True,
            capture_output=True,
            check=False,
        )
        response = json.loads(completed.stdout or "{}")
        if completed.returncode != 0 or not response.get("ok"):
            detail = response.get("error") or completed.stderr.strip() or "unknown Mermaid validation failure"
            raise MermaidSyntaxError(f"Mermaid syntax error: {detail}")
        return MermaidValidationResult(
            diagram_type=_normalize_diagram_type(response.get("diagramType"), requested_kind)
        )


def validate_mermaid(source: str, *, diagram_kind: str | None = None) -> MermaidValidationResult:
    return MermaidValidator().validate(source, diagram_kind=diagram_kind)


def _infer_diagram_kind(source: str) -> str | None:
    for line in source.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        return stripped.split(maxsplit=1)[0]
    return None


def _normalize_diagram_type(diagram_type: object, requested_kind: str | None) -> str | None:
    if isinstance(diagram_type, str):
        if requested_kind == "flowchart" and diagram_type.startswith("flowchart"):
            return requested_kind
        return diagram_type
    return requested_kind
