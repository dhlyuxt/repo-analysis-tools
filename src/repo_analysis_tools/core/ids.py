from enum import StrEnum
import hashlib
import uuid


class StableIdKind(StrEnum):
    SCAN = "scan"
    SLICE = "slice"
    IMPACT = "impact"
    EVIDENCE_PACK = "evidence_pack"
    REPORT = "report"
    EXPORT = "export"


def make_stable_id(kind: StableIdKind) -> str:
    return f"{kind.value}_{uuid.uuid4().hex[:12]}"


def make_anchor_id(file_path: str, kind: str, name: str, start_line: int, end_line: int) -> str:
    digest = hashlib.sha1(
        f"{file_path}|{kind}|{name}|{start_line}|{end_line}".encode("utf-8")
    ).hexdigest()[:12]
    return f"anchor_{digest}"


def make_scope_node_id(label: str) -> str:
    if not label:
        return "scope_root"
    encoded = "".join(
        character
        if character.isascii() and character.isalnum()
        else f"_x{ord(character):02x}_"
        for character in label
    )
    return f"scope_{encoded}"
