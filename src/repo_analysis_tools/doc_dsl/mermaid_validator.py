from __future__ import annotations

from dataclasses import dataclass
import json
from json import JSONDecodeError
import os
from pathlib import Path
import shutil
import subprocess


REPO_ROOT = Path(__file__).resolve().parents[3]
MERMAID_VALIDATE_SCRIPT = REPO_ROOT / "tools" / "validate_mermaid.mjs"
DEFAULT_NODE_BINARY = Path("/home/hyx/anaconda3/envs/agent/bin/node")
NODE_BINARY_ENV = "REPO_ANALYSIS_TOOLS_NODE_BINARY"
SUBPROCESS_TIMEOUT_SECONDS = 10


class MermaidSyntaxError(ValueError):
    pass


@dataclass(frozen=True)
class MermaidValidationResult:
    diagram_type: str | None


class MermaidValidator:
    def __init__(self, node_binary: str = "node") -> None:
        self.node_binary = _resolve_node_binary(node_binary)

    def validate(self, source: str, *, diagram_kind: str | None = None) -> MermaidValidationResult:
        requested_kind = diagram_kind or _infer_diagram_kind(source)
        payload = json.dumps({"source": source, "diagram_kind": requested_kind})
        completed = _run_validator_process(self.node_binary, payload)
        response = _decode_validator_response(completed.stdout)
        if completed.returncode != 0 or not response.get("ok"):
            detail = response.get("error") or completed.stderr.strip() or "unknown Mermaid validation failure"
            raise MermaidSyntaxError(f"Mermaid syntax error: {detail}")
        return MermaidValidationResult(
            diagram_type=_normalize_diagram_type(response.get("diagramType"), requested_kind)
        )


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


def _resolve_node_binary(node_binary: str) -> str:
    if node_binary != "node":
        return node_binary
    env_override = os.environ.get(NODE_BINARY_ENV)
    if env_override:
        return env_override
    path_node = shutil.which("node")
    if path_node:
        return path_node
    if DEFAULT_NODE_BINARY.exists():
        return str(DEFAULT_NODE_BINARY)
    return node_binary


def _run_validator_process(node_binary: str, payload: str) -> subprocess.CompletedProcess[str]:
    try:
        return subprocess.run(
            [node_binary, str(MERMAID_VALIDATE_SCRIPT)],
            input=payload,
            text=True,
            capture_output=True,
            check=False,
            timeout=SUBPROCESS_TIMEOUT_SECONDS,
        )
    except FileNotFoundError as exc:
        raise MermaidSyntaxError(f"Mermaid syntax error: could not start node process: {exc}") from exc
    except subprocess.TimeoutExpired as exc:
        raise MermaidSyntaxError("Mermaid syntax error: validator process timed out") from exc


def _decode_validator_response(stdout: str) -> dict[str, object]:
    try:
        payload = json.loads(stdout or "{}")
    except JSONDecodeError as exc:
        raise MermaidSyntaxError("Mermaid syntax error: invalid validator response") from exc
    if not isinstance(payload, dict):
        raise MermaidSyntaxError("Mermaid syntax error: invalid validator response")
    return payload
