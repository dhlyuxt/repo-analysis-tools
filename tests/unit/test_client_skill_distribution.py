from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SKILL_NAMES = [
    "repo-understand",
    "change-impact",
    "analysis-writing",
    "analysis-maintenance",
]


def normalize_skill_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


class ClientSkillDistributionTest(unittest.TestCase):
    def test_claude_skills_mirror_agents_skills(self) -> None:
        for skill_name in SKILL_NAMES:
            agents_path = ROOT / ".agents" / "skills" / skill_name / "SKILL.md"
            claude_path = ROOT / ".claude" / "skills" / skill_name / "SKILL.md"

            self.assertTrue(agents_path.is_file(), str(agents_path))
            self.assertTrue(claude_path.is_file(), str(claude_path))
            self.assertEqual(normalize_skill_text(agents_path), normalize_skill_text(claude_path))
