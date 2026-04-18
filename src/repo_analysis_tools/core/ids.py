from enum import StrEnum
import uuid


class StableIdKind(StrEnum):
    SCAN = "scan"
    SLICE = "slice"
    EVIDENCE_PACK = "evidence_pack"
    REPORT = "report"
    EXPORT = "export"


def make_stable_id(kind: StableIdKind) -> str:
    return f"{kind.value}_{uuid.uuid4().hex[:12]}"
