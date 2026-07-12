#!/usr/bin/env -S uv run python
from __future__ import annotations

from pathlib import Path
import unittest


CODEX_ROOT = Path(__file__).resolve().parents[3]


class LearningDispositionContractTests(unittest.TestCase):
    def test_root_doctrine_keeps_implicit_execution_checkpoint(self) -> None:
        agents = (CODEX_ROOT / "AGENTS.md").read_text(encoding="utf-8")
        for required in (
            "Learning disposition mandate",
            "Invoke `$learnings` after a decision-shaping validation transition",
            "before every Codex-made commit, PR handoff, or terminal implementation/review closeout",
            "even when the user did not explicitly name the skill",
            "`appended`, `duplicate-skip`, `no-op`, or `blocked`",
            "Never silently discard invalid legacy records",
        ):
            with self.subTest(required=required):
                self.assertIn(required, agents)

    def test_learnings_skill_owns_disposition_and_safe_skip(self) -> None:
        skill = (CODEX_ROOT / "skills/learnings/SKILL.md").read_text(
            encoding="utf-8"
        )
        for required in (
            "## Disposition Invariant",
            "learning-disposition: appended",
            "learning-disposition: duplicate-skip",
            "learning-disposition: no-op",
            "learning-disposition: blocked",
            "--invalid-policy skip",
            "run `ledger --version`",
            "`>= 0.5.2`",
            "Never combine skip with `--mode move` or",
        ):
            with self.subTest(required=required):
                self.assertIn(required, skill)

    def test_actuation_handoff_cannot_bypass_disposition(self) -> None:
        skill = (CODEX_ROOT / "skills/actuating/SKILL.md").read_text(
            encoding="utf-8"
        )
        closure = (
            CODEX_ROOT / "skills/actuating/references/closure.md"
        ).read_text(encoding="utf-8")
        self.assertIn(
            "Before handing off `ready-to-ship` or reporting terminal `complete`",
            skill,
        )
        self.assertIn("## Learning disposition after decision", closure)
        self.assertIn("decision becomes stale", skill)
        self.assertIn("decision becomes stale", closure)


if __name__ == "__main__":
    unittest.main()
