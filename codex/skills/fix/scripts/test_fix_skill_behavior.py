#!/usr/bin/env python3
"""Behavioral contract tests for the fix skill's review-saturation loop."""

from __future__ import annotations

import unittest
from dataclasses import dataclass
from pathlib import Path

from lint_fix_skill_contract import lint_skill


@dataclass
class SaturationState:
    clean_streak: int = 0
    done: bool = False
    blocked: bool = False

    def note_edit(self) -> None:
        self.clean_streak = 0

    def note_review_clean(self) -> None:
        if self.blocked:
            raise AssertionError("blocked state cannot receive more reviews")
        self.clean_streak += 1
        if self.clean_streak >= 2:
            self.done = True

    def note_review_findings(
        self,
        *,
        recurring_seeded: bool,
        materially_changed: bool,
        validation_improved: bool,
    ) -> None:
        if self.done:
            raise AssertionError("done state cannot receive more findings")
        self.clean_streak = 0
        if recurring_seeded and not materially_changed and not validation_improved:
            self.blocked = True


class FixSkillBehaviorTests(unittest.TestCase):
    def test_contract_lints(self) -> None:
        skill_path = Path(__file__).resolve().parents[1] / "SKILL.md"
        self.assertEqual(lint_skill(skill_path), [])

    def test_first_clean_is_only_candidate_clean(self) -> None:
        state = SaturationState()
        state.note_review_clean()
        self.assertFalse(state.done)
        self.assertEqual(state.clean_streak, 1)

    def test_two_consecutive_cleans_close_the_run(self) -> None:
        state = SaturationState()
        state.note_review_clean()
        state.note_review_clean()
        self.assertTrue(state.done)
        self.assertEqual(state.clean_streak, 2)

    def test_edit_between_clean_reviews_resets_clean_streak(self) -> None:
        state = SaturationState()
        state.note_review_clean()
        state.note_edit()
        state.note_review_clean()
        self.assertFalse(state.done)
        self.assertEqual(state.clean_streak, 1)

    def test_reopening_after_candidate_clean_resets_streak(self) -> None:
        state = SaturationState()
        state.note_review_clean()
        state.note_review_findings(
            recurring_seeded=False,
            materially_changed=True,
            validation_improved=False,
        )
        self.assertFalse(state.done)
        self.assertFalse(state.blocked)
        self.assertEqual(state.clean_streak, 0)

    def test_recurring_seeded_finding_without_material_progress_blocks(self) -> None:
        state = SaturationState()
        state.note_review_findings(
            recurring_seeded=True,
            materially_changed=False,
            validation_improved=False,
        )
        self.assertTrue(state.blocked)
        self.assertFalse(state.done)

    def test_recurring_seeded_finding_with_material_progress_keeps_loop_alive(self) -> None:
        state = SaturationState()
        state.note_review_findings(
            recurring_seeded=True,
            materially_changed=True,
            validation_improved=False,
        )
        self.assertFalse(state.blocked)
        self.assertEqual(state.clean_streak, 0)


if __name__ == "__main__":
    unittest.main()
