#!/usr/bin/env -S uv run python
from __future__ import annotations

from pathlib import Path
import unittest


CODEX_ROOT = Path(__file__).resolve().parents[3]


class LearningDispositionContractTests(unittest.TestCase):
    def test_root_doctrine_moves_lifecycle_checkpoint_to_ledger(self) -> None:
        agents = (CODEX_ROOT / "AGENTS.md").read_text(encoding="utf-8")
        for required in (
            "Source-memory checkpoint mandate",
            "closure -> handoff/report -> source-memory evaluation",
            "must not delay code closure, a Codex-made commit, or a PR handoff",
            "evaluate Learnings, Synesthesia, and Negative Ledger",
            "checkpoint_context=source-memory-checkpoint/v1",
            "ledger validate source-memory-checkpoint",
            "never silently discard invalid legacy records",
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
            "`>= 0.10.5`",
            "ledger show --source learnings --id lrn-...",
            "source-owned alias for `export --format full`",
            "Never combine skip with `--mode move` or",
            "## Ledger checkpoint participant",
            "Do not rerun\n`$ledger ensure`",
            "ledger export --source learnings --id lrn-... --format memory-note",
            "do not invoke Synesthesia",
        ):
            with self.subTest(required=required):
                self.assertIn(required, skill)
        self.assertNotIn("evaluate `$synesthesia` in the same lifecycle point", skill)

    def test_actuation_handoff_cannot_bypass_disposition(self) -> None:
        skill = (CODEX_ROOT / "skills/actuating/SKILL.md").read_text(
            encoding="utf-8"
        )
        closure = (
            CODEX_ROOT / "skills/actuating/references/closure.md"
        ).read_text(encoding="utf-8")
        self.assertIn("Complete the handoff or report", skill)
        self.assertIn("Complete delivery handoff or reporting before", closure)
        self.assertIn("admission cannot gate", closure)


if __name__ == "__main__":
    unittest.main()
