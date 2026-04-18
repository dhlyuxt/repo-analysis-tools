from enum import StrEnum
from typing import Any


SCHEMA_VERSION = "1"


class ErrorCode(StrEnum):
    INVALID_INPUT = "invalid_input"
    NOT_FOUND = "not_found"
    CONFLICT = "conflict"
    RUNTIME_STATE = "runtime_state"
    INTERNAL = "internal"


def _message(level: str, text: str) -> dict[str, str]:
    return {"level": level, "text": text}


def ok_response(
    *,
    data: dict[str, Any],
    messages: list[str] | None = None,
    recommended_next_tools: list[str] | None = None,
) -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "status": "ok",
        "data": data,
        "messages": [_message("info", text) for text in (messages or [])],
        "recommended_next_tools": recommended_next_tools or [],
    }


def error_response(
    code: ErrorCode,
    message: str,
    *,
    details: dict[str, Any] | None = None,
    recommended_next_tools: list[str] | None = None,
) -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "status": "error",
        "data": {
            "error": {
                "code": code.value,
                "message": message,
                "details": details or {},
            }
        },
        "messages": [_message("error", message)],
        "recommended_next_tools": recommended_next_tools or [],
    }
