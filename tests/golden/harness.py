import json
from pathlib import Path
from typing import Any
from unittest import TestCase


FIXTURES_DIR = Path(__file__).resolve().parent / "fixtures"


def fixture_path(name: str) -> Path:
    return FIXTURES_DIR / name


def load_fixture(name: str) -> Any:
    with fixture_path(name).open(encoding="utf-8") as fixture_file:
        return json.load(fixture_file)


def assert_matches_fixture(test_case: TestCase, fixture_name: str, actual: Any) -> None:
    expected = load_fixture(fixture_name)
    test_case.assertEqual(actual, expected)
