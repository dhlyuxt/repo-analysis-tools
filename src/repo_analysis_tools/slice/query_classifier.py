from __future__ import annotations

import re

from repo_analysis_tools.slice.models import QueryClassification


_LOCATE_SYMBOL_PATTERN = re.compile(
    r"^where\s+is\s+(?P<quote>['\"`])?(?P<symbol>[A-Za-z_][A-Za-z0-9_]*)(?P=quote)?\s+defined\??$",
    re.IGNORECASE,
)
_FILE_ROLE_PATTERN = re.compile(r"^what\s+is\s+the\s+role\s+of\s+(?P<subject>.+?)\??$", re.IGNORECASE)


class QueryClassifier:
    def classify(self, question: str) -> QueryClassification:
        normalized = question.strip()
        if not normalized:
            raise ValueError("question must not be empty")

        locate_match = _LOCATE_SYMBOL_PATTERN.fullmatch(normalized)
        if locate_match is not None:
            return QueryClassification(
                query_kind="locate_symbol",
                symbol_name=locate_match.group("symbol"),
            )

        role_match = _FILE_ROLE_PATTERN.fullmatch(normalized)
        if role_match is not None:
            return QueryClassification(
                query_kind="file_role",
                subject=role_match.group("subject").strip(),
            )

        lowered = normalized.lower()
        if "startup flow" in lowered or "startup" in lowered or "init flow" in lowered or "initialization flow" in lowered:
            return QueryClassification(query_kind="init_flow")

        return QueryClassification(query_kind="general_question")
